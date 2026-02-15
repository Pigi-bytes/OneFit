import hashlib
import json
import logging
import time
from datetime import datetime

import requests
from sqlalchemy import func

from app import Config, db
from app.models import RequestLog
from app.utils.logger import QueryTimer

DAILY_LIMIT = Config.DAILY_LIMIT
MONTHLY_LIMIT = Config.MONTHLY_LIMIT

api_logger = logging.getLogger("OneFit.ApiCache")
perf_logger = logging.getLogger("OneFit.Performance")
db_logger = logging.getLogger("OneFit.Database")


class SmartApiClient:
    def __init__(self):
        pass

    def getUsageStats(self):
        """Récupère les statistiques d'utilisation de l'api"""
        today = datetime.now().date()
        firstDayOfTheMonth = today.replace(day=1)

        api_logger.debug(f"Calcul des stats pour {today} et {firstDayOfTheMonth}")
        thisDay = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) == today).count()
        thisMonth = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) >= firstDayOfTheMonth).count()
        api_logger.info(f"Stats: Jour {thisDay}, Mois {thisMonth}")
        return thisDay, thisMonth

    def get(self, url, params={}, headers={}, **kwargs):
        api_logger.info(f"Tentative d'accès à l'URL : {url}")
        # Construction de l'URL
        try:
            req = requests.PreparedRequest()
            req.prepare_url(url, params)
            full_url = req.url
            api_logger.debug(f"URL préparée: {full_url}")
            cache_key = hashlib.md5(f"{url}{json.dumps(params, sort_keys=True)}".encode()).hexdigest()
            api_logger.debug(f"Clé générée: {cache_key}")
        except Exception as e:
            api_logger.error(f"Erreur lors de la construction de l'URL: {e}")
            return None

        # Vérification dans la base de donnée
        with QueryTimer("check si cache est présent"):
            cached_entry = (
                db.session.query(RequestLog)
                .filter(RequestLog.cache_key == cache_key, RequestLog.status_code == 200)
                .order_by(RequestLog.timestamp.desc())
                .first()
            )

        if cached_entry and cached_entry.response_body:
            db_logger.info(f"Données récupérées depuis la BDD pour {cache_key}")
            cached_entry.cache_hits += 1
            db.session.commit()
            api_logger.info(f"cache_hits incrémenté à {cached_entry.cache_hits}")
            try:
                data = json.loads(cached_entry.response_body)
                api_logger.debug(f"Réponse: {data}")
                if isinstance(data, dict) and "data" in data:
                    api_logger.info("Retourne data['data']")
                    return data["data"]
                return data
            except json.JSONDecodeError:
                api_logger.warning("Impossible de décoder le JSON du cache. Ignoré.")
                pass

        today, month = self.getUsageStats()
        if today >= DAILY_LIMIT or month >= MONTHLY_LIMIT:
            api_logger.critical(f"Quota atteint | Jour: {today}/{DAILY_LIMIT} | Mois: {month}/{MONTHLY_LIMIT}")
            return None

        try:
            api_logger.info(f"Envoi requête vers: {full_url}")
            start = time.perf_counter()
            response = requests.get(url, params=params, headers=headers, **kwargs)
            duration = time.perf_counter() - start
            api_logger.info(f"Status: {response.status_code} | {duration:.3f}s | URL: {full_url}")

            if duration > 2.0:
                perf_logger.warning(f"Apelle lent : {full_url} | {duration:.3f}s")

            log_entry = RequestLog(
                cache_key=cache_key,  # type: ignore
                status_code=response.status_code,  # type: ignore
                response_body=response.text,  # type: ignore
            )
            db.session.add(log_entry)
            db.session.commit()
            api_logger.info("Requête enregistrée dans RequestLog")

            response.raise_for_status()

            data = response.json()
            api_logger.debug(f"Réponse JSON: {data}")
            if isinstance(data, dict) and "data" in data:
                api_logger.info("Retourne data['data']")
                return data["data"]
            return data

        except requests.RequestException as e:
            api_logger.error(f"RequestException : {str(e)}")
            return None
        except Exception as e:
            api_logger.critical(f"{type(e).__name__} | Msg: {str(e)}", exc_info=True)
            return None
