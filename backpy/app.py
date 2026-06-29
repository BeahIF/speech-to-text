from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from db import db
from routes.question import question_bp
from routes.transcribe import transcribe_bp
from routes.evaluate import evaluate_bp
from routes.report import report_bp
from routes.practice import practice_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                ]
            }
        },
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    db.init_app(app)

    app.register_blueprint(practice_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(transcribe_bp)
    app.register_blueprint(evaluate_bp)
    app.register_blueprint(report_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "success": True,
            "data": {
                "status": "ok"
            },
            "error": None
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    os.makedirs("uploads", exist_ok=True)

    app.run(debug=True, host="127.0.0.1", port=5000)