# 🚀 GUÍA DE DEPLOYMENT EN RAILWAY

## ✅ TODOS LOS FIXES CRÍTICOS HAN SIDO APLICADOS

```
✅ Fix 1: engine.execute() → compatible con SQLAlchemy 2.x
✅ Fix 2: .env.example → credenciales no expuestas
✅ Fix 3: Endpoint /health → health checks funcionales
✅ Fix 4: Procfile mejorado → workers configurados (4x concurrencia)
```

---

## 📝 PRE-DEPLOYMENT CHECKLIST

### 1. Cambiar Contraseña PostgreSQL (CRÍTICO)
```bash
# En Railway Dashboard:
# 1. Ir a Databases → PostgreSQL
# 2. Click en los 3 puntos → Connect
# 3. Copiar la nueva DATABASE_URL
# 4. Cambiar contraseña (Generate new password)
# 5. GUARDAR LA URL NUEVA
```

**POR QUÉ:** Tu contraseña actual está expuesta en local

---

### 2. Generar JWT_SECRET_KEY Seguro (CRÍTICO)

```bash
# En tu terminal LOCAL:
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Ejemplo output:
# V1a2B3c4D5e6F7g8H9i0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5Y6Z...
```

**Copiar este valor - lo necesitarás para Railway**

---

### 3. Push a GitHub (si aún no lo hiciste)

```bash
cd /workspaces/AlanHerr-ApiMedicaBack

# Verificar que .env NO está en git
git ls-files | grep ".env"  # Debe estar VACÍO

# Si todo bien:
git add .
git commit -m "fix: SQLAlchemy 2.x compatibility, Railway readiness, health checks"
git push origin development  # o main según tu branch
```

---

## 🚢 PASOS EN RAILWAY DASHBOARD

### 1. Crear Nuevo Proyecto
```
1. Railway.app → New Project
2. GitHub → Seleccionar repositorio
3. Deploy
```

### 2. Crear Base de Datos PostgreSQL
```
1. + → PostgreSQL
2. Esperar a que inicie
3. Copiar TODAS las credenciales
```

### 3. Configurar Variables de Entorno

Ve a **Deploy → Variables** y agrega:

```
DATABASE_URL = [Copiar desde PostgreSQL plugin]
JWT_SECRET_KEY = [La clave generada con secrets.token_urlsafe()]
FLASK_ENV = production
DEBUG = False
CORS_ORIGINS = https://tu-frontend.com,https://www.tu-frontend.com
DIABETES_THRESHOLD = 0.5
```

**IMPORTANTE:**
- `DATABASE_URL`: Obtenla del PostgreSQL plugin (incluye usuario, pass, host, port, dbname)
- `JWT_SECRET_KEY`: La que generaste con `secrets.token_urlsafe(64)`
- `FLASK_ENV`: DEBE ser `production`
- `DEBUG`: DEBE ser `False`

---

## 🔍 VERIFICAR DEPLOYMENT

Una vez deployado en Railway:

### 1. Test Health Check
```bash
curl https://tu-api-railway.up.railway.app/health

# Esperado:
# {"status":"healthy","service":"API Médica","version":"2.0"}
```

### 2. Test Registro
```bash
curl -X POST https://tu-api-railway.up.railway.app/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'

# Esperado: 201 Created
# {"message":"User registered successfully"}
```

### 3. Test Login
```bash
curl -X POST https://tu-api-railway.up.railway.app/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'

# Esperado: 200
# {"access_token":"eyJ0eXAiOiJKV1QiLCJhbGc..."}
```

### 4. Monitorear Logs
```
En Railway Dashboard:
1. Tu proyecto → Deploy → Logs
2. Buscar errores
3. Revisar health check logs
```

---

## 🚨 SI ALGO FALLA

### Error: "Connection refused" a BD
```
Solución: Verificar que DATABASE_URL está correcta en Railway Variables
         Esperar 30s a que PostgreSQL esté listo
```

### Error: "JWT token is invalid"
```
Solución: Verificar JWT_SECRET_KEY está en Railway Variables
         DEBE coincidir exactamente con lo que generaste
```

### Error: "CORS error"
```
Solución: Actualizar CORS_ORIGINS en Railway Variables
         Incluir exactamente tu dominio frontend
         Ejemplo: https://miapp.vercel.app,https://www.miapp.vercel.app
```

### Error: "Internal Server Error"
```
Solución: Ver logs en Railway Dashboard
         Buscar la línea con el error
         Revisar si es problema de BD o aplicación
```

---

## 📊 ENDPOINTS FINALES RAILWAY

### Endpoints Públicos (sin JWT):
```
GET  /health                          → Verificar salud API
```

### Endpoints de Autenticación:
```
POST /users/register                  → Crear usuario
POST /users/login                     → Login (obtener JWT)
```

### Endpoints Admin (requiere JWT + is_admin=True):
```
POST /admin/model/upload              → Subir modelo PKL
DELETE /admin/model/<model_id>        → Eliminar modelo
```

### Endpoints Generales (requiere JWT):
```
GET  /models                          → Listar modelos
GET  /models/<model_id>/schema        → Obtener schema modelo
POST /predict/<model_id>              → Hacer predicción
```

---

## 🎯 FLUJO COMPLETO EN PRODUCCIÓN

```
1. Admin usuario se registra:
   POST /users/register {username, password}
   
2. Sistema promociona a admin (manual en BD o mediante endpoint futuro)
   
3. Admin sube modelo:
   POST /admin/model/upload
   [Headers: Authorization: Bearer {JWT}]
   [FormData: model_file, scaler_file, metadata]
   
4. Usuarios normales se registran:
   POST /users/register {username, password}
   
5. Usuarios login:
   POST /users/login {username, password}
   
6. Usuarios hacen predicciones:
   POST /predict/diabetes-v1 {Pregnancies, Glucose, ...}
   [Headers: Authorization: Bearer {JWT}]
```

---

## ✨ CONFIRMACIÓN FINAL

Antes de hacer `git push` definitivo:

```bash
# Verificar que todo está en orden
./curl_examples.sh  # Test local (asumiendo que tienes modelos PKL)

# O test manual en desarrollo:
python3 app.py

# En otra terminal:
curl http://localhost:5000/health
# {"status":"healthy",...}
```

---

## 📞 SOPORTE

Si todo falla:
1. Revisar logs en Railway Dashboard
2. Verificar variables de entorno exactas
3. Confirmar que PostgreSQL está UP
4. Esperar 30s a que dyno inicie completamente

**Listo para deployment.** 🚀
