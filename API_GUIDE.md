# 🎯 Guía de API - Sistema Dinámico de Modelos

## 🚀 Inicio Rápido

### 1. Crear cuenta y obtener JWT

```bash
# Registrar usuario
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_user", "password": "password123"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_user", "password": "password123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

> El usuario creado no es admin por defecto. Para usar `/admin/model/upload` y `/admin/model/{model_id}`, el usuario debe tener `is_admin=true` en la base de datos.

### 2. Cargar un modelo (PKL)

```bash
curl -X POST http://localhost:5000/admin/model/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "model_file=@/ruta/a/model.pkl" \
  -F 'metadata={"name":"Mi Modelo de Diabetes","model_id":"diabetes-v1","version":"1.0","description":"Predice riesgo de diabetes","feature_names":["Pregnancies","Glucose","BloodPressure"],"threshold":0.5}'
```

Si el modelo es un pipeline completo, solo necesita `model_file`.

Si el modelo es un modelo independiente con scaler separado:

```bash
curl -X POST http://localhost:5000/admin/model/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "model_file=@/ruta/a/modelo.pkl" \
  -F "scaler_file=@/ruta/a/scaler.pkl" \
  -F 'metadata={"name":"Mi Modelo de Diabetes","model_id":"diabetes-v1","version":"1.0","description":"Predice riesgo de diabetes","feature_names":["Pregnancies","Glucose","BloodPressure"],"threshold":0.5}'
```

### 3. Listar modelos disponibles

```bash
curl -X GET http://localhost:5000/models
```

Ejemplo de respuesta:

```json
{
  "models": [
    {
      "model_id": "diabetes-v1",
      "name": "Mi Modelo de Diabetes",
      "version": "1.0",
      "description": "Predice riesgo de diabetes",
      "model_type": "DecisionTreeClassifier",
      "n_features": 8,
      "output_type": "classification",
      "created_at": "2026-03-17T..."
    }
  ]
}
```

### 4. Obtener schema de un modelo (para frontend)

```bash
curl -X GET http://localhost:5000/models/diabetes-v1/schema
```

Ejemplo de respuesta:

```json
{
  "model_id": "diabetes-v1",
  "name": "Mi Modelo de Diabetes",
  "version": "1.0",
  "description": "...",
  "model_type": "DecisionTreeClassifier",
  "features": [
    {
      "name": "Pregnancies",
      "type": "float",
      "label": "Pregnancies",
      "required": true
    },
    {
      "name": "Glucose",
      "type": "float",
      "label": "Glucose",
      "required": true
    }
  ],
  "output": {
    "type": "classification",
    "classes": [0, 1],
    "has_probability": true
  }
}
```

### 5. Hacer una predicción

```bash
curl -X POST http://localhost:5000/predict/diabetes-v1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Pregnancies": 6,
    "Glucose": 190,
    "BloodPressure": 106,
    "SkinThickness": 40,
    "Insulin": 99,
    "BMI": 35.0,
    "DiabetesPedigreeFunction": 0.55,
    "Age": 45
  }'
```

Ejemplo de respuesta:

```json
{
  "id": 1,
  "model_id": "diabetes-v1",
  "prediction": 1,
  "probability": 0.73,
  "positive": true,
  "threshold": 0.5,
  "created_at": "2026-03-17T13:15:..."
}
```

### 6. Debug mode (opcional)

```bash
curl -X POST "http://localhost:5000/predict/diabetes-v1?debug=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

La respuesta incluirá un objeto `debug` con información adicional del modelo.

---

## 🔧 Parámetros de Upload

### Form Data

```json
{
  "model_file": "archivo.pkl",           // REQUERIDO: El modelo PKL
  "scaler_file": "scaler.pkl",           // OPCIONAL: Scaler PKL si el modelo no es pipeline
  "metadata": {
    "name": "string",                    // Nombre del modelo
    "model_id": "string",                // ID único. Si se omite, se genera a partir de name
    "version": "string",                 // Versión
    "description": "string",             // Descripción
    "feature_names": ["f1", "f2"],     // OPCIONAL: Nombres de features si el modelo no los expone
    "threshold": 0.5                      // OPCIONAL: Umbral para el campo positive
  }
}
```

