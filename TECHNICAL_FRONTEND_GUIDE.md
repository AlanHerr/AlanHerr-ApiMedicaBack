# 🚀 PROMPT TÉCNICO PARA FRONTEND - API MÉDICA DIABETES

## 📌 INFORMACIÓN BASE

**URL Base:** `https://web-production-856934.up.railway.app`  
**Versión API:** 2.0  
**Ambiente:** Producción  
**Autenticación:** JWT Bearer Token  
**Content-Type:** `application/json`

---

## 🎯 ¿QUÉ HACE ESTA API?

API RESTful especializada en **predicción de riesgo de diabetes** usando Machine Learning. Sistema dinámico que:

1. **Gestiona usuarios** con roles (Admin/Regular)
2. **Administra modelos ML** (Admins cargan modelos .pkl entrenados)
3. **Ejecuta predicciones** dinámicamente según el modelo
4. **Almacena predicciones** en BD para auditoría
5. **Valida datos** automáticamente según cada modelo

**Características Principales:**
- ✅ Autenticación JWT segura
- ✅ Control de acceso por roles
- ✅ Múltiples modelos simultáneamente
- ✅ Validación automática de features
- ✅ Historial de predicciones
- ✅ Manejo de errores completo

---

## 🔐 AUTENTICACIÓN - JWT BEARER TOKEN

### Flujo de Autenticación

```
1. Usuario → POST /users/login (username + password)
2. API → Retorna access_token (JWT)
3. Usuario → Guarda token en localStorage/sessionStorage
4. Cada request → Incluir: Authorization: Bearer {token}
```

### Estructura del Token

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

El token contiene `user_id` y expira según configuración del servidor.

**Token Válido:** 24 horas (típico)  
**Lugar de Almacenamiento:** `localStorage` (recomendado)

---

## 📋 ENDPOINTS PRINCIPALES

### 1️⃣ REGISTRO DE USUARIO

```
POST /users/register
Content-Type: application/json
```

**Request:**
```json
{
  "username": "juan_medico",
  "password": "MiPass123Seguro!"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully"
}
```

**Response (409 Conflict):**
```json
{
  "error": "User already exists"
}
```

**Códigos HTTP:**
- `201` - Registro exitoso
- `400` - Campo faltante
- `409` - Usuario ya existe

---

### 2️⃣ LOGIN

```
POST /users/login
Content-Type: application/json
```

**Request:**
```json
{
  "username": "juan_medico",
  "password": "MiPass123Seguro!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNzE2NTAwMDAwfQ.hash..."
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

**Códigos HTTP:**
- `200` - Login exitoso, token retornado
- `400` - Campos faltantes
- `401` - Credenciales inválidas

**Instrucciones de Implementación:**
```javascript
// Guardar token después de login
localStorage.setItem('access_token', response.access_token);

