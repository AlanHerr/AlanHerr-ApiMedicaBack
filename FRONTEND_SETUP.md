# 🚀 Setup Recomendado para Frontend

## Stack Recomendado

```
Frontend: React 18 + Vite
UI: TailwindCSS o Material-UI
State: React Context + hooks (o Redux si es grande)
HTTP: Fetch API o Axios
```

---

## Crear Proyecto React + Vite

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios react-router-dom
```

---

## Estructura de Carpetas

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── ModelList.jsx
│   │   ├── PredictForm.jsx
│   │   ├── ModelUpload.jsx
│   │   └── Dashboard.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── PredictPage.jsx
│   │   └── AdminPage.jsx
│   ├── services/
│   │   └── api.js
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── .env.local
├── .env.production
├── vite.config.js
├── package.json
└── README.md
```

---

## Archivos Base

### `src/context/AuthContext.jsx`

```javascript
import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }, [token]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/users/login`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        }
      );
      if (!res.ok) throw new Error('Login failed');
      const data = await res.json();
      setToken(data.access_token);
      setUser({ username });
      return data;
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, password) => {
    setLoading(true);
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/users/register`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        }
      );
      if (!res.ok) throw new Error('Registration failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
```

### `src/services/api.js`

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const getHeaders = (token) => ({
  'Content-Type': 'application/json',
  ...(token && { 'Authorization': `Bearer ${token}` }),
});

export const api = {
  // Models
  listModels: async () => {
    const res = await fetch(`${API_URL}/models`);
    if (!res.ok) throw new Error('Failed to list models');
    return res.json();
  },

  getModelSchema: async (modelId) => {
    const res = await fetch(`${API_URL}/models/${modelId}/schema`);
    if (!res.ok) throw new Error('Failed to get schema');
    return res.json();
  },

  // Predictions
  predict: async (modelId, data, token) => {
    const res = await fetch(`${API_URL}/predict/${modelId}`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Prediction failed');
    return res.json();
  },

  // Admin: Upload
  uploadModel: async (files, metadata, token) => {
    const formData = new FormData();
    formData.append('model_file', files.model);
    if (files.scaler) formData.append('scaler_file', files.scaler);
    formData.append('metadata', JSON.stringify(metadata));

    const res = await fetch(`${API_URL}/admin/model/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },

  // Admin: Delete
  deleteModel: async (modelId, token) => {
    const res = await fetch(`${API_URL}/admin/model/${modelId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Delete failed');
    return res.status === 204;
  },
};
```

### `.env.local`

```
VITE_API_URL=http://localhost:5000
```

### `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

---

## GitHub Setup

### 1. Crear repositorio
```bash
git init
git add .
git commit -m "Initial commit: frontend scaffolding"
git remote add origin https://github.com/AlanHerr/AlanHerr-ApiFrontend.git
git branch -M main
git push -u origin main
```

### 2. Crear rama development
```bash
git checkout -b development
git push -u origin development
```

---

## Flujo de Desarrollo

```bash
# Local: backend en puerto 5000
npm run dev  # frontend en puerto 3000

# .env.local apuntará a http://localhost:5000
```

---

## Scripts en package.json

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src"
  }
}
```

---

## Checklist

- [ ] Crear repo en GitHub
- [ ] `npm create vite` con template React
- [ ] Instalar dependencias (axios, react-router, etc)
- [ ] Crear estructura de carpetas
- [ ] Implementar AuthContext
- [ ] Implementar servicios API
- [ ] Componente Login/Register
- [ ] Página de predicción
- [ ] Página de admin (upload)
- [ ] Routing con react-router
- [ ] Deploy a Vercel/Netlify

---

## Comandos Útiles

```bash
# Iniciar frontend
npm run dev

# Build para producción
npm run build

# Deployar a Vercel (necesita CLI)
npm i -g vercel
vercel

# Ver variables de entorno
cat .env.local
```

---

## Notas

- El backend está en `development` branch de AlanHerr-ApiMedicaBack
- Frontend también debería usar rama `development`
- Cuando backend esté en producción, actualizar `VITE_API_URL` en `.env.production`
