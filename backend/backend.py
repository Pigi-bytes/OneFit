from app import app
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info("Démarrage du serveur Flask")
    app.run(debug=True)
