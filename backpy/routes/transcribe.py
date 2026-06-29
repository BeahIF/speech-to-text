from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, current_app
from db import db
from models.practice import Practice
from models.transcription import Transcription
from werkzeug.utils import secure_filename
from services.evaluator import evaluate_transcription_and_code
import os
import uuid


load_dotenv()

transcribe_bp = Blueprint("transcribe", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {".wav", ".mp3", ".m4a", ".webm", ".ogg"}

WHISPER_MODEL = None
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")


def load_whisper():
    global WHISPER_MODEL

    if WHISPER_MODEL is None:
        import whisper
        WHISPER_MODEL = whisper.load_model(MODEL_NAME)
        current_app.logger.info(f"Whisper model '{MODEL_NAME}' loaded.")

    return WHISPER_MODEL


def is_allowed_filename(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT


@transcribe_bp.route("/transcribe", methods=["POST"])
def transcribe():
    audio_path = None

    try:
        print("[transcribe] request recebida")

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_FILE",
                    "message": "Nenhum arquivo de áudio foi enviado."
                }
            }), 400

        audio_file = request.files["file"]

        practice_id = request.form.get("practice_id")
        code = request.form.get("resolution") or request.form.get("code") or ""
        language = request.form.get("language") or "python"

        if not practice_id:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_PRACTICE_ID",
                    "message": "O campo practice_id é obrigatório."
                }
            }), 400

        if not code:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "MISSING_CODE",
                    "message": "O campo resolution ou code é obrigatório."
                }
            }), 400

        practice = Practice.query.get(practice_id)

        if not practice:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "PRACTICE_NOT_FOUND",
                    "message": "Prática não encontrada."
                }
            }), 404

        original_filename = secure_filename(
            audio_file.filename or f"audio_{uuid.uuid4().hex}.wav"
        )

        if not is_allowed_filename(original_filename):
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_AUDIO_TYPE",
                    "message": f"Tipo de arquivo não permitido: {original_filename}"
                }
            }), 400

        unique_name = f"{uuid.uuid4().hex}_{original_filename}"
        audio_path = os.path.join(UPLOAD_FOLDER, unique_name)

        audio_file.save(audio_path)

        print(f"[transcribe] áudio salvo em {audio_path}")

        whisper_model = load_whisper()
        whisper_result = whisper_model.transcribe(audio_path, language="pt")

        transcription_text = whisper_result.get("text", "").strip()

        if not transcription_text:
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "EMPTY_TRANSCRIPTION",
                    "message": "Não foi possível transcrever o áudio. Tente gravar novamente."
                }
            }), 400

        question_text = ""

        if practice.question:
            question_text = practice.question.description or ""

        new_transcription = Transcription(
            practice_id=practice_id,
            transcription=transcription_text,
            resolution=code
        )

        db.session.add(new_transcription)
        db.session.flush()

        eval_result = evaluate_transcription_and_code(
            question=question_text,
            code=code,
            transcription=transcription_text,
            language=language
        )

        feedback_text = eval_result.get("feedback") or "Feedback automático não disponível."

        new_transcription.feedback = feedback_text

        practice.solution = code
        practice.feedback = feedback_text
        practice.status = "completed"

        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "practice_id": str(practice.id),
                "transcription_id": str(new_transcription.id),
                "transcription": transcription_text,
                "feedback": feedback_text,
                "evaluation_success": eval_result.get("success", False)
            },
            "error": eval_result.get("error")
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro na rota /transcribe: %s", e)

        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "TRANSCRIBE_FAILED",
                "message": str(e)
            }
        }), 500