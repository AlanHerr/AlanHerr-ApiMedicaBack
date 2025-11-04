
# Importa la clase principal de Flask para crear la aplicación web

import os
from flask import Flask
from controller.products_controller import products_bp
from controller.user_controller import users_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.register_blueprint(products_bp)
app.register_blueprint(users_bp)

# Configuración de la clave secreta para JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "tu_clave_secreta_jwt")
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')