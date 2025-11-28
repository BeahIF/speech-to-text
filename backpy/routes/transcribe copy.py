from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, current_app, send_file
from db import db
from models.practice import Practice
from models.transcription import Transcription
import os
import whisper
from werkzeug.utils import secure_filename
import requests
from flask_cors import CORS
from services.evaluator import evaluate_transcription_and_code

# from gtts import gTTS
import pyttsx3

from flask import send_file
import uuid
load_dotenv()
transcribe_bp = Blueprint('transcribe', __name__)
model = whisper.load_model("base")
api_key = os.getenv("API_KEY")  # Ou o nome real da sua variável
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print("acontece alguma coisa aqui", api_key)
CORS(transcribe_bp, origins=["http://localhost:3000","http://127.0.0.1:3000"])
ALLOWED_EXT = {'.wav', '.mp3', '.m4a', '.webm', '.ogg'}

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
@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe():
    
    print("entrou na rota transcribe", request.form)
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    audio_file = request.files['file']
    practice_id = request.form.get('practice_id')
    resolution = request.form.get('resolution')
    print("resolution", resolution)

    if not practice_id or not resolution:
        return jsonify({"error": "Campos 'practice_id' e 'resolution' são obrigatórios"}), 400

    orig_filename = secure_filename(audio_file.filename or f"audio_{uuid.uuid4()}.wav")
    if not is_allowed_filename(orig_filename):
            # allow but convert if necessary; for simplicity, reject unknown ext
        return jsonify({"error": f"Tipo de arquivo não permitido: {orig_filename}"}), 400

    unique_name = f"{uuid.uuid4().hex}_{orig_filename}"
    audio_path = os.path.join(UPLOAD_FOLDER, unique_name)
    audio_file.save(audio_path)
    
    model = load_whisper()
    result = model.transcribe(audio_path, language="pt")  # ajusta se quiser detect_language
    transcription_text = result.get('text', '').strip()

    practice = Practice.query.get(practice_id)
    print("practice", practice)
    if not practice:
        return jsonify({"error": "Prática não encontrada"}), 404
    question_text = practice.question.description

    # Salva o arquivo temporariamente
    # filename = secure_filename(audio_file.filename)
    # audio_path = os.path.join(UPLOAD_FOLDER, filename)
    # audio_file.save(audio_path)

    # Transcreve o áudio com Whisper
    # result = model.transcribe(audio_path)
    # transcription_text = result['text']
    # os.remove(audio_path)

    # Salva a transcrição na tabela intermediária
    new_transcription = Transcription(
        practice_id=practice_id,
        transcription=transcription_text,
        resolution=resolution
    )
    db.session.add(new_transcription)
    db.session.flush()
    # EU ACHO QUE ESSE PROMPT SÓ SERVE PARA O FINAL DA ENTREVISTA
    # promptFinal = f"""
# Você é um assistente que está entrevistando um usuário para uma vaga
# tech, o usuário deve resolver uma questão de programação. O usuário te
# informou a questão que ele quer resolver e é a seguinte: "{question_text}".
#  A explicação do usuário: "{transcription_text}"
    # E o código até agora foi: "{resolution}"
    # Dê um feedback técnico, objetivo e construtivo.
    # """
    # prompt = f"""
    #     Você é um assistente técnico que está conduzindo uma entrevista de programação com um candidato.
    #     O usuário está resolvendo a seguinte questão:
    #     "{question_text}"
    #     Durante a prática, ele compartilhou essa explicação:"{transcription_text}"
    #     E o código parcial atual é:"{resolution}"
    #     Forneça um **feedback oral intermediário**, como se você estivesse falando diretamente com o candidato.
    #     - Seja claro, breve e didático
    #     - Use linguagem natural, sem termos excessivamente técnicos
    #     - **Não inclua trechos de código**
    #     - Foque em **orientações, elogios e sugestões** que possam ajudar o usuário a melhorar ou continuar seu raciocínio
    #     - Esteja no papel de alguém que está acompanhando a prática e guiando com pequenas dicas
    # """

    # payload = {
    #     "model": "deepseek/deepseek-chat:free",
    #     "messages": [
    #         {"role": "system", "content": "Você é um assistente técnico que avalia explicações de código."},
    #         {"role": "user", "content": prompt}  
    #     ],
        
    # }
    eval_result = evaluate_transcription_and_code(transcription_text, resolution, language='python')

        # use the evaluator feedback text (join feedback sentences)
    feedback_text = " ".join(eval_result.get("feedback", [])) or "Feedback automático gerado."

    # print("paylosd", payload)
    # try:
    #     response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={
    #     "Authorization": f"Bearer {api_key}",
    #     "Content-Type": "application/json",
      
    # }, json=payload)
    
        # result = response.json()
        # print("result", result)
        # feedback_text = result["choices"][0]["message"]["content"]

    new_transcription.feedback = feedback_text
    db.session.commit()

        # 🔊 Converter feedback em áudio
    audio_filename = f"feedback_{uuid.uuid4().hex}.mp3"
    audio_out_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    try:
        engine = pyttsx3.init()
        engine.save_to_file(feedback_text, audio_out_path)
        engine.runAndWait()
    except Exception as e:
        current_app.logger.exception("Erro ao gerar TTS local com pyttsx3: %s", e)
        # print("audio ", audio_filename)
        # tts = gTTS(text=feedback_text, lang='pt-br')
        # tts.save(audio_filename)

    # 🔁 Retornar o áudio pro front
        # return send_file(
        # audio_filename,
        # as_attachment=False,
        # mimetype="audio/mpeg",
        # download_name="feedback.mp3"
        # )
        return jsonify({
            "transcription": transcription_text,
            "feedback": feedback_text,
            "evaluation": eval_result,
            "tts_error":str(e)
        }), 201
        return send_file(audio_out_path, as_attachment=False, mimetype="audio/mpeg", download_name="feedback.mp3"), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro na rota /transcribe: %s", e)

        return jsonify({"error": f"Erro ao gerar feedback: {str(e)}"}), 500
    # db.session.commit()
    finally:
        # opcional: cleanup de arquivos antigos se quiser (não remover o arquivo enviado imediatamente se precisar)
        pass

    # return jsonify({
    #     "message": "Transcrição registrada com sucesso",
    #     "transcription": transcription_text
    # }), 201
