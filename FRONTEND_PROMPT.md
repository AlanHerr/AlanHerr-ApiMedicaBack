# 🚀 PROMPT PARA FRONTEND - COPIA Y PEGA EN CLAUDE/CHATGPT

```
Eres un expert frontend developer. Necesito que integres una API REST médica 
en mi aplicación.

## INFORMACIÓN BASE
- URL Base: https://web-production-856934.up.railway.app
- Autenticación: JWT Bearer Token (guardar en localStorage)
- Content-Type: application/json

## ¿QUÉ HACE LA API?
Es un sistema de predicción de diabetes usando Machine Learning.
- Usuarios se registran/logean
- Acceden a modelos ML dinámicos
- Hacen predicciones rellenando formularios
- El sistema guarda resultados en BD

## ENDPOINTS QUE NECESITO INTEGRAR

### 1. REGISTRO
POST /users/register
{
  "username": "usuario",
  "password": "pass123"
}
Respuesta: { "message": "User registered successfully" }

### 2. LOGIN
POST /users/login
{
  "username": "usuario",
  "password": "pass123"
}
Respuesta: { "access_token": "eyJ..." }
→ Guardar token en localStorage

### 3. LISTAR MODELOS
GET /models
Headers: Authorization: Bearer {token}
Respuesta: {
  "models": [
    { "model_id": "diabetes-v1", "name": "Diabetes v1", "version": "1.0", ... },
    { "model_id": "heart-disease-v1", "name": "Heart Disease", "version": "1.0", ... }
  ]
}

### 4. OBTENER SCHEMA DEL MODELO (para generar formulario dinámico)
GET /models/{model_id}/schema
Headers: Authorization: Bearer {token}
Respuesta: {
  "model_id": "diabetes-v1",
  "features": [
    { "name": "Pregnancies", "type": "int", "label": "Embarazos", "required": true },
    { "name": "Glucose", "type": "float", "label": "Glucosa", "required": true },
    ... más 6 features
  ]
}

### 5. HACER PREDICCIÓN
POST /predict/{model_id}
Headers: Authorization: Bearer {token}
Body: {
  "Pregnancies": 6,
  "Glucose": 190,
  "BloodPressure": 106,
  "SkinThickness": 40,
  "Insulin": 99,
  "BMI": 35.0,
  "DiabetesPedigreeFunction": 0.55,
  "Age": 45
}
Respuesta: {
  "id": 42,
  "prediction": 1,
  "probability": 0.73,
  "positive": true,
  "created_at": "2026-05-22T15:45:30Z"
}

## FLUJO EN FRONTEND
1. Usuario se registra → POST /users/register
2. Usuario hace login → POST /users/login → Guardar token
3. Mostrar dropdown con modelos disponibles (GET /models)
4. Cuando selecciona modelo → Cargar schema (GET /models/{id}/schema)
5. Generar formulario dinámico basado en schema
6. Usuario llena formulario y envía
7. POST /predict/{model_id} con los datos
8. Mostrar resultado (prediction, probability, positive)
9. Interpretar: prediction=1 → RIESGO ALTO, prediction=0 → RIESGO BAJO

## MANEJO DE ERRORES
- 401 → Token expirado, redirigir a login
- 422 → Errores de validación, mostrar junto a campos
- 404 → Modelo no existe
- 503 → API no disponible

## REQUISITOS
Implementa una aplicación con:
- Página de Registro/Login (jwt, localStorage)
- Dashboard con selector de modelos
- Formulario dinámico generado según schema
- Visualización de resultados (prediction + probability)
- Manejo robusto de errores

Genera componentes React con:
- useEffect para obtener modelos
- useState para gestionar estado
- Validación en tiempo real
- Error boundaries
- Loading states
```

---

## 📋 RESPUESTA TIPO QUE ESPERAR

```
El developer te responderá con:

1. Estructura de carpetas propuesta
2. Componentes React:
   - LoginForm.jsx
   - RegisterForm.jsx
   - ModelSelector.jsx
   - DynamicForm.jsx
   - ResultsDisplay.jsx
   - Dashboard.jsx

3. Hook personalizado:
   - useApi.js → Manejar requests con token automático
   - useAuth.js → Gestionar autenticación

4. Servicio:
   - api.js → Todas las funciones para conectar con API

5. Ejemplos de código completos
```

---

## 🔑 PUNTOS CLAVE AL EXPLICAR AL DEVELOPER

### Autenticación
```
El token JWT va en:
Authorization: Bearer {token}

Guardarlo en localStorage:
localStorage.setItem('access_token', response.access_token)

Usarlo en cada request:
headers: { 'Authorization': `Bearer ${token}` }

Si error 401 → Token expirado → Logout
```

### Formulario Dinámico
```
La API retorna el schema con:
- features: array de campos
- Cada campo tiene: name, type, label, required

El frontend DEBE:
1. Leer el schema
2. Generar inputs según type (int/float)
3. Mostrar label en lugar de name
4. Validar según type antes de enviar
```

### Predicción
```
Respuesta clave:
{
  "prediction": 1,      → 0=negativo, 1=positivo
  "probability": 0.73,  → 73% de probabilidad
  "positive": true      → Supera threshold (>0.5)
}

Interpretación:
Si positive=true → "⚠️ RIESGO ALTO (73%)"
Si positive=false → "✅ RIESGO BAJO (25%)"
```

---

## 🎯 ALTERNATIVA: PROMPT MÁS CORTO

Si prefieres un prompt más breve y directo:

```
Soy frontend developer. Necesito integrar esta API REST en mi app:

URL: https://web-production-856934.up.railway.app

Endpoints:
1. POST /users/register - Registrar usuario
2. POST /users/login - Login (retorna JWT)
3. GET /models - Listar modelos ML disponibles
4. GET /models/{id}/schema - Schema del modelo (para generar formulario)
5. POST /predict/{id} - Hacer predicción con datos

El flujo es:
Usuario → Registra → Login (obtiene token) → Selecciona modelo → 
Llena formulario generado dinámicamente → Envía predicción → Ve resultado

¿Puedes generar componentes React para esto?
Incluye validación, error handling y loading states.
```

---

## 📞 SI NECESITAS AYUDA

### El developer podría preguntar:

**P: ¿Dónde guardo el token?**
R: En localStorage después de login
```javascript
localStorage.setItem('access_token', response.access_token)
```

**P: ¿Cómo valido el formulario?**
R: Usa el schema:
```javascript
const schema = await getModelSchema('diabetes-v1');
// schema.features tiene type (int/float) y validaciones
```

**P: ¿Qué pasa si el token expira?**
R: La API retorna 401, redirige a login:
```javascript
if (response.status === 401) {
  localStorage.removeItem('access_token');
  redirect('/login');
}
```

**P: ¿Cómo muestro el resultado?**
R: Usa prediction y probability:
```javascript
if (result.positive) {
  showAlert(`⚠️ Alto riesgo: ${Math.round(result.probability * 100)}%`);
} else {
  showAlert(`✅ Bajo riesgo: ${Math.round((1-result.probability) * 100)}%`);
}
```

---

**Próximos pasos:**
1. Copia uno de estos prompts
2. Pástalo en Claude/ChatGPT
3. Especifica framework (React/Vue/Angular)
4. Pide que genere componentes
5. Integra en tu proyecto

¡Listo! 🚀
```
