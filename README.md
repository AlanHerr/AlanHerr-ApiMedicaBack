# API Médica de Predicción de Diabetes

API RESTful con Flask que predice riesgo de diabetes usando un scaler y un árbol de decisión (scikit‑learn). Autenticación con JWT, persistencia con SQLAlchemy y base de datos PostgreSQL (con fallback a SQLite para desarrollo).

—

## Contenido
- Descripción y stack
- Estructura
- Instalación/Ejecución
- Variables de entorno y conexión a BD
- Blueprints y endpoints (payloads, respuestas, errores)
- Modelos y almacenamiento
- Ejemplos con curl
- Despliegue (Railway) y notas
- Seguridad y buenas prácticas
- Troubleshooting

—

## Descripción y stack
- Framework: Flask 3.x (Blueprints)
- Auth: Flask‑JWT‑Extended (tokens JWT)
- ORM: SQLAlchemy 2.x
- ML: scikit‑learn (DecisionTreeClassifier + StandardScaler) cargados con joblib
- BD: PostgreSQL vía driver psycopg (psycopg3); fallback a SQLite local para desarrollo
- WSGI: Gunicorn (Procfile incluido)

—

## Estructura

```
├── app.py                      # App Flask y registro de blueprints
├── config/
│   └── database.py             # Engine SQLAlchemy, Session y create_all
├── controller/
│   ├── user_controller.py      # /users/register, /users/login
│   └── diabetes_controller.py  # /predict/diabetes (JWT)
├── model/
│   ├── base.py                 # Declarative Base
│   ├── user.py                 # Tabla usuarios
│   └── diabetes.py             # Tabla diabetes_predictions
├── repository/
│   ├── user_repository.py      # Acceso a User
│   └── diabetes_repository.py  # Inserción de predicciones
├── service/
│   ├── user_service.py         # Registro y autenticación
│   ├── diabetes_model.py       # Carga scaler/modelo (.pkl)
│   └── diabetes_service.py     # Validación + pipeline + persistencia
├── model/scaler.pkl            # Scaler entrenado (esperado)
├── model/modelo_arbol_de_decision.pkl # Modelo entrenado (esperado)
├── main.py                     # Alias WSGI opcional (main:app)
├── Procfile                    # Gunicorn
├── requirements.txt
├── curl_examples.sh
└── README.md
```

—

## Instalación y ejecución
1) Entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2) Dependencias
```bash
pip install -r requirements.txt
```
3) Variables (ver siguiente sección) y correr en desarrollo
```bash
python app.py
```

—

## Variables de entorno y conexión a BD
Archivo `.env` (ejemplo):
```
# PostgreSQL (Railway/Heroku)
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
# Compatibilidad: también se acepta MYSQL_URI con el mismo valor
# MYSQL_URI=postgresql://usuario:contraseña@host:puerto/nombre_db

# JWT
JWT_SECRET_KEY=tu_clave_secreta_jwt

# Umbral para clasificar positivo/negativo (opcional)
DIABETES_THRESHOLD=0.5

# Orígenes permitidos para CORS (separados por coma)
# CORS_ORIGINS=https://tu-frontend.vercel.app,https://otro-dominio.com
```

Notas:
- La app prioriza DATABASE_URL y usa el driver `psycopg` (psycopg3). Si tu URL es `postgres://` o `postgresql://`, se normaliza internamente a `postgresql+psycopg://`.
- Si la conexión remota falla, se usa SQLite local `sqlite:///medical_local.db` (útil en desarrollo). En proveedores que exigen SSL, agrega `?sslmode=require`.

—

## Blueprints y endpoints

Blueprints registrados: `users`, `diabetes`.

### POST /users/register (público)
Registra un nuevo usuario.

Request JSON:
```
{
  "username": "demo_user",
  "password": "Demo1234!"
}
```
Respuestas:
- 201: `{ "message": "User registered successfully" }`
- 400: `{ "error": "Username and password required" }`
- 409: `{ "error": "User already exists" }`

### POST /users/login (público)
Autentica y devuelve un JWT.

Request JSON:
```
{
  "username": "demo_user",
  "password": "Demo1234!"
}
```
Respuestas:
- 200: `{ "access_token": "<JWT>" }`
- 401: `{ "error": "Invalid credentials" }`