### Notas de metadata
- `feature_names`: útil cuando el modelo no tiene `feature_names_in_` o `n_features_in_`.
- Si no se proporcionan tipos de feature, el sistema asume `float`.
- `threshold` se usa sólo cuando el modelo devuelve probabilidades.

---

## 🐛 Formatos Soportados

### ✅ Pipeline Completo (recomendado)

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', DecisionTreeClassifier())
])
pipe.fit(X_train, y_train)
joblib.dump(pipe, 'model.pkl')
```

### ✅ Modelo + Scaler Separados

```python
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
import joblib

scaler = StandardScaler()
scaler.fit(X_train)
joblib.dump(scaler, 'scaler.pkl')

model = DecisionTreeClassifier()
model.fit(scaler.transform(X_train), y_train)
joblib.dump(model, 'model.pkl')
```

### Requisitos
- Modelos serializados con `joblib`
- Archivos `.pkl`
- Modelos scikit-learn compatibles
- Si el modelo no es pipeline y necesita escalado, envía `scaler_file`

---

## 📊 Estructura de Datos Guardada

Cada modelo crea una tabla dinámica de predicciones en la base de datos:

```
{model_id}_predictions
├─ id (INT, PK)
├─ <feature1> (FLOAT/INT según tipo)
├─ <feature2> (FLOAT/INT según tipo)
├─ ...
├─ predicted (INT o FLOAT)
├─ probability (FLOAT, NULL si no hay predict_proba)
└─ created_at (TIMESTAMP)
```

Ejemplo: `diabetes_v1_predictions`

---

## 🔐 Autenticación y Roles

### Endpoints públicos (sin JWT)
- `POST /users/register`
- `POST /users/login`
- `GET /models`
- `GET /models/{model_id}/schema`

### Endpoints protegidos (JWT requerido)
- `POST /predict/{model_id}`

### Endpoints admin (JWT + is_admin=true)
- `POST /admin/model/upload`
- `DELETE /admin/model/{model_id}`

---

## 📌 Endpoints disponibles

- `POST /users/register` — Registrar usuario
- `POST /users/login` — Login y obtención de token JWT
- `POST /admin/model/upload` — Subir modelo PKL (admin)
- `GET /models` — Listar modelos activos
- `GET /models/{model_id}/schema` — Obtener esquema de features y output
- `DELETE /admin/model/{model_id}` — Eliminar modelo (lo marca como inactivo)
- `POST /predict/{model_id}` — Ejecutar predicción y almacenar resultado

---

## ❌ Errores comunes

### Error 409: Modelo ya existe

```json
{"error": "El modelo diabetes-v1 ya existe"}
```

**Solución:** Usa un `model_id` diferente o elimina el modelo existente.

### Error 400: Archivo modelo requerido

```json
{"error": "Archivo modelo requerido"}
```

**Solución:** Incluye `model_file` en el form-data.

### Error 403: No autorizado

```json
{"error": "Se requieren permisos de administrador"}
```

**Solución:** Usa un usuario admin para subir o eliminar modelos.

### Error 404: Modelo no encontrado

```json
{"error": "Modelo diabetes-v1 no encontrado"}
```

**Solución:** Verifica `model_id` y usa `/models` para confirmar que el modelo existe.

### Error 422: Validación de features

```json
{
  "errors": {
    "Pregnancies": "Campo requerido",
    "Glucose": "Debe ser de tipo float"
  }
}
```

**Solución:** Envía todos los features esperados con tipos correctos.

---

## 💡 Tips para frontend

1. Consultar `/models/{model_id}/schema` para renderizar formularios dinámicos.
2. Validar tipos de datos antes de hacer el POST a `/predict/{model_id}`.
3. Mostrar `prediction`, `probability` y `positive`.
4. Usar `threshold` del modelo para interpretar la clase positiva.

---

## 📁 Variables de entorno

```env
DATABASE_URL=postgresql://user:pass@host:port/db
JWT_SECRET_KEY=tu_clave_super_secreta
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
PORT=5000
```

---

## 📦 Ejecución local

```bash
python app.py
```

La API se expondrá en `http://localhost:5000`.



