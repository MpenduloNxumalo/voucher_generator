from connexion import FlaskApp

app = FlaskApp(__name__, specification_dir=".")
app.add_api("api/vouchers_api.yaml")

if __name__ == "__main__":
    app.run(port=5000)