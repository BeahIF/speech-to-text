
from flask import Flask, request, jsonify
import whisper
import os
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import json
from flask_sqlalchemy import SQLAlchemy
from models.practice import Practice
from models.question import Question

from models.transcription import Transcription
load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



api_key = os.getenv('API_KEY')
print(api_key)
model = whisper.load_model("base")  # Modelo que suporta português
# esse endpoint vai ser usado de 5 em 5 min
# ele preciso receber o que a pessoa digitou rbm
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    audio_file = request.files['file']
    audio_path = os.path.join('uploads', audio_file.filename)
    mock_code = request.form.get('mock_code')
    resolution = request.form.get('resolution')
    audio_file.save(audio_path)

    result = model.transcribe(audio_path)
    os.remove(audio_path)
# AQUI FALTA EU SALVAR O ARQUIVO DE AUDIO TBM
    new_transcription = Transcription(mock_code=mock_code, transcription='text', resolution=resolution)
    db.session.add(new_transcription)
    db.session.commit()
    return jsonify({"text": result['text']})
    # return ""
@app.route('/test-api', methods=['GET'])
def test_api():
    print("chegando aqui ")
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
      
    },
    data=json.dumps({
        "model": "deepseek/deepseek-chat:free",
        "messages": [
        {
            "role": "user",
            "content": "Você é um assistente que está entrevistando um usuário para uma vaga tech, o usuário deve resolver uma questão de programação. O usuário te informou a questão que ele quer resolver e é a seguinte: ${questao}. Aqui está a solução do usuário:   ${solution} Você deve dar um feedback para ele sobre a solução dele."
        }
        ],
        
    })
    )
    print(response.text)
    
# falta um endpoint que pega o retorno do deepseek e transforma em audio 

@app.route('/submit-question', methods=['POST'])
def submit_question():
    # Receber a questão do corpo da requisição
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    
    #aqui preciso salvar no banco de dados 
    #depois vou chamar o whisper que fica ouvindo a pessoa
    
    
    
    response = {
        "question": question,
        "answer": "Esta é uma resposta padrão para sua questão."
    }

    return jsonify(response), 200
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='127.0.0.1', port=5000)
