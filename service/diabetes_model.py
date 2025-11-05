from pathlib import Path
from typing import Optional

import numpy as np  # noqa: F401

try:
    import joblib
except Exception as e:  # pragma: no cover
    joblib = None


_SCALER = None
_MODEL = None


def _load_joblib(path: Path):
    if joblib is None:
        raise RuntimeError("joblib no está disponible para cargar modelos")
    return joblib.load(path)


def get_scaler() -> object:
    global _SCALER
    if _SCALER is None:
        scaler_path = Path(__file__).resolve().parents[1] / 'model' / 'scaler.pkl'
        _SCALER = _load_joblib(scaler_path)
    return _SCALER


def get_model() -> object:
    global _MODEL
    if _MODEL is None:
        model_path = Path(__file__).resolve().parents[1] / 'model' / 'modelo_arbol_de_decision.pkl'
        _MODEL = _load_joblib(model_path)
    return _MODEL
