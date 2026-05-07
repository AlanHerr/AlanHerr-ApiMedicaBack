    # 🚀 API Médica Dinámica - Sistema de Modelos ML

API RESTful avanzada con Flask para predicción médica dinámica. Permite a profesionales subir modelos de Machine Learning (PKL) de forma segura, genera esquemas automáticamente, crea tablas de base de datos dinámicas y ejecuta predicciones con almacenamiento persistente. Soporta múltiples modelos simultáneamente con autenticación JWT y base de datos PostgreSQL (Railway).

---

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Stack Tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Configuración](#instalación-y-configuración)
- [Variables de Entorno](#variables-de-entorno)
- [Uso de la API](#uso-de-la-api)
- [Endpoints Principales](#endpoints-principales)
- [Formatos de Modelos Soportados](#formatos-de-modelos-soportados)
- [Base de Datos](#base-de-datos)
- [Despliegue](#despliegue)
- [Seguridad](#seguridad)
- [Troubleshooting](#troubleshooting)
- [Contribución](#contribución)
- [Licencia](#licencia)

---

## 🎯 Descripción General

Este sistema transforma una API estática de predicción de diabetes en una plataforma dinámica que permite:

- **Carga de Modelos**: Profesionales pueden subir modelos ML entrenados (PKL) vía endpoints seguros
- **Generación Automática de Esquemas**: Extrae metadatos del modelo para crear formularios dinámicos en el frontend
- **Tablas Dinámicas**: Crea automáticamente tablas de base de datos para almacenar predicciones por modelo
- **Predicciones Seguras**: Ejecuta predicciones con validación y almacenamiento persistente
- **Multi-Modelo**: Soporta múltiples modelos simultáneamente con aislamiento de datos

### Casos de Uso
- Plataformas médicas que necesitan actualizar modelos frecuentemente
- Profesionales de ML que despliegan modelos sin modificar el backend
- Sistemas de predicción con múltiples especialidades médicas

---

## 🛠️ Stack Tecnológico

- **Framework Web**: Flask 3.x con Blueprints modulares
- **Autenticación**: Flask-JWT-Extended (tokens JWT)
- **ORM**: SQLAlchemy 2.x con soporte PostgreSQL
- **Machine Learning**: scikit-learn, joblib para serialización PKL
- **Base de Datos**: PostgreSQL (Railway) con fallback a SQLite
- **Servidor WSGI**: Gunicorn
- **Procesamiento de Datos**: NumPy, Pandas
- **Validación**: Marshmallow para esquemas dinámicos
- **CORS**: Flask-CORS para integración frontend

---

## 🏗️ Arquitectura

El sistema sigue una arquitectura limpia con separación de responsabilidades:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controller    │───▶│    Service      │───▶│  Repository     │
│   (Endpoints)   │    │  (Lógica de     │    │  (Acceso a BD)  │
│                 │    │   Negocio)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Model         │    │   PKL Files     │    │   Database       │
│   (ORM)         │    │   (Storage)     │    │   (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

- **Controller Layer**: Maneja requests HTTP, validación de entrada, respuestas JSON
- **Service Layer**: Contiene lógica de negocio, carga de modelos, ejecución de predicciones
- **Repository Layer**: Abstracción de acceso a datos, operaciones CRUD
- **Model Layer**: Definiciones ORM SQLAlchemy para tablas estáticas y dinámicas

---

## 📁 Estructura del Proyecto

```
AlanHerr-ApiMedicaBack/
├── app.py                          # Aplicación Flask principal
├── main.py                         # Alias WSGI alternativo
├── Procfile                        # Configuración Gunicorn
├── requirements.txt                # Dependencias Python
├── API_GUIDE.md                    # Guía completa de la API
├── README.md                       # Este archivo
├── curl_examples.sh                # Scripts de ejemplo con curl
├── config/
│   └── database.py                 # Configuración BD SQLAlchemy
├── controller/
│   ├── __init__.py
│   ├── user_controller.py          # Auth: register/login
│   ├── model_controller.py         # Admin: upload/list modelos
│   └── predict_controller.py       # Predictions genéricas
├── model/
│   ├── __init__.py
│   ├── base.py                     # Base declarativa SQLAlchemy
│   ├── user.py                     # Tabla usuarios (con is_admin)
│   ├── model_metadata.py           # Metadatos de modelos ML
│   └── diabetes.py                 # Tabla legacy (opcional)
├── repository/
│   ├── __init__.py
│   ├── user_repository.py          # CRUD usuarios
│   └── model_metadata_repository.py # CRUD metadatos modelos
├── service/
│   ├── __init__.py
│   ├── user_service.py             # Lógica auth
│   ├── model_service.py            # Carga y extracción PKL
│   └── prediction_service.py       # Predicciones dinámicas
└── models/                         # Directorio para archivos PKL
    ├── .gitkeep                    # Mantener directorio en git
    └── [model_id]/
        ├── model.pkl
        └── scaler.pkl (opcional)
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/AlanHerr/AlanHerr-ApiMedicaBack.git
cd AlanHerr-ApiMedicaBack
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto (ver sección [Variables de Entorno](#variables-de-entorno))

### 5. Ejecutar en Desarrollo
```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

---

## 🔧 Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db

# JWT
JWT_SECRET_KEY=tu_clave_secreta_muy_segura_aqui

# CORS (opcional)
CORS_ORIGINS=https://tu-frontend.vercel.app,https://otro-dominio.com

# Puerto (opcional, default 5000)
PORT=5000
```

### Notas sobre Base de Datos
- **PostgreSQL (Recomendado)**: Usa Railway u otro proveedor cloud
- **SQLite (Desarrollo)**: Si `DATABASE_URL` falla, automáticamente usa `sqlite:///medical_local.db`
- **SSL**: Para Railway, agrega `?sslmode=require` a la URL si es necesario

---

## 📖 Uso de la API

### Flujo Típico de Uso

1. **Registro/Login**: Crear cuenta de usuario (admin para subir modelos)
2. **Subir Modelo**: Admin carga modelo PKL con metadatos
3. **Listar Modelos**: Ver modelos disponibles
4. **Obtener Schema**: Frontend obtiene esquema dinámico para formularios
5. **Hacer Predicción**: Usuario envía datos y recibe predicción almacenada

### Autenticación
- Usa JWT tokens para endpoints protegidos
- Usuarios normales: solo predicciones
- Admins: pueden subir modelos

Ver [API_GUIDE.md](API_GUIDE.md) para ejemplos completos con curl.

---

## 🔗 Endpoints Principales

### Autenticación
- `POST /users/register` - Registro de usuario
- `POST /users/login` - Login y obtención de JWT

### Gestión de Modelos (Admin)
- `POST /admin/model/upload` - Subir modelo PKL
- `GET /models` - Listar modelos disponibles
- `GET /models/{id}/schema` - Obtener esquema para frontend

### Predicciones
- `POST /predict/{model_id}` - Ejecutar predicción

### Documentación Detallada
Para payloads, respuestas y ejemplos completos, consulta [API_GUIDE.md](API_GUIDE.md)

---

## 🤖 Formatos de Modelos Soportados

### ✅ Pipeline Completo (Recomendado)
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])
pipeline.fit(X_train, y_train)
joblib.dump(pipeline, 'model.pkl')
```

### ✅ Modelo + Scaler Separados
```python
# Scaler
scaler = StandardScaler()
scaler.fit(X_train)
joblib.dump(scaler, 'scaler.pkl')

# Modelo
model = RandomForestClassifier()
model.fit(scaler.transform(X_train), y_train)
joblib.dump(model, 'model.pkl')
```

### Requisitos
- **Librerías**: scikit-learn, joblib
- **Tipos**: Clasificadores binarios o regresión
- **Features**: Nombres de features accesibles vía `feature_names_in_` o proporcionados en metadatos

---

## 🗄️ Base de Datos

### Tablas Estáticas
- `users`: id, username, password_hash, is_admin, created_at
- `model_metadata`: id, model_id, name, version, description, model_type, n_features, output_type, created_at, file_path

### Tablas Dinámicas
Por cada modelo, se crea automáticamente:
- `{model_id}_predictions`: Campos de input + prediction, probability, created_at

### Compatibilidad
- PostgreSQL: Producción (Railway)
- SQLite: Desarrollo local (fallback automático)

---

## 🚢 Despliegue

### Railway (Recomendado)
1. Conectar repositorio GitHub
2. Variables de entorno: `DATABASE_URL`, `JWT_SECRET_KEY`
3. Puerto: Railway asigna automáticamente
4. Comando: `web: gunicorn app:app`

### Otros Proveedores
- **Heroku**: Similar a Railway, usa `Procfile`
- **Vercel**: Para serverless, adaptar a funciones
- **Docker**: Crear Dockerfile con Python 3.8+ y requirements.txt

---

## 🔒 Seguridad

### Autenticación
- JWT tokens con expiración
- Passwords hasheadas con Werkzeug
- Roles: usuario normal vs admin

### Validación
- Entrada sanitizada
- Validación de tipos de datos
- Límites en tamaños de archivos PKL

### Mejores Prácticas
- No subir `.env` al repositorio
- Usar HTTPS en producción
- Rotar JWT_SECRET_KEY periódicamente
- Rate limiting recomendado para producción

---

## 🐛 Troubleshooting

### Errores Comunes

**"No module named 'psycopg'"**
- Instalar: `pip install psycopg[binary]`
- Verificar requirements.txt

**"Connection failed"**
- Verificar DATABASE_URL
- Agregar `?sslmode=require` para Railway

**"Model loading failed"**
- Verificar formato PKL (joblib/scikit-learn)
- Revisar dependencias del modelo

**JWT Errors**
- Verificar token no expirado
- Header: `Authorization: Bearer <token>`

### Logs
- Desarrollo: Flask muestra logs detallados
- Producción: Configurar logging a archivo o servicio externo

---

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Guías de Código
- PEP 8 para Python
- Docstrings en funciones públicas
- Tests unitarios para nuevas funcionalidades

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para detalles.

---

**Autor**: AlanHerr  
**Versión**: 2.0 - Sistema Dinámico  
**Fecha**: Abril 2026
