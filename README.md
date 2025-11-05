
# API Médica de Predicción de Diabetes

API RESTful con Flask para predicción de diabetes basada en modelos de Machine Learning (scaler + árbol de decisión). Incluye autenticación JWT para gestión de usuarios. Persistencia con SQLAlchemy y BD remota (o SQLite local como respaldo).

---

## Tabla de Contenidos
1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Instalación y Ejecución](#instalación-y-ejecución)
3. [Variables de Entorno](#variables-de-entorno)
4. [Tabla de Endpoints](#tabla-de-endpoints)
5. [Pruebas con curl_examples.sh](#pruebas-con-curlexamplessh)
6. [Notas de Seguridad y Roles](#notas-de-seguridad-y-roles)
7. [Testing y Buenas Prácticas](#testing-y-buenas-prácticas)
8. [Autor](#autor)

---



## Estructura del Proyecto

```
API/
├── app.py
├── config/
│   ├── __init__.py
│   └── database.py
├── controller/
│   ├── __init__.py
│   ├── diabetes_controller.py
│   └── user_controller.py
├── model/
│   ├── __init__.py
│   ├── base.py
│   ├── diabetes.py
│   └── user.py
├── repository/
│   ├── __init__.py
│   ├── diabetes_repository.py
│   └── user_repository.py
├── service/
│   ├── __init__.py
│   ├── diabetes_model.py
│   ├── diabetes_service.py
│   └── user_service.py
├── .env
├── requirements.txt
├── curl_examples.sh
└── README.md
```

---



## Instalación y Ejecución

### Backend (API Flask)
1. **Crea y activa un entorno virtual (.venv):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno (ver sección abajo).
4. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

---

## Variables de Entorno (Backend)

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
MYSQL_URI=postgresql://usuario:contraseña@host:puerto/nombre_db
JWT_SECRET_KEY=tu_clave_secreta_jwt
# Umbral operativo opcional para clasificar positivo/negativo
DIABETES_THRESHOLD=0.5
```

- `MYSQL_URI`: cadena de conexión SQLAlchemy a tu BD remota. Puede apuntar a PostgreSQL (ej. `postgresql://...`) o a MySQL (`mysql+driver://...`). Si no se define o falla la conexión, se usa SQLite local `medical_local.db` como respaldo.
- `JWT_SECRET_KEY`: clave secreta para firmar tokens JWT (usa una aleatoria fuerte en producción).
- `DIABETES_THRESHOLD`: umbral para marcar `positive` en la respuesta del modelo (por defecto 0.5).

---

## Tabla de Endpoints

| Método | Endpoint              | Descripción                        | Autenticación |
|--------|-----------------------|------------------------------------|---------------|
| POST   | /predict/diabetes     | Predice diabetes y almacena datos  | JWT           |
| POST   | /users/register       | Registra un nuevo usuario          | No            |
| POST   | /users/login          | Inicia sesión y devuelve JWT       | No            |

---

## Despliegue en Railway (u otros WSGI)

- Asegúrate de definir la variable de entorno `PORT` (Railway la define automáticamente) y tus credenciales (`MYSQL_URI`, `JWT_SECRET_KEY`).
- Este repo incluye un `Procfile` con:
  
   `web: gunicorn app:app --bind 0.0.0.0:$PORT`

   Con eso, el servidor WSGI apunta al objeto `app` definido en `app.py`.
- Si tu plataforma espera el módulo `main:app`, también incluimos `main.py` que reexpone el objeto WSGI.
- El warning de `pkg_resources` es informativo. Si deseas silenciarlo, puedes:
   - Actualizar gunicorn a una versión más reciente, o
   - Fijar `setuptools<81`.

## Modelos de ML

- Archivos esperados en `model/`:
   - `scaler.pkl`: StandardScaler entrenado (scikit-learn)
   - `modelo_arbol_de_decision.pkl`: DecisionTreeClassifier entrenado
- Orden de features esperado por el pipeline (también expuesto vía `feature_names_in_`):
   `["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]`
- Nota: si el modelo fue serializado con otra versión de scikit-learn, puede aparecer un warning al cargar. Conviene alinear versiones o re-serializar.

## Pruebas con curl_examples.sh

El archivo [`curl_examples.sh`](./curl_examples.sh) contiene ejemplos de cómo consumir los endpoints clave de la API usando `curl`, incluyendo:
- Registro y login de usuario
- Obtención de token JWT
- Predicción de diabetes (protegida con JWT) y almacenamiento en BD

Para ejecutar los ejemplos:
```bash
chmod +x curl_examples.sh
./curl_examples.sh
```

Puedes modificar los datos de ejemplo según tus necesidades.

---

## Notas de Seguridad y Roles

- **Roles:** Actualmente todos los usuarios registrados pueden acceder a los endpoints protegidos (no hay distinción de roles).
- **JWT:** Los endpoints protegidos (como `/predict/diabetes` y `/users/`) requieren autenticación JWT.
- **Contraseñas:** Se almacenan de forma segura (hash).
- **Variables sensibles:** No subas `.env` ni credenciales al repositorio.
- **Base de datos:** Si la conexión a Railway falla, se usa SQLite local como respaldo.

---

## Testing y Buenas Prácticas

- El backend está modularizado siguiendo buenas prácticas (modelo, repositorio, servicio, controlador).
- Puedes probar la API sin frontend usando el archivo [`curl_examples.sh`](./curl_examples.sh).
- Los endpoints devuelven respuestas en formato JSON.
- Para pruebas automáticas, puedes usar herramientas como Postman, Insomnia o pytest.

### Pruebas mínimas recomendadas

1. **Login con credenciales válidas:**
   - Espera un token JWT válido.
2. **Login con credenciales inválidas:**
   - Espera error 401.
3. **Acceso a ruta protegida sin token:**
   - Espera error 401.
4. **Acceso a ruta protegida con token válido:**
   - Espera respuesta exitosa.

---


## Predicción de Diabetes: Payload y Respuesta

Endpoint: `POST /predict/diabetes`

Cuerpo JSON requerido (campos obligatorios):

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

Notas:
- Se aceptan también nombres equivalentes en minúscula o con guiones bajos (por ejemplo, `blood_pressure`, `diabetes_pedigree_function`).
- Los valores deben ser numéricos (enteros o flotantes según corresponda).

Respuesta exitosa (200):
```
{
   "id": 1,
   "prediction": 0,
   "probability": 0.23,
   "positive": false,
   "threshold": 0.5
}
```
Donde `id` es el registro almacenado en la BD, `prediction` ∈ {0,1} y `probability` es la probabilidad de clase positiva (si el modelo la expone).

Umbral configurable: puedes ajustar la clasificación operativa con la variable de entorno `DIABETES_THRESHOLD` (por defecto 0.5).

Depuración opcional: añade `?debug=1` al endpoint para obtener detalles como z-scores por feature, importancia de variables y hoja del árbol.

Error de validación (422):
```
{
   "errors": {
      "Glucose": "Debe ser número (float)",
      "Age": "Debe ser mayor a 0"
   }
}
```

---

**Autor:** AlanHerr
