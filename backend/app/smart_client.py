import json
from datetime import datetime

import requests
from sqlalchemy import func

from app import db
from app.models import RequestLog

class SmartApiClient:
    def __init__(self):
        pass

    def getUsageStats(self):
        """Récupère les statistiques d'utilisation de l'api"""
        today = datetime.now().date()
        firstDayOfTheMonth = today.replace(day=1)

        # Compte les appels réels pour aujourd'hui et ce mois
        thisDay = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) == today).count()
        thisMonth = db.session.query(RequestLog).filter(func.date(RequestLog.timestamp) >= firstDayOfTheMonth).count()

        return thisDay, thisMonth

    def get(self, url, params={}, headers={}, **kwargs):
        # Construction de l'URL
        try:
            req = requests.PreparedRequest()
            req.prepare_url(url, params)
            full_url = req.url
        except Exception:
            return None

        # Vérification dans la base de donnée
        # On cherche une requête réussie (200) avec la même URL, la plus récente
        cached_entry = (
            db.session.query(RequestLog)
            .filter(RequestLog.url == full_url, RequestLog.status_code == 200)
            .order_by(RequestLog.timestamp.desc())
            .first()
        )

        # Si une entrée existe et contient une reponse
        if cached_entry and cached_entry.response_body:
            try:
                # Tentative de décodage JSON
                data = json.loads(cached_entry.response_body)

                # Adaptation au format de retour du code original :
                # Si la réponse est loggée telle quelle et contient "data", on retourne "data".
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                return data
            except json.JSONDecodeError:
                pass

        try:
            response = requests.get(url, params=params, headers=headers, **kwargs)

            # Enregistrement dans RequestLog
            log_entry = RequestLog(
                url=full_url,  # type: ignore
                status_code=response.status_code,  # type: ignore
                response_body=response.text,  # type: ignore
            )
            db.session.add(log_entry)
            db.session.commit()

            response.raise_for_status()

            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

        except requests.RequestException:
            return None
        except Exception:
            return None
