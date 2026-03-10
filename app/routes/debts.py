from flask import Blueprint, jsonify, current_app, request
from app.agents.coordinator import CoordinatorAgent
from app.ldclient import build_context

debts_bp = Blueprint("debts", __name__)


@debts_bp.route("/debts", methods=["GET"])
def get_debts():
    user_key = request.args.get("user_key", "user-123")

    ld_client = current_app.config["LD_CLIENT"]
    context = build_context(user_key=user_key)

    coordinator = CoordinatorAgent(ld_client, context)
    debts = coordinator.list_debts()

    return jsonify({"debts": debts})
