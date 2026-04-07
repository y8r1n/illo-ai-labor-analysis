from flask import Blueprint, jsonify, request

from app.services.pipeline import run_analysis_pipeline
from app.services.ai_service import generate_ai_result

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "ILLO backend is running"
    }), 200


@api_bp.route("/analyze", methods=["POST"])
def analyze():
    try:
        payload = request.get_json()

        if not payload:
            return jsonify({
                "status": "error",
                "message": "JSON body가 없습니다."
            }), 400

        result = run_analysis_pipeline(payload)

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"서버 내부 오류: {str(e)}"
        }), 500


# 🔥 여기부터 따로 빼야 함
@api_bp.route("/ai/interpret", methods=["POST"])
def ai_interpret():
    try:
        payload = request.get_json()

        if not payload:
            return jsonify({
                "status": "error",
                "message": "JSON body가 없습니다."
            }), 400

        ai_result = generate_ai_result(payload)

        return jsonify({
            "status": "success",
            "data": ai_result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "AI 분석 실패",
            "detail": str(e)
        }), 500