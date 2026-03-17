# 🎯 Guía de API - Sistema Dinámico de Modelos

## 🚀 Inicio Rápido

### 1. Crear cuenta y obtener JWT

```bash
# Registrar usuario ADMIN
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_user", "password": "password123"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_user", "password": "password123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

### 2. Cargar un modelo (PKL)

```bash
# Formato 1: Un archivo PKL completo (Pipeline o modelo simple)
curl -X POST http://localhost:5000/admin/model/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "model_file=@/ruta/a/model.pkl" \
  -F 'metadata={
    "name": "Mi Modelo de Diabetes",
    "model_id": "diabetes-v1",
    "version": "1.0",
    "description": "Predice riesgo de diabetes",
    "feature_labels": {
      "Pregnancies": "Número de embarazos",
      "Glucose": "Nivel de glucosa",
      "BloodPressure": "Presión arterial"
    }
  }'

# Formato 2: Dos archivos (scaler + modelo separados)
curl -X POST http://localhost:5000/admin/model/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "model_file=@/ruta/a/modelo.pkl" \
  -F "scaler_file=@/ruta/a/scaler.pkl" \
  -F 'metadata={...}'
```

### 3. Listar modelos disponibles

```bash
curl -X GET http://localhost:5000/models
```

Response:
```json
{
  "models": [
    {
      "model_id": "diabetes-v1",
      "name": "Mi Modelo de Diabetes",
      "version": "1.0",
      "description": "...",
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

Response:
```json
{
  "model_id": "diabetes-v1",
  "name": "Mi Modelo de Diabetes",
  "description": "...",
  "features": [
    {
      "name": "Pregnancies",
      "type": "int",
      "label": "Número de embarazos",
      "required": true
    },
    {
      "name": "Glucose",
      "type": "float",
      "label": "Nivel de glucosa",
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
TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

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

Response:
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
curl -X POST http://localhost:5000/predict/diabetes-v1?debug=true \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 🔧 Parámetros de Upload

### Form Data

```json
{
  "model_file": "archivo.pkl",           // REQUERIDO: El modelo
  "scaler_file": "scaler.pkl",           // OPCIONAL: Scaler si no es Pipeline
  "metadata": {
    "name": "string",                    // Nombre del modelo
    "model_id": "string",                // ID único (auto-generado si no se proporciona)
    "version": "string",                 // Versión
    "description": "string",             // Descripción
    "feature_labels": {                  // OPCIONAL: Labels para frontend
      "feature_name": "Descripción"
    },
    "threshold": 0.5                     // OPCIONAL: Umbral de clasificación
  }
}
```

---

## 🐛 Formatos Soportados

### ✅ Soportados

**Opción 1: Pipeline Completo**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('modelo', DecisionTreeClassifier())
])
pipe.fit(X_train, y_train)
joblib.dump(pipe, 'model.pkl')
```

**Opción 2: Scaler + Modelo Separados**
```python
scaler = StandardScaler()
scaler.fit(X_train)
joblib.dump(scaler, 'scaler.pkl')

modelo = DecisionTreeClassifier()
modelo.fit(scaler.transform(X_train), y_train)
joblib.dump(modelo, 'modelo.pkl')
```

---

## 📊 Estructura de Datos Guardada

Cada modelo crea su propia tabla en la BD:

```
{model_id}_predictions
├─ id (INT, PK)
├─ feature1 (FLOAT/INT según tipo)
├─ feature2 (FLOAT/INT según tipo)
├─ ...
├─ predicted (INT o FLOAT)
├─ probability (FLOAT, NULL si no tiene predict_proba)
└─ created_at (TIMESTAMP)
```

Ejemplo: `diabetes_v1_predictions`

---

## 🔐 Autenticación y Roles

### Endpoints Públicos (sin JWT)
- `POST /users/register`
- `POST /users/login`
- `GET /models`
- `GET /models/{model_id}/schema`

### Endpoints Protegidos (JWT requerido)
- `POST /predict/{model_id}` ← Cualquier usuario autenticado

### Endpoints Admin (JWT + is_admin=true)
- `POST /admin/model/upload`
- `DELETE /admin/model/{model_id}`

---

## ❌ Errores Comunes

### Error 409: Modelo ya existe
```
{"error": "El modelo diabetes-v1 ya existe"}
```
**Solución:** Usa un `model_id` diferente

### Error 422: Validación de features
```
{
  "errors": {
    "Pregnancies": "Campo requerido",
    "Glucose": "Debe ser float"
  }
}
```
**Solución:** Verifica que envíes TODOS los features con tipos correctos. Usa `/models/{model_id}/schema` para ver qué espera el modelo.

### Error 403: No autorizado
```
{"error": "Se requieren permisos de administrador"}
```
**Solución:** Solo ADMIN puede hacer upload. Contacta al administrador del sistema.

### Error 404: Modelo no encontrado
```
{"error": "Modelo {model_id} no encontrado"}
```
**Solución:** Usa `/models` para listar modelos disponibles y verifica el `model_id`.

---

## 🧪 Test Completo

```bash
#!/bin/bash

# 1. Registrar
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test123"}' | jq -r '.access_token')

# 3. Upload modelo (necesita archivo real)
# curl -X POST http://localhost:5000/admin/model/upload \
#   -H "Authorization: Bearer $TOKEN" \
#   -F "model_file=@model.pkl" \
#   -F 'metadata={"name":"Test","description":"Test model"}'

# 4. Listar modelos
curl -X GET http://localhost:5000/models | jq

# 5. Obtener schema
# curl -X GET http://localhost:5000/models/test-model/schema | jq

# 6. Hacer predicción
# curl -X POST http://localhost:5000/predict/test-model \
#   -H "Authorization: Bearer $TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"feature1": 1, "feature2": 2}'
```

---

## 📚 Referencia de Tipos de Features

Tipos soportados al extraer metadata:

```
"int"   → Entero (Pregnancies, Age)
"float" → Decimal (Glucose, BMI, etc.)
```

Si el modelo no especifica tipos explícitamente, se asume `float` por defecto.

---

## 🎬 Próximos Pasos para Frontend

1. **Obtener schema dinámico:**
   ```javascript
   const response = await fetch(`/models/${model_id}/schema`);
   const schema = await response.json();
   ```

2. **Renderizar form dinámicamente** con campos según `schema.features`

3. **Validar entrada** antes de enviar a `/predict/{model_id}`

4. **Mostrar resultado** con `prediction` y `probability`

---

## 🔧 Variables de Entorno

```env
DATABASE_URL=postgresql://user:pass@host:port/db
JWT_SECRET_KEY=tu_clave_super_secreta
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

**Última actualización:** Marzo 17, 2026
**Versión:** 1.0 - Sistema Dinámico de Modelos
