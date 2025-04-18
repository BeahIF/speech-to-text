# routes/question_routes.py
from flask import Blueprint, request, jsonify
from models.practice import Practice
from models.question import Question
from db import db
import datetime

question_bp = Blueprint('question', __name__)

@question_bp.route('/question', methods=['POST'])
def create_question():
    data = request.get_json()
    description = data.get('description')
    topic = data.get('topic')
    language = data.get('language')

    if not description or not topic:
        return jsonify({"error": "Descrição e tópico são obrigatórias"}), 400

    question = Question(description=description, topic=topic)
    db.session.add(question)
    db.session.flush() 
    practice = Practice(        questionId=question.id,
        solution="",  # vai ser preenchido depois via áudio ou texto
        data=datetime.date.today(),
        feedback=None,
        status="in_progress",
        language=language
    )
    db.session.add(practice)

    db.session.commit()


    return jsonify({
        "question_id": str(question.id),
        "practice_id": str(practice.id)
    }), 201