// Usar en requests posteriores
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};
```

---

### 3️⃣ LISTAR MODELOS DISPONIBLES

```
GET /models
Authorization: Bearer {token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "models": [
    {
      "model_id": "diabetes-v1",
      "name": "Diabetes Classifier v1",
      "version": "1.0",
      "description": "Predice riesgo de diabetes tipo 2 basado en factores clínicos",
      "model_type": "DecisionTreeClassifier",
      "n_features": 8,
      "output_type": "binary_classification",
      "created_at": "2026-05-22T10:30:00Z"
    },
    {
      "model_id": "heart-disease-v1",
      "name": "Heart Disease Predictor",
      "version": "1.0",
      "description": "Predice riesgo de enfermedad cardiovascular",
      "model_type": "LogisticRegression",
      "n_features": 10,
      "output_type": "binary_classification",
      "created_at": "2026-05-22T11:00:00Z"
    }
  ]
}
```

**Códigos HTTP:**
- `200` - Modelos retornados
- `401` - Token inválido o expirado

**Caso de Uso:** Cargar lista desplegable de modelos en el frontend

---

### 4️⃣ OBTENER SCHEMA DE MODELO (Validación Dinámica)

```
GET /models/{model_id}/schema
Authorization: Bearer {token}
Content-Type: application/json
```

**Ejemplo:** `GET /models/diabetes-v1/schema`

**Response (200 OK):**
```json
{
  "model_id": "diabetes-v1",
  "name": "Diabetes Classifier v1",
  "version": "1.0",
  "description": "Predice riesgo de diabetes tipo 2",
  "model_type": "DecisionTreeClassifier",
  "features": [
    {
      "name": "Pregnancies",
      "type": "int",
      "label": "Número de Embarazos",
      "required": true
    },
    {
      "name": "Glucose",
      "type": "float",
      "label": "Glucosa (mg/dL)",
      "required": true
    },
    {
      "name": "BloodPressure",
      "type": "float",
      "label": "Presión Arterial (mmHg)",
      "required": true
    },
    {
      "name": "SkinThickness",
      "type": "float",
      "label": "Espesor de Piel (mm)",
      "required": true
    },
    {
      "name": "Insulin",
      "type": "float",
      "label": "Insulina (μU/mL)",
      "required": true
    },
    {
      "name": "BMI",
      "type": "float",
      "label": "Índice de Masa Corporal",
      "required": true
    },
    {
      "name": "DiabetesPedigreeFunction",
      "type": "float",
      "label": "Función de Pedigree",
      "required": true
    },
    {
      "name": "Age",
      "type": "int",
      "label": "Edad (años)",
      "required": true
    }
  ],
  "output": {
    "type": "binary_classification",
    "classes": [0, 1],
    "has_probability": true
  }
}
```

**Códigos HTTP:**
- `200` - Schema retornado
- `404` - Modelo no encontrado
- `401` - No autenticado

**Caso de Uso:** Generar formulario dinámico en frontend basado en features del modelo

---

### 5️⃣ HACER PREDICCIÓN

```
POST /predict/{model_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Ejemplo:** `POST /predict/diabetes-v1`

**Request:**
```json
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

**Response (200 OK):**
```json
{
  "id": 42,
  "model_id": "diabetes-v1",
  "prediction": 1,
  "probability": 0.73,
  "positive": true,
  "threshold": 0.5,
  "created_at": "2026-05-22T15:45:30Z"
}
```

**Response (422 Unprocessable Entity) - Errores de Validación:**
```json
{
  "errors": {
    "Pregnancies": "Must be an integer",
    "Glucose": "Must be a positive number",
    "BMI": "Value out of expected range"
  }
}
```

**Response (404 Not Found):**
```json
{
  "error": "Model diabetes-v1 not found"
}
```

**Códigos HTTP:**
- `200` - Predicción exitosa
- `422` - Errores de validación en datos
- `404` - Modelo no existe
- `401` - No autenticado
- `410` - Modelo inactivo

**Campos de Respuesta:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | int | ID único de la predicción |
| `model_id` | string | Identificador del modelo usado |
| `prediction` | int | Predicción: 0=negativo, 1=positivo |
| `probability` | float | Probabilidad [0.0 - 1.0] |
| `positive` | boolean | ¿Supera el threshold? |
| `threshold` | float | Umbral usado (típicamente 0.5) |
| `created_at` | string | ISO timestamp |

**Interpretación de Resultado:**
```
prediction = 1 y positive = true → ALTO RIESGO DE DIABETES
prediction = 0 y positive = false → BAJO RIESGO DE DIABETES
probability = 0.73 → 73% de probabilidad de tener diabetes
```

**Parámetros Query Opcionales:**
```
?debug=1  → Retorna información adicional (z-scores, importancia de features, etc.)
```

**Response con ?debug=1:**
```json
{
  "id": 42,
  "model_id": "diabetes-v1",
  "prediction": 1,
  "probability": 0.73,
  "positive": true,
  "threshold": 0.5,
  "debug": {
    "zscores": {
      "Pregnancies": 1.2,
      "Glucose": 2.1,
      "BloodPressure": 0.9,
      "SkinThickness": 0.5,
      "Insulin": 1.8,
      "BMI": 1.5,
      "DiabetesPedigreeFunction": 0.3,
      "Age": 1.1
    },
    "feature_importances": {
      "Glucose": 0.35,
      "BMI": 0.25,
      "Age": 0.20,
      "Pregnancies": 0.10,
      "BloodPressure": 0.05,
      "SkinThickness": 0.03,
      "Insulin": 0.01,
      "DiabetesPedigreeFunction": 0.01
    }
  },
  "created_at": "2026-05-22T15:45:30Z"
}
```

---

## 🏥 HEALTH CHECK - Verificar Salud de API

```
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "API Médica",
  "version": "2.0"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "error": "Database connection failed"
}
```

**Caso de Uso:** Verificar disponibilidad antes de hacer operaciones críticas

---

## 🔄 FLUJO COMPLETO DE USUARIO

### Escenario: Paciente hace predicción de diabetes

```
1. REGISTRO
   POST /users/register
   → Usuario se registra en el sistema

2. LOGIN
   POST /users/login
   → Obtiene JWT token
   → Guarda en localStorage

3. LISTAR MODELOS
   GET /models
   → Muestra lista: "Diabetes Predictor v1", "Heart Disease v1", etc.

