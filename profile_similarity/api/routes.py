from flask import Blueprint, jsonify, render_template, request

from profile_similarity.matcher.ranking import rank_profiles
from profile_similarity.preprocessor import normalize_profile, parse_plain_text_profile

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/compare", methods=["POST"])
def compare_profiles():
    payload = request.get_json(silent=True) or {}
    profile1 = payload.get("profile1", {})
    profile2 = payload.get("profile2", {})
    # If the client sent raw text (because JSON.parse failed), try parsing it
    if isinstance(profile1, str):
        try:
            profile1 = parse_plain_text_profile(profile1)
        except Exception:
            profile1 = {}
    if isinstance(profile2, str):
        try:
            profile2 = parse_plain_text_profile(profile2)
        except Exception:
            profile2 = {}

    # Normalize noisy inputs into the canonical shape expected by the matcher
    profile1 = normalize_profile(profile1)
    profile2 = normalize_profile(profile2)
    result = rank_profiles(profile1, profile2)
    return jsonify(result)
