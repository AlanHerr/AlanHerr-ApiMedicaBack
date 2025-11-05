from typing import Tuple, Dict, Any, List
import os

import numpy as np
import pandas as pd

from repository.diabetes_repository import create_diabetes_prediction
from service.diabetes_model import get_scaler, get_model


REQUIRED_FIELDS = [
    'Pregnancies',
    'Glucose',
    'BloodPressure',
    'SkinThickness',
    'Insulin',
    'BMI',
    'DiabetesPedigreeFunction',
    'Age',
]


def _normalize_keys(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Aceptar llaves en minúsculas o camel, normalizando a las previstas
    mapping = {
        'pregnancies': 'Pregnancies',
        'glucose': 'Glucose',
        'bloodpressure': 'BloodPressure',
        'blood_pressure': 'BloodPressure',
        'skinthickness': 'SkinThickness',
        'skin_thickness': 'SkinThickness',
        'insulin': 'Insulin',
        'bmi': 'BMI',
        'diabetespedigreefunction': 'DiabetesPedigreeFunction',
        'diabetes_pedigree_function': 'DiabetesPedigreeFunction',
        'age': 'Age',
    }
    out = {}
    for k, v in payload.items():
        key_norm = k
        lk = k.lower()
        if lk in mapping:
            key_norm = mapping[lk]
        out[key_norm] = v
    return out


def validate_and_parse(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    errors = {}
    data = _normalize_keys(payload or {})

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors[field] = 'Campo requerido'

    if errors:
        return {}, errors

    # Tipos esperados
    parsed = {}
    int_fields = {'Pregnancies', 'Age'}
    float_fields = {
        'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction'
    }

    for f in int_fields:
        try:
            parsed[f] = int(data[f])
        except Exception:
            errors[f] = 'Debe ser entero'

    for f in float_fields:
        try:
            parsed[f] = float(data[f])
        except Exception:
            errors[f] = 'Debe ser número (float)'

    # Validaciones básicas
    if 'Pregnancies' in parsed and parsed['Pregnancies'] < 0:
        errors['Pregnancies'] = 'No puede ser negativa'
    if 'Age' in parsed and parsed['Age'] <= 0:
        errors['Age'] = 'Debe ser mayor a 0'
    if 'BMI' in parsed and parsed['BMI'] <= 0:
        errors['BMI'] = 'Debe ser mayor a 0'

    if errors:
        return {}, errors

    return parsed, {}


def predict_and_store(payload: Dict[str, Any], debug: bool = False) -> Tuple[Dict[str, Any], Dict[str, str]]:
    parsed, errors = validate_and_parse(payload)
    if errors:
        return {}, errors

    # Descubrir nombres de features esperados por los artefactos
    scaler = get_scaler()
    model = get_model()

    def _norm(s: str) -> str:
        return s.replace('_', '').lower()

    default_order: List[str] = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ]
    fn = getattr(scaler, 'feature_names_in_', None)
    if fn is not None:
        expected_names = list(fn)
    else:
        expected_names = list(default_order)

    # Mapear parsed -> orden esperado por el scaler/modelo usando normalización de nombres
    parsed_by_norm = {_norm(k): parsed[k] for k in parsed}
    row = []
    missing = []
    for name in expected_names:
        keyn = _norm(name)
        if keyn not in parsed_by_norm:
            missing.append(name)
            row.append(np.nan)
        else:
            row.append(parsed_by_norm[keyn])

    # Crear DataFrame con nombres esperados para evitar warnings y asegurar alineación
    x_df = pd.DataFrame([row], columns=expected_names)

    # Transformar y predecir
    x_scaled = scaler.transform(x_df)
    # Mantener nombres para el modelo si los requiere
    x_scaled_df = pd.DataFrame(x_scaled, columns=expected_names)
    y_pred = model.predict(x_scaled_df)
    pred = int(y_pred[0])

    proba = None
    if hasattr(model, 'predict_proba'):
        try:
            p = model.predict_proba(x_scaled_df)
            if p.ndim == 2 and p.shape[1] >= 2:
                proba = float(p[0, 1])
        except Exception:
            proba = None

    # Guardar en BD
    entry = {
        'pregnancies': parsed['Pregnancies'],
        'glucose': parsed['Glucose'],
        'blood_pressure': parsed['BloodPressure'],
        'skin_thickness': parsed['SkinThickness'],
        'insulin': parsed['Insulin'],
        'bmi': parsed['BMI'],
        'diabetes_pedigree_function': parsed['DiabetesPedigreeFunction'],
        'age': parsed['Age'],
        'predicted': pred,
        'probability': proba,
    }
    record = create_diabetes_prediction(entry)

    threshold = float(os.getenv('DIABETES_THRESHOLD', '0.5'))

    result: Dict[str, Any] = {
        'id': record.id,
        'prediction': pred,
        'probability': proba,
        'positive': (proba is not None and proba >= threshold),
        'threshold': threshold,
    }

    if debug:
        # Calcular z-scores con estadísticas del scaler (si disponibles)
        mean = getattr(scaler, 'mean_', None)
        scale = getattr(scaler, 'scale_', None)
        zscores = None
        if mean is not None and scale is not None:
            try:
                z = (x_df.values[0] - mean) / scale
                zscores = {name: float(z[i]) for i, name in enumerate(expected_names)}
            except Exception:
                zscores = None

        # Información del árbol (si aplica)
        leaf_id = None
        try:
            leaf_id = int(model.apply(x_scaled_df)[0])
        except Exception:
            leaf_id = None

        importances = getattr(model, 'feature_importances_', None)
        top_importances = None
        if importances is not None:
            top_importances = {expected_names[i]: float(v) for i, v in enumerate(importances)}

        result['debug'] = {
            'expected_feature_order': expected_names,
            'zscores': zscores,
            'leaf_id': leaf_id,
            'feature_importances': top_importances,
        }
    return result, {}
