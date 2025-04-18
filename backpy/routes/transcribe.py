from flask import Blueprint, request, jsonify
from db import db
from models.practice import Practice
from models.transcription import Transcription
import os
import whisper
from werkzeug.utils import secure_filename
import requests

transcribe_bp = Blueprint('transcribe', __name__)
model = whisper.load_model("base")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    audio_file = request.files['file']
    practice_id = request.form.get('practice_id')
    resolution = request.form.get('resolution')

    if not practice_id or not resolution:
        return jsonify({"error": "Campos 'practice_id' e 'resolution' são obrigatórios"}), 400

    practice = Practice.query.get(practice_id)
    if not practice:
        return jsonify({"error": "Prática não encontrada"}), 404
    question_text = practice.question.description

    # Salva o arquivo temporariamente
    filename = secure_filename(audio_file.filename)
    audio_path = os.path.join(UPLOAD_FOLDER, filename)
    audio_file.save(audio_path)

    # Transcreve o áudio com Whisper
    result = model.transcribe(audio_path)
    transcription_text = result['text']
    os.remove(audio_path)

    # Salva a transcrição na tabela intermediária
    new_transcription = Transcription(
        practice_id=practice_id,
        transcription=transcription_text,
        resolution=resolution
    )
    db.session.add(new_transcription)
    db.session.flush()
    prompt = f"""
Você é um assistente que está entrevistando um usuário para uma vaga
tech, o usuário deve resolver uma questão de programação. O usuário te
informou a questão que ele quer resolver e é a seguinte: "{question_text}".
 A explicação do usuário: "{transcription_text}"
    E o código até agora foi: "{resolution}"
    Dê um feedback técnico, objetivo e construtivo.
    """
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
      
    }
    print("headers", headers)
    payload = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
        
                 {"role": "system", "content": "Você é um assistente técnico que avalia explicações de código."},
            {"role": "user", "content": prompt}  
        ],
        
    }
    print("paylosd", payload)
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
      
    }, json=payload)
        result = response.json()
        print("result", result)
        feedback_text = result["choices"][0]["message"]["content"]

        new_transcription.feedback = feedback_text
        db.session.commit()

        return jsonify({
            "transcription": transcription_text,
            "feedback": feedback_text
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao gerar feedback: {str(e)}"}), 500
    # db.session.commit()

    # return jsonify({
    #     "message": "Transcrição registrada com sucesso",
    #     "transcription": transcription_text
    # }), 201
