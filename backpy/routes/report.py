# routes/report.py
from flask import Blueprint, send_file, jsonify, current_app, request
from io import BytesIO
import os

from db import db
from models.practice import Practice
from models.transcription import Transcription
from services.report import generate_practice_pdf

report_bp = Blueprint('report', __name__, url_prefix='/practices')

@report_bp.route('/<practice_id>/export', methods=['GET'])
def export_practice_pdf(practice_id):
    try:
        practice = Practice.query.get(practice_id)
        if not practice:
            return jsonify({"error": "Practice not found"}), 404

        # tenta buscar a transcrição/feedback mais recente para essa prática
        transcription = Transcription.query.filter_by(practice_id=practice_id).order_by(Transcription.id.desc()).first()
        transcription_text = transcription.transcription if transcription else ''
        feedback_text = transcription.feedback if transcription else ''
        # monta evaluation se salva no practice ou transcription (ajusta conforme teu model)
        evaluation = {
            "text_scores": getattr(transcription, 'text_scores', {}) or {},
            "code_info": getattr(transcription, 'code_info', {}) or {},
            "code_score": getattr(transcription, 'code_score', None),
            "final_score": getattr(transcription, 'final_score', None),
            "feedback": [feedback_text] if feedback_text else []
        }

        question_text = practice.question.description if getattr(practice, 'question', None) else ''
        code_text = practice.solution if getattr(practice, 'solution', None) else ''

        buffer = generate_practice_pdf(practice_id, question_text, transcription_text, code_text, evaluation, language=practice.language)

        # envia como attachment
        filename = f"practice_{practice_id}_report.pdf"
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)
    except Exception as e:
        current_app.logger.exception("Erro exportando PDF: %s", e)
        return jsonify({"error": str(e)}), 500
