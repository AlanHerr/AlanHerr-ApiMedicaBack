# Alias para plataformas que esperan `main:app`
from app import app as application
# También exponemos `app` para compatibilidad con `main:app` o `app:app`
app = application
