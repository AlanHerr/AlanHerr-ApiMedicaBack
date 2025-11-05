
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
