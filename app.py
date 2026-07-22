from os import getenv

from falae import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(getenv("APP_PORT", 5000))
    )