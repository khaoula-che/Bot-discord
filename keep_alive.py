import os
import time
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

PORT = int(os.getenv('PORT', 5000))

@app.route('/')
def home():
    return "Bot is running!"

def run():
    while True:
        try:
            app.run(host='0.0.0.0', port=PORT)
        except Exception as e:
            logger.error(f"Une erreur s'est produite : {e}")
            logger.info("Tentative de redémarrage dans 10 secondes...")
            time.sleep(10)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    keep_alive()
