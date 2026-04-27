from flask import Blueprint, jsonify, request

from app.services.pipeline import run_analysis_pipeline
from app.services.ai_service import generate_ai_result, generate_rag_ai_result
from app.services.rag_service import match_rag_resources
import traceback

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "ILLO backend is running"
    }), 200


@api_bp.route("/analyze", methods=["POST"])
def analyze():
    print("[DEBUG] request.json =", request.get_json())

    try:
        payload = request.get_json()

        if not payload:
            return jsonify({
                "status": "error",
                "message": "JSON body가 없습니다."
            }), 400

        result = run_analysis_pipeline(payload)

        rag_result = match_rag_resources({
            "viewer_role": payload.get("viewer_role", "employee"),
            "risk_factors": result.get("risk_factors", []),
            "related_factors": result.get("related_factors", []),
            "user_selected_contexts": payload.get("user_selected_contexts", [])
        })

        result["rag"] = rag_result

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
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"서버 내부 오류: {str(e)}"
        }), 500
    
@api_bp.route("/ai/rag", methods=["POST"])
def ai_rag():
    try:
        payload = request.get_json()

        if not payload:
            return jsonify({
                "status": "error",
                "message": "JSON body가 없습니다."
            }), 400

        rag_ai_result = generate_rag_ai_result(payload)

        return jsonify({
            "status": "success",
            "data": rag_ai_result
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
        }), 500