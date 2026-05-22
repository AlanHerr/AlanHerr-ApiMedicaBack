# 🎯 Guía de Integración Frontend

## 🔗 Configuración Base

### URLs de Servidor

**Desarrollo Local:**
```
API_BASE_URL=http://localhost:5000
```

**Producción (cuando esté deployado):**
```
API_BASE_URL=https://alanherr-apimedicaback-production.up.railway.app
```

---

## 🔐 Autenticación (JWT)

### 1. Registro de Usuario
```http
POST /users/register
Content-Type: application/json

{
  "username": "usuario123",
  "password": "SecurePass123!"
}
```

**Respuesta (201):**
```json
{
  "message": "User registered successfully"
}
```

### 2. Login
```http
POST /users/login
Content-Type: application/json

{
  "username": "usuario123",
  "password": "SecurePass123!"
}
```

**Respuesta (200):**
```json
{
  "access_token": "eyJhbGc..."
}
```

**Guardar `access_token` en localStorage:**
```javascript
localStorage.setItem('access_token', response.access_token);
```

---

## 📦 Endpoints Públicos (sin autenticación)

### 3. Listar Modelos Disponibles
```http
GET /models
Content-Type: application/json
```

**Respuesta (200):**
```json
{
  "models": [
    {
      "model_id": "diabetes-v1",
      "name": "Diabetes v1",
      "version": "1.0",
      "description": "Predice diabetes",
      "model_type": "DecisionTreeClassifier",
      "n_features": 8,
      "output_type": "classification",
      "created_at": "2026-05-20T..."
    }
  ]
}
```

### 4. Obtener Schema de Modelo
```http
GET /models/{model_id}/schema
Content-Type: application/json
```

Ejemplo: `GET /models/diabetes-v1/schema`

**Respuesta (200):**
```json
{
  "model_id": "diabetes-v1",
  "name": "Diabetes v1",
  "version": "1.0",
  "description": "Predice diabetes",
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
    },
    {
      "name": "BloodPressure",
      "type": "float",
      "label": "Blood Pressure",
      "required": true
    },
    {
      "name": "SkinThickness",
      "type": "float",
      "label": "Skin Thickness",
      "required": true
    },
    {
      "name": "Insulin",
      "type": "float",
      "label": "Insulin",
      "required": true
    },
    {
      "name": "BMI",
      "type": "float",
      "label": "BMI",
      "required": true
    },
    {
      "name": "DiabetesPedigreeFunction",
      "type": "float",
      "label": "Diabetes Pedigree Function",
      "required": true
    },
    {
      "name": "Age",
      "type": "float",
      "label": "Age",
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

---

## 🤖 Hacer Predicción (Requiere JWT)

### 5. Predicción
```http
POST /predict/{model_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "Pregnancies": 6,
  "Glucose": 190,
  "BloodPressure": 106,
  "SkinThickness": 40,
  "Insulin": 99,
  "BMI": 35.0,
  "DiabetesPedigreeFunction": 0.55,
  "Age": 45
}
```

**Respuesta (200):**
```json
{
  "prediction": 1,
  "probability": 0.87,
  "model_id": "diabetes-v1",
  "timestamp": "2026-05-20T..."
}
```

---

## 📤 Upload de Modelos (Admin Only, Requiere JWT)

### 6. Subir Nuevo Modelo
```http
POST /admin/model/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

