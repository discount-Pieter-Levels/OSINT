from flask import Blueprint, jsonify, render_template, request

from profile_similarity.matcher.ranking import rank_profiles

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/compare", methods=["POST"])
def compare_profiles():
    payload = request.get_json(silent=True) or {}
    profile1 = payload.get("profile1", {})
    profile2 = payload.get("profile2", {})
    result = rank_profiles(profile1, profile2)
    return jsonify(result)