4. OBTENER SCHEMA
   GET /models/diabetes-v1/schema
   → Frontend genera formulario dinámicamente con campos:
     - Pregnancies (número embarazos)
     - Glucose (glucosa)
     - BloodPressure (presión)
     - ... otros 5 campos

5. USUARIO LLENA FORMULARIO
   → Entra: Pregnancies: 6, Glucose: 190, etc.

6. HACER PREDICCIÓN
   POST /predict/diabetes-v1
   {data}
   → API retorna:
     prediction: 1
     probability: 0.73
     → MENSAJE: "Alto riesgo de diabetes (73% probabilidad)"

7. GUARDAR/VER HISTORIAL
   → Sistema almacena automáticamente en BD
   → Próximo login, puede ver historial de predicciones anteriores
```

---

## 🛡️ VALIDACIONES AUTOMÁTICAS

La API valida automáticamente:

### Tipo de Dato
```
❌ "Pregnancies": "seis"      → Error: Must be integer
✅ "Pregnancies": 6           → OK
```

### Rango de Valores
```
❌ "Age": -5                  → Error: Must be positive
❌ "Glucose": 2000            → Error: Out of range (0-500)
✅ "Age": 45                  → OK
✅ "Glucose": 150             → OK
```

### Campos Requeridos
```
❌ {"Pregnancies": 6, "Glucose": 150}  → Error: Missing BloodPressure, BMI, etc.
✅ {todos 8 campos requeridos}         → OK
```

---

## 📊 TIPOS DE MODELOS SOPORTADOS

### Binary Classification (Diabetes v1)
```
Output: 0 o 1
Probability: [0.0 - 1.0]
Interpretación: 1 = Positivo, 0 = Negativo
```

### Multiclass Classification (Futuro)
```
Output: 0, 1, 2, 3, ...
Probability: [p0, p1, p2, p3, ...]
```

### Regression (Futuro)
```
Output: Número continuo (ej: 125.5)
Probability: N/A
```

---

## ⚠️ MANEJO DE ERRORES

### Error 401 - No Autenticado
```json
{
  "error": "Unauthorized - Token inválido o expirado"
}
```

**Solución Frontend:**
```javascript
if (response.status === 401) {
  localStorage.removeItem('access_token');
  redirect('/login');  // Redirigir a login
}
```

### Error 422 - Validación Fallida
```json
{
  "errors": {
    "Glucose": "Must be a number",
    "Age": "Must be positive"
  }
}
```

**Solución Frontend:**
```javascript
// Mostrar errores junto a campos del formulario
Object.entries(errors).forEach(([field, message]) => {
  setFieldError(field, message);
});
```

### Error 404 - Modelo No Encontrado
```json
{
  "error": "Model xyz-model not found"
}
```

**Solución Frontend:**
```javascript
// Mostrar mensaje de error
showAlert('El modelo no está disponible');
```

### Error 503 - Servicio No Disponible
```json
{
  "status": "unhealthy",
  "error": "Database connection failed"
}
```

**Solución Frontend:**
```javascript
// Mostrar mensaje de mantenimiento
showAlert('El servicio no está disponible. Intenta más tarde.');
```

---

## 🔑 ESTRUCTURA DE RESPUESTAS

### Respuesta Exitosa (Predicción)
```json
{
  "id": 123,
  "model_id": "diabetes-v1",
  "prediction": 1,
  "probability": 0.73,
  "positive": true,
  "threshold": 0.5,
  "created_at": "2026-05-22T15:45:30Z"
}
```

### Respuesta de Error
```json
{
  "error": "Descripción del error"
}
```

O si es validación:
```json
{
  "errors": {
    "field1": "Error message",
    "field2": "Error message"
  }
}
```

---

## 💻 EJEMPLOS DE CÓDIGO FRONTEND

### Con Fetch API

```javascript
// 1. LOGIN
async function login(username, password) {
  const response = await fetch(
    'https://web-production-856934.up.railway.app/users/login',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }
  );
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data.access_token;
  } else {
    throw new Error('Login failed');
  }
}

// 2. LISTAR MODELOS
async function getModels() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(
    'https://web-production-856934.up.railway.app/models',
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  return data.models;
}

