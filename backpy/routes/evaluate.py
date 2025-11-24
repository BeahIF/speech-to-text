from flask import Blueprint, request, jsonify
from services.evaluator import evaluate_transcription_and_code

evaluate_bp = Blueprint('evaluate', __name__, url_prefix='/evaluate')

@evaluate_bp.route('/', methods=['POST'])
def evaluate():
    data = request.get_json() or {}
    transcription = data.get('transcription', '')
    code = data.get('code', '')
    language = data.get('language', 'python')  # 'python' ou 'js' (heurística)

    result = evaluate_transcription_and_code(transcription, code, language=language)
    return jsonify(result), 200
