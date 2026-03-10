from flask import Flask
from dotenv import load_dotenv
from app.ldclient import init_ld_client


def create_app():
    load_dotenv()

    app = Flask(__name__)

    ld_client = init_ld_client()
    app.config["LD_CLIENT"] = ld_client

    from app.routes.summary import summary_bp
    from app.routes.debts import debts_bp

    app.register_blueprint(summary_bp)
    app.register_blueprint(debts_bp)

    return app
