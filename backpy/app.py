
from flask import Flask, request, jsonify
import whisper
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
model = whisper.load_model("base")  # Modelo que suporta português

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    audio_file = request.files['file']
    audio_path = os.path.join('uploads', audio_file.filename)
    audio_file.save(audio_path)

    result = model.transcribe(audio_path)
    os.remove(audio_path)

    return jsonify({"text": result['text']})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='127.0.0.1', port=5000)
