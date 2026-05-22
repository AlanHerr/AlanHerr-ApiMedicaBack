# Seguridad de la aplicación

Este documento reúne las partes del código relacionadas con la seguridad (autenticación, autorización, manejo de contraseñas y configuración JWT).

**Archivos clave**
- [app.py](app.py#L1-L120): Configuración de CORS y JWT.
- [.env](.env#L1-L40): Variable `JWT_SECRET_KEY`.
- [controller/user_controller.py](controller/user_controller.py#L1-L80): Endpoints de registro y login.
- [service/user_service.py](service/user_service.py#L1-L120): Hashing y verificación de contraseñas.
- [model/user.py](model/user.py#L1-L80): Definición del modelo `User` (campo `password`).
- [repository/user_repository.py](repository/user_repository.py#L1-L120): Acceso a usuarios en la BD.
- [controller/predict_controller.py](controller/predict_controller.py#L1-L160): Uso de `@jwt_required()` para proteger predicciones.
- [controller/model_controller.py](controller/model_controller.py#L1-L260): Endpoints administrativos protegidos y verificación de `is_admin`.
- [curl_examples.sh](curl_examples.sh#L1-L120) y [API_GUIDE.md](API_GUIDE.md#L1-L200): ejemplos de uso con `Authorization: Bearer <token>`.

---

## Fragmentos importantes

1) Configuración JWT en `app.py`:

```python
# Configuración de la clave secreta para JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "tu_clave_secreta_jwt")
jwt = JWTManager(app)
```

2) Variable de entorno en `.env`:

```
JWT_SECRET_KEY=tu_clave_secreta_jwt_super_segura
```

3) Registro y login en `controller/user_controller.py`:

```python
@users_bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ...
    user = UserService.register_user(username, password)

@users_bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = UserService.authenticate(username, password)
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200
```

4) Hashing de contraseñas en `service/user_service.py`:

```python
from werkzeug.security import generate_password_hash, check_password_hash

hashed_password = generate_password_hash(password)
...
if user and check_password_hash(user.password, password):
    return user
```

5) Modelo `User` en `model/user.py` (campo password):

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
```

6) Endpoints protegidos con JWT en `controller/predict_controller.py` y `controller/model_controller.py`:

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@predict_bp.route('/predict/<model_id>', methods=['POST'])
@jwt_required()
def predict(model_id):
    ...

@model_bp.route('/admin/model/upload', methods=['POST'])
@jwt_required()
def upload_model():
    user_id = get_jwt_identity()
    # verificar admin
    if not check_admin(int(user_id)):
        return jsonify({'error': 'Se requieren permisos de administrador'}), 403
```

7) Ejemplo de uso (cabecera Authorization) en `curl_examples.sh` y `API_GUIDE.md`:

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario1", "password": "12345"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -i -X POST http://localhost:5000/predict/diabetes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{ ... }'
```

---

## Observaciones y recomendaciones rápidas
- La clave JWT se toma de `.env`; en producción asegúrate de usar un secreto fuerte y rotarlo según política.
- Revisar expiración de tokens (no configurado explícitamente en el código actual).
- Considerar añadir `fresh` tokens, `access`/`refresh` tokens y protección CSRF si corresponde.
- Logs: evitar imprimir contraseñas o tokens en logs.

Si quieres, puedo:
- Añadir más fragmentos (por ejemplo middleware o manejo de errores JWT).
- Crear tests para endpoints protegidos.
- Revisar y proponer configuración de expiración/refresh.