Form Data:
- model_file: <archivo.pkl>
- scaler_file: <scaler.pkl> (opcional)
- metadata: JSON string
```

**Metadata JSON:**
```json
{
  "name": "Mi Modelo Diabetes",
  "model_id": "diabetes-custom-v1",
  "version": "1.0",
  "description": "Modelo personalizado",
  "feature_names": ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"],
  "threshold": 0.5
}
```

**Respuesta (201):**
```json
{
  "model_id": "diabetes-custom-v1",
  "name": "Mi Modelo Diabetes",
  "version": "1.0",
  "model_type": "DecisionTreeClassifier",
  "features": [...],
  "output": {...},
  "status": "ready",
  "created_at": "2026-05-20T..."
}
```

**Errores:**
- 403: No es admin
- 400: Archivo inválido
- 409: Modelo ya existe

---

## 🗑️ Eliminar Modelo (Admin Only)

### 7. Borrar Modelo
```http
DELETE /admin/model/{model_id}
Authorization: Bearer {access_token}
```

**Respuesta (204):** Sin contenido

---

## 📋 Headers Requeridos

**Con autenticación:**
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};
```

**Multipart (upload):**
```javascript
// NO incluir Content-Type, el navegador lo establece automáticamente
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};
```

---

## 🛠️ Ejemplo de Implementación (JavaScript/React)

### Instanciar cliente API
```javascript
// services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api = {
  // Auth
  register: (username, password) =>
    fetch(`${API_BASE_URL}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }).then(r => r.json()),

  login: (username, password) =>
    fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }).then(r => r.json()),

  // Models
  listModels: () =>
    fetch(`${API_BASE_URL}/models`).then(r => r.json()),

  getModelSchema: (modelId) =>
    fetch(`${API_BASE_URL}/models/${modelId}/schema`).then(r => r.json()),

  predict: (modelId, data, token) =>
    fetch(`${API_BASE_URL}/predict/${modelId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  uploadModel: (files, metadata, token) => {
    const formData = new FormData();
    formData.append('model_file', files.model);
    if (files.scaler) formData.append('scaler_file', files.scaler);
    formData.append('metadata', JSON.stringify(metadata));

    return fetch(`${API_BASE_URL}/admin/model/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    }).then(r => r.json());
  }
};
```

### Usar en componente
```javascript
// pages/PredictPage.jsx
import { api } from '../services/api';

export function PredictPage() {
  const [models, setModels] = React.useState([]);
  const [selectedModel, setSelectedModel] = React.useState(null);
  const [result, setResult] = React.useState(null);
  const token = localStorage.getItem('access_token');

  React.useEffect(() => {
    api.listModels().then(setModels);
  }, []);

  const handlePredict = async (data) => {
    const res = await api.predict(selectedModel.model_id, data, token);
    setResult(res);
  };

  return (
    <div>
      <select onChange={e => setSelectedModel(e.target.value)}>
        {models.map(m => (
          <option key={m.model_id} value={m.model_id}>
            {m.name} v{m.version}
          </option>
        ))}
      </select>
      {/* Renderizar formulario dinámico basado en schema */}
      {result && <p>Predicción: {result.prediction}</p>}
    </div>
  );
}
```

---

## 🌍 Variables de Entorno (Frontend)

### `.env.local` (desarrollo)
```
REACT_APP_API_URL=http://localhost:5000
```

### `.env.production` (producción)
```
REACT_APP_API_URL=https://alanherr-apimedicaback-production.up.railway.app
```

---

## ✅ Checklist Frontend

- [ ] Login/Registro de usuarios
- [ ] Formulario dinámico basado en schema de modelo
- [ ] Página de predicción
- [ ] Listado de modelos
- [ ] Panel de upload (admin)
- [ ] Manejo de errores HTTP
- [ ] Persistencia de JWT en localStorage
- [ ] CORS habilitado (ya configurado en backend)

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| 401 Unauthorized | Token expirado o inválido. Hacer login nuevamente. |
| 403 Forbidden | Usuario no es admin. Contactar administrador. |
| 404 Model not found | El model_id no existe. Verificar con `/models`. |
| CORS error | Backend ya permite CORS. Verificar URL de API. |
| 422 Unprocessable Entity | Faltan features o tipos incorrectos. Revisar schema. |

---

## 📞 Soporte

- Backend repo: [AlanHerr/AlanHerr-ApiMedicaBack](https://github.com/AlanHerr/AlanHerr-ApiMedicaBack)
- Branch: `development`
