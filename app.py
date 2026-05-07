import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Importación de controladores
from controller.user_controller import users_bp
from controller.model_controller import model_bp
from controller.predict_controller import predict_bp

# Importación de la lógica de base de datos
from database import init_db 

load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN DE CORS ---
_origins_env = os.getenv("CORS_ORIGINS")
if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(',') if o.strip()]
else:
    allowed_origins = ["http://localhost:5173", "http://localhost:3000"]

CORS(
    app,
    resources={r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"],
    }},
    supports_credentials=True,
)

# --- INICIALIZACIÓN DE BASE DE DATOS ---
# Forzamos la creación de tablas al arrancar
with app.app_context():
    init_db()

# --- REGISTRO DE BLUEPRINTS ---
app.register_blueprint(users_bp)
app.register_blueprint(model_bp)
app.register_blueprint(predict_bp)

# --- CONFIGURACIÓN JWT ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "tu_clave_secreta_jwt")
jwt = JWTManager(app)

if __name__ == '__main__':
    # Railway usa la variable PORT por defecto
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)