import os
import joblib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / 'models'
MODELS_DIR.mkdir(exist_ok=True)


def _convert_to_json_serializable(obj: Any) -> Any:
    """
    Convierte tipos de NumPy a tipos Python nativos JSON-serializables.
    """
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
    """Servicio para cargar, validar y extraer metadata de modelos PKL."""

    @staticmethod
    def extract_metadata_from_model(model: Any) -> Dict[str, Any]:
        """
        Extrae metadata de un modelo cargado.
        Soporta: Pipeline completo, modelos individuales (DecisionTree, LogisticRegression, etc.)
        
        Returns:
            Dict con: model_type, feature_names, feature_types, output_type, classes, has_proba
        """
        metadata = {}
        
        # Si es Pipeline, extraemos el modelo y scaler
        if isinstance(model, Pipeline):
            metadata['is_pipeline'] = True
            # El último paso contiene el modelo
            final_model = model.steps[-1][1]
        else:
            metadata['is_pipeline'] = False
            final_model = model
        
        # Tipo de modelo
        metadata['model_type'] = final_model.__class__.__name__
        
        # Features esperadas
        if hasattr(final_model, 'feature_names_in_'):
            # Convertir a lista de strings y asegurar JSON-serializable
            feature_names = [str(f) for f in final_model.feature_names_in_]
            metadata['feature_names'] = feature_names
        else:
            metadata['feature_names'] = []
        
        metadata['n_features'] = (
            len(metadata['feature_names']) if metadata['feature_names'] 
            else getattr(final_model, 'n_features_in_', 0)
        )
        
        # Tipos de features (si el scaler lo guarda)
        metadata['feature_types'] = ModelService._extract_feature_types(model, metadata)
        
        # Tipo de salida (clasificación, regresión, etc.)
        metadata['output_type'] = ModelService._detect_output_type(final_model)
        
        # Clases (si es clasificador)
        if hasattr(final_model, 'classes_'):
            # Convertir clases a tipos Python nativos
            classes = _convert_to_json_serializable(list(final_model.classes_))
            metadata['classes'] = classes
        else:
            metadata['classes'] = None
        
        # ¿Puede dar probabilidades?
        metadata['has_proba'] = hasattr(final_model, 'predict_proba')
        
        return metadata

    @staticmethod
    def _extract_feature_types(model: Any, metadata: Dict) -> list:
        """
        Intenta extraer tipos de features. Por defecto, supone float.
        """
        feature_names = metadata.get('feature_names', [])
        if not feature_names:
            return []
        
        # Por defecto, float para todo (excepto si hay info en scaler)
        feature_types = ['float'] * len(feature_names)
        
        # Si es Pipeline, checa el scaler
        if isinstance(model, Pipeline):
            for step_name, step in model.steps:
                if hasattr(step, 'feature_names_in_'):
                    # El scaler tiene info
                    break
        
        # Nota: scikit-learn no guarda tipos explícitamente,
        # así que estos son defaults. El usuario puede especificar.
        return feature_types

    @staticmethod
    def _detect_output_type(model: Any) -> str:
        """Detecta si es clasificador o regresor."""
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
        """
        Guarda los archivos PKL en la carpeta /models/ con nombres consistentes.
        
        Args:
            model_file_path: Ruta temporal del archivo modelo
            scaler_file_path: Ruta temporal del archivo scaler (opcional)
            model_id: ID del modelo (ej: "diabetes-v1")
            is_pipeline: Si es Pipeline completo
        
        Returns:
            Tuple(model_final_path, scaler_final_path)
        """
        # Nombres finales
        model_final_name = f"{model_id}-model.pkl"
        scaler_final_name = f"{model_id}-scaler.pkl" if scaler_file_path else None
        
        model_final_path = MODELS_DIR / model_final_name
        scaler_final_path = MODELS_DIR / scaler_final_name if scaler_final_name else None
        
        # Copiar/mover archivos
        try:
            # El modelo
            with open(model_file_path, 'rb') as src:
                with open(model_final_path, 'wb') as dst:
                    dst.write(src.read())
            logger.info(f"Modelo guardado en: {model_final_path}")
            
            # El scaler si existe
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
        is_pipeline: bool = False
    ) -> Tuple[Any, Any]:
        """
        Carga el modelo y scaler del disco.
        
        Returns:
            Tuple(model, scaler)
        """
        try:
            model = joblib.load(model_path)
            scaler = None
            
            if is_pipeline:
                # Si es Pipeline, el scaler está incluido
                scaler = None
            elif scaler_path:
                scaler = joblib.load(scaler_path)
            
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
        """
        Valida que los datos de entrada sean válidos para el modelo.
        
        Returns:
            Tuple(parsed_data, errors)
        """
        errors = {}
        parsed = {}
        
        # Validar que estén todos los features
        for feature_name in feature_names:
            if feature_name not in data:
                errors[feature_name] = 'Campo requerido'
        
        if errors:
            return {}, errors
        
        # Parsear types
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
