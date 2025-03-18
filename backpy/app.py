
from flask import Flask, request, jsonify
import whisper
import os
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('API_KEY')
print(api_key)
app = Flask(__name__)
CORS(app)
model = whisper.load_model("base")  # Modelo que suporta português
# esse endpoint vai ser usado de 5 em 5 min
# ele preciso receber o que a pessoa digitou rbm
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    audio_file = request.files['file']
    audio_path = os.path.join('uploads', audio_file.filename)
    audio_file.save(audio_path)

    result = model.transcribe(audio_path)
    os.remove(audio_path)
# aqui vai salvar a transcricao no banco e tbm o codigo da pessoa

    return jsonify({"text": result['text']})

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

    # Aqui você pode processar a questão conforme necessário
    # Por exemplo, retornar uma resposta ou análise simples
    #aqui preciso salvar no banco de dados 
    #depois vou chamar o whisper que fica ouvindo a pessoa
    
    
    
    response = {
        "question": question,
        "answer": "Esta é uma resposta padrão para sua questão."
    }

    return jsonify(response), 200
    
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='127.0.0.1', port=5000)
