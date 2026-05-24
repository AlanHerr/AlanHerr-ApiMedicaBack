import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from controller.user_controller import users_bp
from controller.model_controller import model_bp
from controller.predict_controller import predict_bp
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from sqlalchemy import text
from config.database import get_db_session

load_dotenv()

app = Flask(__name__)

# Configurar CORS
_origins_env = os.getenv("CORS_ORIGINS")

if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://verbose-space-yodel-jpwq47wj75pf7px-3000.app.github.dev",
    ]

CORS(
    app,
    origins=allowed_origins,
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Authorization"],
)

# Garantizar headers CORS en TODAS las respuestas (incluyendo errores y JWT)
@app.after_request
def apply_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "Authorization"
    return response

# Manejar preflight OPTIONS globalmente para todas las rutas
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin", "")
        if origin in allowed_origins:
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.status_code = 200
            return response

# Registrar blueprints
app.register_blueprint(users_bp)
app.register_blueprint(model_bp)
app.register_blueprint(predict_bp)

# JWT
jwt_secret = os.getenv("JWT_SECRET_KEY")
if not jwt_secret:
    raise RuntimeError("JWT_SECRET_KEY is required in environment and must not use a hardcoded fallback")
app.config["JWT_SECRET_KEY"] = jwt_secret
jwt = JWTManager(app)

# Health Check
@app.route('/health', methods=['GET'])
def health_check():
    try:
        session = get_db_session()
        session.execute(text("SELECT 1"))
        session.close()
        return jsonify({
            'status': 'healthy',
            'service': 'API Médica',
            'version': '2.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')