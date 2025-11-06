
# 0. Registrar usuario y obtener token
curl -i -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario1", "password": "12345"}'

TOKEN=$(curl -s -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario1", "password": "12345"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 1. Predicción de diabetes (PROTEGIDA)
curl -i -X POST http://localhost:5000/predict/diabetes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
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



BASE="https://alanherr-apimedicaback-production.up.railway.app"

curl -sS -X POST "$BASE/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "Demo1234!"
  }'

TOKEN=$(curl -sS -X POST "$BASE/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "Demo1234!"
  }' | jq -r '.access_token')
echo "TOKEN=$TOKEN"


curl -sS -X POST "$BASE/predict/diabetes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Pregnancies": 7,
    "Glucose": 170,
    "BloodPressure": 100,
    "SkinThickness": 40.0,
    "Insulin": 350,
    "BMI": 42,
    "DiabetesPedigreeFunction": 1.3,
    "Age": 60
  }'