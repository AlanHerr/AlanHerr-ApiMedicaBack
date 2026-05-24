import hashlib
import os
import joblib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / 'models'


def _ensure_models_dir():
    """Garantiza que el directorio de modelos existe antes de usarlo."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _convert_to_json_serializable(obj: Any) -> Any:
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _convert_to_json_serializable(v) for k, v in obj.items()}
    else:
        return obj


class ModelService:

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    @staticmethod
    def verify_file_hash(file_path: str, expected_hash: str, label: str) -> None:
        if not expected_hash:
            return
        calculated_hash = ModelService.compute_sha256(file_path)
        if calculated_hash.lower() != expected_hash.lower():
            raise ValueError(f"Hash SHA-256 inválido para {label}.")

    @staticmethod
    def load_serialized_model(file_path: str, expected_hash: Optional[str] = None) -> Any:
        if expected_hash:
            ModelService.verify_file_hash(file_path, expected_hash, 'archivo serializado')
        return joblib.load(file_path)

    @staticmethod
    def extract_metadata_from_model(model: Any) -> Dict[str, Any]:
        metadata = {}

        if isinstance(model, Pipeline):
            metadata['is_pipeline'] = True
            final_model = model.steps[-1][1]
        else:
            metadata['is_pipeline'] = False
            final_model = model

        metadata['model_type'] = final_model.__class__.__name__

        feature_names_raw = None

        if isinstance(model, Pipeline):
            if hasattr(model, 'feature_names_in_'):
                feature_names_raw = model.feature_names_in_
            else:
                first_step = model.steps[0][1]
                if hasattr(first_step, 'feature_names_in_'):
                    feature_names_raw = first_step.feature_names_in_

        if feature_names_raw is None and hasattr(final_model, 'feature_names_in_'):
            feature_names_raw = final_model.feature_names_in_

        metadata['feature_names'] = [str(f) for f in feature_names_raw] if feature_names_raw is not None else []

        metadata['n_features'] = (
            len(metadata['feature_names']) if metadata['feature_names']
            else getattr(final_model, 'n_features_in_', 0)
        )

        metadata['feature_types'] = ModelService._extract_feature_types(model, metadata)
        metadata['output_type'] = ModelService._detect_output_type(final_model)

        if hasattr(final_model, 'classes_'):
            metadata['classes'] = _convert_to_json_serializable(list(final_model.classes_))
        else:
            metadata['classes'] = None

        metadata['has_proba'] = hasattr(final_model, 'predict_proba')

        return metadata

    @staticmethod
    def _extract_feature_types(model: Any, metadata: Dict) -> list:
        feature_names = metadata.get('feature_names', [])
        if not feature_names:
            return []
        return ['float'] * len(feature_names)

    @staticmethod
    def _detect_output_type(model: Any) -> str:
        model_name = model.__class__.__name__
        if 'Classifier' in model_name or 'Decision' in model_name:
            return 'classification'
        elif 'Regressor' in model_name:
            return 'regression'
        else:
            return 'unknown'

    @staticmethod
    def save_model_files(
        model_file_path: str,
        scaler_file_path: Optional[str],
        model_id: str,
        is_pipeline: bool
    ) -> Tuple[str, Optional[str]]:
        # Siempre garantizar que el directorio existe antes de guardar
        _ensure_models_dir()

        model_final_name = f"{model_id}-model.pkl"
        scaler_final_name = f"{model_id}-scaler.pkl" if scaler_file_path else None

        model_final_path = MODELS_DIR / model_final_name
        scaler_final_path = MODELS_DIR / scaler_final_name if scaler_final_name else None

        try:
            with open(model_file_path, 'rb') as src:
                with open(model_final_path, 'wb') as dst:
                    dst.write(src.read())
            logger.info(f"Modelo guardado en: {model_final_path}")

            if scaler_file_path:
                with open(scaler_file_path, 'rb') as src:
                    with open(scaler_final_path, 'wb') as dst:
                        dst.write(src.read())
                logger.info(f"Scaler guardado en: {scaler_final_path}")
        except Exception as e:
            logger.error(f"Error guardando archivos: {e}")
            raise

        return (
            str(model_final_path),
            str(scaler_final_path) if scaler_final_path else None
        )

    @staticmethod
    def load_model_and_scaler(
        model_path: str,
        scaler_path: Optional[str] = None,
        is_pipeline: bool = False,
        expected_model_hash: Optional[str] = None,
        expected_scaler_hash: Optional[str] = None,
    ) -> Tuple[Any, Any]:
        try:
            model = ModelService.load_serialized_model(model_path, expected_model_hash)
            scaler = None
            if not is_pipeline and scaler_path:
                scaler = ModelService.load_serialized_model(scaler_path, expected_scaler_hash)
            return model, scaler
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise

    @staticmethod
    def validate_input_for_model(
        data: Dict[str, Any],
        feature_names: list,
        feature_types: list
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        errors = {}
        parsed = {}

        for feature_name in feature_names:
            if feature_name not in data:
                errors[feature_name] = 'Campo requerido'

        if errors:
            return {}, errors

        for i, feature_name in enumerate(feature_names):
            feature_type = feature_types[i] if i < len(feature_types) else 'float'
            value = data[feature_name]
            try:
                if feature_type == 'int':
                    parsed[feature_name] = int(value)
                elif feature_type == 'float':
                    parsed[feature_name] = float(value)
                else:
                    parsed[feature_name] = value
            except (ValueError, TypeError):
                errors[feature_name] = f'Debe ser de tipo {feature_type}'

        if errors:
            return {}, errors

        return parsed, {}