// 3. OBTENER SCHEMA
async function getModelSchema(modelId) {
  const token = localStorage.getItem('access_token');
  const response = await fetch(
    `https://web-production-856934.up.railway.app/models/${modelId}/schema`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return await response.json();
}

// 4. HACER PREDICCIÓN
async function predict(modelId, data) {
  const token = localStorage.getItem('access_token');
  const response = await fetch(
    `https://web-production-856934.up.railway.app/predict/${modelId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }
  );
  
  if (response.ok) {
    return await response.json();
  } else {
    const error = await response.json();
    throw error;
  }
}
```

### Con Axios

```javascript
import axios from 'axios';

const API_URL = 'https://web-production-856934.up.railway.app';

// Crear instancia con configuración
const api = axios.create({ baseURL: API_URL });

// Interceptor para agregar token automáticamente
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
async function login(username, password) {
  const response = await api.post('/users/login', { username, password });
  localStorage.setItem('access_token', response.data.access_token);
  return response.data.access_token;
}

// Listar modelos
async function getModels() {
  const response = await api.get('/models');
  return response.data.models;
}

// Obtener schema
async function getModelSchema(modelId) {
  const response = await api.get(`/models/${modelId}/schema`);
  return response.data;
}

// Hacer predicción
async function predict(modelId, data) {
  const response = await api.post(`/predict/${modelId}`, data);
  return response.data;
}
```

---

## 🎨 COMPONENTES RECOMENDADOS

### 1. Login Form
- Input: username
- Input: password (type="password")
- Button: Enviar
- Almacenar token en localStorage

### 2. Model Selector
- Dropdown: Listar modelos de `GET /models`
- Display: name, description, version
- OnChange: Cargar schema del modelo

### 3. Dynamic Form Generator
- Leer schema de `GET /models/{id}/schema`
- Generar inputs dinámicamente según `features`
- Validación en tiempo real basada en `type`
- Mostrar `label` en lugar de `name`

### 4. Prediction Results
- Display: prediction (0/1) con ícono
- Display: probability (%) con progress bar
- Display: positive (true=rojo, false=verde)
- Display: timestamp

### 5. Error Handling
- Si 401 → Logout y redirigir a login
- Si 422 → Mostrar errores al lado de campos
- Si 404 → Mostrar "Modelo no disponible"
- Si 503 → Mostrar "Servicio en mantenimiento"

---

## 📈 CASOS DE USO COMUNES

### 1. Predicción Simple (Paciente)
```
Paciente llena formulario → Envía predicción → Ve resultado
```

### 2. Evaluaciones Múltiples (Médico)
```
Médico evalúa 10 pacientes → Genera 10 predicciones → Ve estadísticas
```

### 3. Comparación de Modelos (Admin)
```
Admin sube nuevo modelo → Compara con versión anterior → Elige mejor
```

### 4. Auditoría (Hospital)
```
Sistema guarda todas las predicciones → Hospital audita al mes
```

---

## 🚀 CONSIDERACIONES DE PERFORMANCE

- **Caché de modelos:** GET /models solo una vez al iniciar app
- **Lazy loading:** Cargar schema solo cuando se selecciona modelo
- **Debounce:** Si hay búsqueda, esperar 500ms antes de enviar
- **Timeout:** Máximo 30s por predicción
- **Retry:** Si falla, reintentar hasta 3 veces

---

## 🔒 CONSIDERACIONES DE SEGURIDAD

✅ **JWT almacenado en localStorage** (vulnerable a XSS)  
→ Usar sanitización HTML con `DOMPurify`

✅ **Datos sensibles en formulario**  
→ No los guardes en localStorage

✅ **CORS habilitado para tu dominio frontend**  
→ Verificar en CORS_ORIGINS de Railway

✅ **HTTPS obligatorio**  
→ Usar `https://` en producción

---

## 📞 DEBUGGING

### Ver token completo (localStorage)
```javascript
console.log(localStorage.getItem('access_token'));
```

### Verificar salud de API
```bash
curl https://web-production-856934.up.railway.app/health
```

### Simular predicción en postman/insomnia
```
POST https://web-production-856934.up.railway.app/predict/diabetes-v1
Header: Authorization: Bearer {token}
Body: {datos json}
```

---

## 🎯 CHECKLIST PARA FRONTEND DEVELOPER

- [ ] Implementar login/register
- [ ] Guardar token en localStorage
- [ ] Implementar logout (limpiar token)
- [ ] Listar modelos disponibles
- [ ] Cargar schema dinámicamente
- [ ] Generar formulario según schema
- [ ] Validar datos antes de enviar
- [ ] Manejar errores 401, 422, 404, 503
- [ ] Mostrar resultados con interpretación
- [ ] Agregar loading spinners
- [ ] Agregar error messages
- [ ] Probar con múltiples modelos
- [ ] Responsive design
- [ ] Documentar componentes

---

## 📚 RECURSOS

- **API URL:** https://web-production-856934.up.railway.app
- **Health Check:** https://web-production-856934.up.railway.app/health
- **Documentación Completa:** Ver DEPLOYMENT_GUIDE.md en repo

---

**Última actualización:** 22 de Mayo, 2026  
**Versión:** 2.0  
**Ambiente:** Producción en Railway

