
from flask import Flask, request, jsonify
import whisper
import os
from flask_cors import CORS, cross_origin
import requests
from dotenv import load_dotenv
import json
from db import db
from datetime import date
import uuid

from models.practice import Practice
from models.question import Question
from models.transcription import Transcription
from routes.question import question_bp
from routes.transcribe import transcribe_bp
from routes.evaluate import evaluate_bp 
from routes.report import report_bp

load_dotenv()
app = Flask(__name__)
CORS(app,  resources={r"/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]}},
    supports_credentials=False,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],)
app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.register_blueprint(question_bp)
app.register_blueprint(transcribe_bp)
app.register_blueprint(evaluate_bp)  
app.register_blueprint(report_bp)

api_key = os.getenv('API_KEY')
# print(api_key)
model = whisper.load_model("base")  # Modelo que suporta português
# esse endpoint vai ser usado de 5 em 5 min
# ele preciso receber o que a pessoa digitou e o que ela falou
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_ORIGINS = {"http://localhost:3000", "http://127.0.0.1:3000"}

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return resp
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
    
@app.route('/submit-question', methods=['POST'])
def submit_question():
    # Receber a questão do corpo da requisição
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    
    response = {
        "question": question,
        "answer": "Esta é uma resposta padrão para sua questão."
    }

    return jsonify(response), 200

@app.route('/practice', methods=['POST','OPTIONS'])
@cross_origin(origins=["http://localhost:3000", "http://127.0.0.1:3000"])
def create_practice():
    
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        data = request.get_json() or {}
        print("data", data)
        question = data.get('question_id')  # opcional
        language = data.get('language')
        status = data.get('status', 'active')
        initial_solution = data.get('solution') or ''
        question_uuid = None

        if question:
            print("question", question)
            try:
                question_uuid = uuid.UUID(question)
            except ValueError:
                return jsonify({"error": "question_id inválido (UUID esperado)"}), 400
        p = Practice(questionId=question_uuid,solution=initial_solution, data=date.today(),feedback=None,language=language, status='active')
        db.session.add(p)
        db.session.commit()
        
        return jsonify({"practice_id": p.id}), 201
    except Exception as e:
        db.session.rollback()
        print("Erro ao criar prática:", str(e))
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='127.0.0.1', port=5000)
