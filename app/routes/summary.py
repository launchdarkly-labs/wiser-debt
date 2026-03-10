from flask import Blueprint, jsonify, current_app, request
from app.agents.coordinator import CoordinatorAgent
from app.ldclient import build_context

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary", methods=["POST"])
def post_summary():
    data = request.get_json(silent=True) or {}
    user_key = data.get("user_key", "user-123")

    ld_client = current_app.config["LD_CLIENT"]
    context = build_context(user_key=user_key)

    coordinator = CoordinatorAgent(ld_client, context)
    results = coordinator.summarize()

    return jsonify({"debts": results})
