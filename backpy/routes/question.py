from flask import Blueprint, request, jsonify
from models.practice import Practice
from models.question import Question
from db import db
import datetime


question_bp = Blueprint("question", __name__)


@question_bp.route("/question", methods=["POST"])
def create_question():
    try:
        data = request.get_json() or {}

        description = data.get("description")
        topic = data.get("topic")
        language = data.get("language", "python")

        if not description or not topic:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Descrição e tópico são obrigatórios."
                }
            }), 400

        question = Question(
            description=description,
            topic=topic
        )

        db.session.add(question)
        db.session.flush()

        practice = Practice(
            questionId=question.id,
            solution="",
            data=datetime.date.today(),
            feedback=None,
            status="in_progress",
            language=language
        )

        db.session.add(practice)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "question_id": str(question.id),
                "practice_id": str(practice.id)
            },
            "error": None
        }), 201

    except Exception as e:
        db.session.rollback()
        print("[question] erro ao criar questão:", str(e))

        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "CREATE_QUESTION_FAILED",
                "message": str(e)
            }
        }), 500