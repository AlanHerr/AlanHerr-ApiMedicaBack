import joblib
import logging
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
from config.database import get_db_session, engine
from sqlalchemy import Column, Integer, Float, DateTime, text
from sqlalchemy.orm import declarative_base
from datetime import datetime
from service.model_service import ModelService

logger = logging.getLogger(__name__)


def _sanitize_table_name(name: str) -> str:
    """
    Sanitiza un nombre para que sea válido en SQL.
    Reemplaza guiones y caracteres especiales con guiones bajos.
    """
    return name.replace('-', '_').replace(' ', '_').replace('.', '_')


def _get_or_create_predictions_table(model_id: str, feature_names: list, feature_types: list):
    """
    Crea dinámicamente la tabla de predicciones para un modelo si no existe.
    
    Estructura:
    {model_id}_predictions (
        id INT PRIMARY KEY,
        feature1 FLOAT,
        feature2 INT,
        ...,
        predicted INT/FLOAT,
        probability FLOAT,
        created_at TIMESTAMP
    )
    """
    # Sanitizar el model_id para que sea válido como nombre de tabla
    sanitized_id = _sanitize_table_name(model_id)
    table_name = f"{sanitized_id}_predictions"
    
    session = get_db_session()
    try:
        # Verificar si tabla ya existe
        inspector_result = engine.execute(
            text(f"SELECT 1 FROM {table_name} LIMIT 1")
        )
        logger.info(f"Tabla {table_name} ya existe.")
        return table_name
    except Exception:
        # Tabla no existe, crearla
        pass
    
    try:
        # Construir SQL dinámico adaptado a PostgreSQL, MySQL y SQLite
        columns = []
        
        # Detectar el tipo de BD
        db_url = str(engine.url)
        if 'postgresql' in db_url or 'postgres' in db_url:
            # PostgreSQL
            columns.append("id SERIAL PRIMARY KEY")
        elif 'sqlite' in db_url:
            # SQLite
            columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            # MySQL y otros (por defecto)
            columns.append("id INTEGER PRIMARY KEY AUTO_INCREMENT")
        
        # Agregar columnas para cada feature
        for i, feature_name in enumerate(feature_names):
            feature_type = feature_types[i] if i < len(feature_types) else 'float'
            sql_type = 'INTEGER' if feature_type == 'int' else 'FLOAT'
            columns.append(f"{feature_name} {sql_type}")
        
        # Columnas de resultado
        columns.append("predicted INTEGER")
        columns.append("probability FLOAT")
        columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        
        session.execute(text(create_sql))
        session.commit()
        logger.info(f"Tabla {table_name} creada exitosamente.")
        return table_name
    except Exception as e:
        logger.error(f"Error creando tabla {table_name}: {e}")
        raise
    finally:
        session.close()


def predict_and_store(
    model_metadata,
    model,
    scaler,
    payload: Dict[str, Any],
    debug: bool = False
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Realiza predicción con un modelo genérico y almacena el resultado.
    
    Args:
        model_metadata: Registro de ModelMetadata
        model: Modelo cargado
        scaler: Scaler cargado (None si es Pipeline)
        payload: Datos de entrada del usuario
        debug: Si incluir información de debug
    
    Returns:
        Tuple(result_dict, errors_dict)
    """
    
    # Validar entrada
    parsed_data, errors = ModelService.validate_input_for_model(
        payload,
        model_metadata.feature_names,
        model_metadata.feature_types
    )
    
    if errors:
        return {}, errors
    
    # Preparar datos para predicción
    try:
        # Crear DataFrame con orden correcto
        row = [parsed_data[fname] for fname in model_metadata.feature_names]
        x_df = pd.DataFrame([row], columns=model_metadata.feature_names)
        
        # Escalar
        if model_metadata.is_pipeline:
            # Si es pipeline, incluye escalado internamente
            x_scaled = model.named_steps['scaler'].transform(x_df)
            # El modelo espera datos escalados
            x_pred = x_scaled
        else:
            if scaler:
                x_scaled = scaler.transform(x_df)
                x_pred = x_scaled
            else:
                x_pred = x_df.values
        
        # Convertir a DataFrame si es necesario (algunos modelos lo requieren)
        if not isinstance(x_pred, pd.DataFrame):
            x_pred = pd.DataFrame(x_pred, columns=model_metadata.feature_names)
        
        # Predicción
        y_pred = model.predict(x_pred)
        pred = int(y_pred[0]) if model_metadata.output_type == 'classification' else float(y_pred[0])
        
        # Probabilidad
        proba = None
        if model_metadata.has_proba and hasattr(model, 'predict_proba'):
            try:
                p = model.predict_proba(x_pred)
                if p.ndim == 2 and p.shape[1] >= 2:
                    proba = float(p[0, 1])  # Probabilidad de la clase positiva
            except Exception as e:
                logger.warning(f"No se pudo calcular probabilidad: {e}")
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return {}, {'prediction': f'Error en predicción: {str(e)}'}
    
    # Almacenar en BD
    try:
        # Asegurar que tabla existe
        table_name = _get_or_create_predictions_table(
            model_metadata.model_id,
            model_metadata.feature_names,
            model_metadata.feature_types
        )
        
        # Insertar resultado
        session = get_db_session()
        insert_data = {**parsed_data, 'predicted': pred, 'probability': proba}
        
        # Construir INSERT seguro
        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join([':' + k for k in insert_data.keys()])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        result = session.execute(text(insert_sql), insert_data)
        session.commit()
        
        # Obtener ID del registro insertado (compatible con PostgreSQL, MySQL, SQLite)
        db_url = str(engine.url)
        if 'postgresql' in db_url or 'postgres' in db_url:
            # PostgreSQL
            result_id = session.execute(text(f"SELECT currval(pg_get_serial_sequence('{table_name}', 'id'))")).scalar()
        else:
            # SQLite y MySQL
            result_id = session.execute(text(f"SELECT last_insert_rowid()")).scalar()
        
        session.close()
        
    except Exception as e:
        logger.error(f"Error almacenando predicción: {e}")
        return {}, {'storage': f'Error almacenando predicción: {str(e)}'}
    
    # Construir respuesta
    threshold = float(model_metadata.metadata_json.get('threshold', 0.5)) if model_metadata.metadata_json else 0.5
    
    result = {
        'id': result_id,
        'model_id': model_metadata.model_id,
        'prediction': pred,
        'probability': proba,
        'positive': proba is not None and proba >= threshold if proba is not None else None,
        'threshold': threshold,
        'created_at': datetime.utcnow().isoformat(),
    }
    
    if debug:
        result['debug'] = {
            'expected_feature_order': model_metadata.feature_names,
            'model_type': model_metadata.model_type,
            'is_pipeline': model_metadata.is_pipeline,
        }
    
    return result, {}