### POST /predict/diabetes (protegido con JWT)
Recibe los 8 atributos clínicos, ejecuta el pipeline ML y almacena entrada + salida en BD.

Headers: `Authorization: Bearer <JWT>`

Query opcional: `?debug=1` para información de depuración (importancias, z‑scores, hoja del árbol).

Request JSON (nombres aceptan equivalentes minúsculas/underscore):
```
{
  "Pregnancies": 2,
  "Glucose": 130.0,
  "BloodPressure": 70.0,
  "SkinThickness": 20.0,
  "Insulin": 85.0,
  "BMI": 28.1,
  "DiabetesPedigreeFunction": 0.45,
  "Age": 33
}
```
Respuesta 200:
```
{
  "id": 1,
  "prediction": 0,
  "probability": 0.23,
  "positive": false,
  "threshold": 0.5
  // si debug=1 → "debug": { expected_feature_order, zscores, leaf_id, feature_importances }
}
```
Errores 422 (validación):
```
{ "errors": { "Age": "Debe ser mayor a 0", "BMI": "Debe ser mayor a 0" } }
```

—

## Modelos y almacenamiento

Archivos esperados:
- `model/scaler.pkl` (StandardScaler)
- `model/modelo_arbol_de_decision.pkl` (DecisionTreeClassifier)

Orden de features esperado (también detectado mediante `feature_names_in_` si está presente):
`["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]`

Tablas principales:
- `users`: id, username, password(hash)
- `diabetes_predictions`: campos de entrada + `predicted`, `probability`, `created_at`

—

## Ejemplos con curl

Base URL (Railway):
```bash
BASE="https://alanherr-apimedicaback-production.up.railway.app"
```

Registrar (opcional):
```bash
curl -sS -X POST "$BASE/users/register" -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"Demo1234!"}'
```

Login → token:
```bash
TOKEN=$(curl -sS -X POST "$BASE/users/login" -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"Demo1234!"}' | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
```

Predicción:
```bash
curl -sS -X POST "$BASE/predict/diabetes" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"Pregnancies":2,"Glucose":130,"BloodPressure":70,"SkinThickness":20,"Insulin":85,"BMI":28.1,"DiabetesPedigreeFunction":0.45,"Age":33}'
```

Debug:
```bash
curl -sS -X POST "$BASE/predict/diabetes?debug=1" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"Pregnancies":2,"Glucose":130,"BloodPressure":70,"SkinThickness":20,"Insulin":85,"BMI":28.1,"DiabetesPedigreeFunction":0.45,"Age":33}'
```

Consejo de seguridad: evita imprimir o hardcodear el token. Puedes guardar la cabecera en un archivo con permisos 600 y usar `-H @archivo`.

—

## Despliegue (Railway)
- Variables: `DATABASE_URL` (o `MYSQL_URI`), `JWT_SECRET_KEY`, `PORT` (Railway la define).
- `Procfile`: `web: gunicorn app:app --bind 0.0.0.0:$PORT`
- `main.py` reexpone WSGI como `main:app` si alguna plataforma lo requiere.
- Driver de BD: se usa `psycopg` (psycopg3). Si ves errores con `psycopg2`, limpia caché y reinstala deps para tomar el `requirements.txt` actualizado.

—

## Seguridad y buenas prácticas
- JWT: tokens de corta duración recomendados; considera añadir refresh tokens.
- Passwords: se guardan hasheadas (Werkzeug).
- No subas `.env` ni secretos al repo. Usa variables del entorno del proveedor.
- Rate limiting y CORS se pueden añadir según el cliente/consumo esperado.
- En desarrollo, Flask reloader duplica algunas acciones de import: no implica dobles inserciones.

—

## Troubleshooting
- "No module named 'psycopg2'": estás usando el driver viejo. Este proyecto usa psycopg3. Asegúrate de instalar `psycopg[binary]` y que la URL sea `postgresql(+psycopg)://`.
- "Connection via SSH" al ver la BD: tu Postgres de Railway se accede por TCP/SSL, no por SSH. Conéctate con la cadena `postgresql://...` y `sslmode=require` si aplica.
- Veo dos logs de “Conexión a la base de datos remota exitosa.”: el reloader de Flask en dev crea dos procesos. En prod (Gunicorn) no ocurre, y se ha reducido el log duplicado.

—

© Proyecto API Médica de Predicción de Diabetes
}
```

---

**Autor:** AlanHerr
