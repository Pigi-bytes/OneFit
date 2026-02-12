import hashlib
import json
import logging
import time
from datetime import datetime

import requests
from sqlalchemy import func

from app import Config, db
from app.models import RequestLog

DAILY_LIMIT = Config.DAILY_LIMIT
MONTHLY_LIMIT = Config.MONTHLY_LIMIT

logger = logging.getLogger("OneFit.ApiCache")


class SmartApiClient:
    def __init__(self):
        pass

    def getUsageStats(self):
        """Récupère les statistiques d'utilisation de l'api"""
        today = datetime.now().date()
        firstDayOfTheMonth = today.replace(day=1)

        logger.debug(f"Calcul des stats pour {today} et {firstDayOfTheMonth}")
        thisDay = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) == today).count()
        thisMonth = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) >= firstDayOfTheMonth).count()
        logger.debug(f"Stats: Jour {thisDay}, Mois {thisMonth}")
        return thisDay, thisMonth

    def get(self, url, params={}, headers={}, **kwargs):
        logger.info(f"Tentative d'accès à l'URL : {url}")
        # Construction de l'URL
        try:
            req = requests.PreparedRequest()
            req.prepare_url(url, params)
            full_url = req.url
            logger.debug(f"URL préparée: {full_url}")
            cache_key = hashlib.md5(f"{url}{json.dumps(params, sort_keys=True)}".encode()).hexdigest()
            logger.debug(f"Clé générée: {cache_key}")
        except Exception as e:
            logger.error(f"Erreur lors de la construction de l'URL: {e}")
            return None

        # Vérification dans la base de donnée
        cached_entry = (
            db.session.query(RequestLog)
            .filter(RequestLog.cache_key == cache_key, RequestLog.status_code == 200)
            .order_by(RequestLog.timestamp.desc())
            .first()
        )

        if cached_entry and cached_entry.response_body:
            logger.info(f"Données récupérées depuis la BDD pour {full_url}")
            cached_entry.cache_hits += 1
            db.session.commit()
            logger.info(f"cache_hits incrémenté à {cached_entry.cache_hits}")
            try:
                data = json.loads(cached_entry.response_body)
                logger.debug(f"Réponse: {data}")
                if isinstance(data, dict) and "data" in data:
                    logger.info("Retourne data['data']")
                    return data["data"]
                return data
            except json.JSONDecodeError:
                logger.warning("Impossible de décoder le JSON du cache. Ignoré.")
                pass

        today, month = self.getUsageStats()
        if today >= DAILY_LIMIT or month >= MONTHLY_LIMIT:
            logger.critical("QUOTA EXHAUSTED | Jour: %s/%s | Mois: %s/%s", today, DAILY_LIMIT, month, MONTHLY_LIMIT)
            return None

        try:
            logger.info(f"Envoi requête vers: {full_url}")
            start = time.perf_counter()
            response = requests.get(url, params=params, headers=headers, **kwargs)
            duration = time.perf_counter() - start
            logger.debug(f"Status: {response.status_code} | In {duration} Body: {response.text[:200]}")

            log_entry = RequestLog(
                cache_key=cache_key,  # type: ignore
                status_code=response.status_code,  # type: ignore
                response_body=response.text,  # type: ignore
            )
            db.session.add(log_entry)
            db.session.commit()
            logger.info("Requête enregistrée dans RequestLog")

            response.raise_for_status()

            data = response.json()
            logger.debug(f"Réponse JSON: {data}")
            if isinstance(data, dict) and "data" in data:
                logger.info("Retourne data['data']")
                return data["data"]
            return data

        except requests.RequestException as e:
            logger.error(f"RequestException : {str(e)}")
            return None
        except Exception as e:
            logger.critical(f"{type(e).__name__} | Msg: {str(e)}", exc_info=True)
            return None
