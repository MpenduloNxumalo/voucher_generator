from connexion import FlaskApp
from pathlib import Path

app = FlaskApp(__name__, specification_dir=".")
app.add_api("api/vouchers_api.yaml")
BASE_DIR = Path(__file__).resolve().parent
DEBUG = False

if __name__ == "__main__":
    host = "0.0.0.0" if not DEBUG else "127.0.0.1"
    app.run(host=host, port=5000)
