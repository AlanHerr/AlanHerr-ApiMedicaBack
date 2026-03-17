
# Importa la clase principal de Flask para crear la aplicación web

import os
from flask import Flask
from flask_cors import CORS
from controller.user_controller import users_bp
from controller.model_controller import model_bp
from controller.predict_controller import predict_bp
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar CORS: orígenes desde env CORS_ORIGINS (separados por coma)
_origins_env = os.getenv("CORS_ORIGINS")
if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(',') if o.strip()]
else:
    # Defaults de desarrollo; para producción define CORS_ORIGINS (ej: https://tu-app.vercel.app)
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

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

# Registrar blueprints
app.register_blueprint(users_bp)
app.register_blueprint(model_bp)
app.register_blueprint(predict_bp)

# Configuración de la clave secreta para JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "tu_clave_secreta_jwt")
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')