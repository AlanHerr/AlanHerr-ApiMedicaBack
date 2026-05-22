# 📝 Prompt para Frontend (Copilot)

**Copiar este prompt cuando inicies el repositorio frontend:**

---

## PROMPT PARA COPILOT

```
Voy a crear un frontend React + Vite que se conecta a una API backend.

## Información del Backend

API Base URL (desarrollo): http://localhost:5000
API Base URL (producción): https://alanherr-apimedicaback-production.up.railway.app

## Endpoints Disponibles

### Auth (sin JWT)
- POST /users/register → { username, password }
- POST /users/login → { username, password } → { access_token }

### Models (sin JWT)
- GET /models → lista de modelos
- GET /models/{model_id}/schema → schema dinámico

### Predict (con JWT)
- POST /predict/{model_id} + Authorization: Bearer {token} → predicción

### Admin (con JWT + is_admin)
- POST /admin/model/upload → multipart (model_file, scaler_file, metadata)
- DELETE /admin/model/{model_id}

## Lo que necesito

1. Estructura React con carpetas: components/, pages/, services/, context/
2. AuthContext para manejar JWT y usuario actual
3. Servicio api.js que encapsule todos los endpoints
4. Componentes:
   - LoginPage (registro + login)
   - DashboardPage (listado de modelos)
   - PredictPage (formulario dinámico basado en schema, hacer predicción)
   - AdminPage (upload de modelos)
5. Rutas con react-router-dom
6. Variables de entorno: VITE_API_URL
7. Manejo básico de errores
8. Persistencia de JWT en localStorage

## Stack
- React 18 + Vite
- react-router-dom para rutas
- Fetch API (o axios si lo prefieres)
- Tailwind CSS para estilos (opcional, pero recomendado)

## Comportamiento

- Usuario se registra → login automático
- Dashboard muestra modelos disponibles
- Click en modelo → va a página de predicción
- Formulario se genera dinámicamente según features del schema
- Muestra resultado de predicción
- Admin puede subir modelos via formulario multipart
- Token se guarda en localStorage y se envía en Authorization header

¿Puedes crear esta estructura lista para ejecutar?
```

---

## 🚀 Uso

1. Crea repositorio nuevo en GitHub: `AlanHerr-ApiFrontend`
2. Clone locally: `git clone https://github.com/AlanHerr/AlanHerr-ApiFrontend.git`
3. En VS Code con Copilot abierto, pega el **PROMPT PARA COPILOT** arriba
4. Copilot creará toda la estructura
5. Ejecuta: `npm install && npm run dev`
6. Abre: http://localhost:3000

---

## ✅ Lo que te entregará Copilot

- [x] Proyecto React inicializado
- [x] Carpeta src/ con estructura completa
- [x] AuthContext funcional
- [x] Servicios API listos
- [x] Componentes de Login, Dashboard, Predict, Admin
- [x] Routing configurado
- [x] .env.local con variables
- [x] Manejo básico de errores

---

## 📋 Post-Setup

Después que Copilot cree el proyecto:

```bash
cd AlanHerr-ApiFrontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev

# En otra terminal, iniciar backend
cd ../AlanHerr-ApiMedicaBack
python app.py
```

Luego abre http://localhost:3000 en el navegador.

---

## 🔑 Puntos Clave

- **Token Storage**: localStorage (no es ideal para producción, pero para desarrollo sirve)
- **CORS**: Backend ya tiene CORS habilitado para localhost
- **Schema Dinámico**: Usar la respuesta de `/models/{id}/schema` para renderizar formulario
- **Admin**: Solo usuarios con `is_admin=true` pueden subir modelos
- **Rutas Protegidas**: Si no hay token, redirigir a Login

---

## 📞 Backend Repo Info

- Repo: `AlanHerr-ApiMedicaBack`
- Branch: `development`
- Documentación: 
  - `FRONTEND_INTEGRATION.md` (endpoints detallados)
  - `API_GUIDE.md` (ejemplos curl)
  - `curl_examples.sh` (script de prueba)
