from flask import Blueprint, request, jsonify
from services.evaluator import evaluate_transcription_and_code


evaluate_bp = Blueprint("evaluate", __name__, url_prefix="/evaluate")


@evaluate_bp.route("/", methods=["POST"])
def evaluate():
    try:
        data = request.get_json() or {}

        question = data.get("question", "")
        code = data.get("code", "")
        transcription = data.get("transcription", "")
        language = data.get("language", "python")

        if not code and not transcription:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_INPUT",
                    "message": "É necessário enviar pelo menos código ou transcrição para avaliação."
                }
            }), 400

        result = evaluate_transcription_and_code(
            question=question,
            code=code,
            transcription=transcription,
            language=language
        )

        return jsonify({
            "success": result.get("success", False),
            "data": {
                "feedback": result.get("feedback")
            },
            "error": result.get("error")
        }), 200

    except Exception as e:
        print("[evaluate] erro:", str(e))

        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "EVALUATE_FAILED",
                "message": "Erro ao avaliar resposta."
            }
        }), 500