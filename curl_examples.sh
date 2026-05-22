#!/usr/bin/env bash

# Ejecuta este script directamente con: bash curl_examples.sh
# Usa rutas absolutas internas para localizar los archivos en models/.
set -euo pipefail
IFS=$'\n\t'

BASE_LOCAL="http://localhost:5000"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
MODEL_ID="diabetes-v1"
MODEL_FILE="$SCRIPT_DIR/models/${MODEL_ID}-model.pkl"
SCALER_FILE="$SCRIPT_DIR/models/${MODEL_ID}-scaler.pkl"
ADMIN_USER="admin_test"
ADMIN_PASS="AdminPass123!"
NORMAL_USER="regular_user"
NORMAL_PASS="pass123"



printf "=== 0. Crear/promover usuario admin en BD ===\n"
python3 << 'EOF'
import os
import sys
sys.path.insert(0, os.getcwd())
from config.database import get_db_session
from model.user import User
from werkzeug.security import generate_password_hash

session = get_db_session()
try:
    admin = session.query(User).filter_by(username="admin_test").first()
    if not admin:
        admin = User(username="admin_test", password=generate_password_hash("AdminPass123!"), is_admin=True)
        session.add(admin)
        session.commit()
        print("✓ Usuario admin_test creado.")
    else:
        admin.is_admin = True
        session.commit()
        print("✓ Usuario admin_test promovido a admin.")
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    session.close()
EOF

printf "\n=== 1. Crear usuario normal en BD ===\n"
python3 << 'EOF'
import os
import sys
sys.path.insert(0, os.getcwd())
from config.database import get_db_session
from model.user import User
from werkzeug.security import generate_password_hash

session = get_db_session()
try:
    normal = session.query(User).filter_by(username="regular_user").first()
    if not normal:
        normal = User(username="regular_user", password=generate_password_hash("pass123"), is_admin=False)
        session.add(normal)
        session.commit()
        print("✓ Usuario regular_user creado.")
    else:
        print("✓ Usuario regular_user ya existe.")
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    session.close()
EOF

printf "\n=== 2. Login con usuario admin ===\n"
TOKEN=$(curl -sS -X POST "$BASE_LOCAL/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$ADMIN_USER\", \"password\": \"$ADMIN_PASS\"}" 2>/dev/null | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("access_token", ""))' 2>/dev/null || echo "")
if [[ -z "$TOKEN" ]]; then
  printf "✗ No se pudo obtener token para admin. Revisa el servidor y las credenciales.\n"
  exit 1
fi
printf "TOKEN=%s\n" "$TOKEN"

printf "\n=== 3. Subir modelo PKL (como admin) ===\n"
if [[ -f "$MODEL_FILE" && -f "$SCALER_FILE" ]]; then
  curl -sS -X POST "$BASE_LOCAL/admin/model/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "model_file=@$MODEL_FILE" \
    -F "scaler_file=@$SCALER_FILE" \
    -F 'metadata={"name":"Diabetes v1","model_id":"diabetes-v1","version":"1.0","description":"Predice diabetes","feature_names":["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"],"threshold":0.5}' || true
else
  printf "✗ No se encontró el archivo de modelo en %s o %s\n" "$MODEL_FILE" "$SCALER_FILE"
fi

printf "\n=== 4. Login con usuario normal ===\n"
NORMAL_TOKEN=$(curl -sS -X POST "$BASE_LOCAL/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$NORMAL_USER\", \"password\": \"$NORMAL_PASS\"}" 2>/dev/null | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("access_token", ""))' 2>/dev/null || echo "")
if [[ -z "$NORMAL_TOKEN" ]]; then
  printf "✗ No se pudo obtener token para usuario normal. Revisa las credenciales o el endpoint.\n"
fi
printf "NORMAL_TOKEN=%s\n" "$NORMAL_TOKEN"

printf "\n=== 5. Intentar subir modelo con usuario normal (debe fallar) ===\n"
if [[ -n "$NORMAL_TOKEN" ]]; then
  curl -sS -X POST "$BASE_LOCAL/admin/model/upload" \
    -H "Authorization: Bearer $NORMAL_TOKEN" \
    -F "model_file=@/dev/null" || true
else
  printf "✗ No se pudo obtener token para usuario normal. Revisa credenciales.\n"
fi

printf "\n=== 6. Listar modelos disponibles ===\n"
set +e
curl -sS -w "\nHTTP_STATUS:%{http_code}\n" -X GET "$BASE_LOCAL/models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" || true
set -e

printf "\n=== 7. Predicción de diabetes-v1 ===\n"
set +e
curl -sS -w "\nHTTP_STATUS:%{http_code}\n" -X POST "$BASE_LOCAL/predict/$MODEL_ID" \
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
      }' || true
set -e

printf "\n=== FIN de las pruebas curl ===\n"
