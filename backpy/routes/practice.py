from flask import Blueprint, request, jsonify
from datetime import date
import uuid

from db import db
from models.practice import Practice


practice_bp = Blueprint("practice", __name__)


@practice_bp.route("/practice", methods=["POST"])
def create_practice():
    try:
        data = request.get_json() or {}

        question_id = data.get("question_id")
        language = data.get("language")
        initial_solution = data.get("solution") or ""

        question_uuid = None

        if question_id:
            try:
                question_uuid = uuid.UUID(question_id)
            except ValueError:
                return jsonify({
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_QUESTION_ID",
                        "message": "question_id inválido. Um UUID era esperado."
                    }
                }), 400

        practice = Practice(
            questionId=question_uuid,
            solution=initial_solution,
            data=date.today(),
            feedback=None,
            language=language,
            status="active"
        )

        db.session.add(practice)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "practice_id": practice.id
            },
            "error": None
        }), 201

    except Exception as e:
        db.session.rollback()
        print("[practice] erro ao criar prática:", str(e))

        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "CREATE_PRACTICE_FAILED",
                "message": "Não foi possível criar a prática."
            }
        }), 500