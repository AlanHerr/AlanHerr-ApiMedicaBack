import logging
import joblib
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from repository.model_metadata_repository import ModelMetadataRepository
from service.model_service import ModelService
from service.prediction_service import predict_and_store

logger = logging.getLogger(__name__)

predict_bp = Blueprint('predict', __name__)


@predict_bp.route('/predict/<model_id>', methods=['POST'])
@jwt_required()
def predict(model_id):
    """
    Endpoint genérico de predicción para cualquier modelo.
    
    Requiere:
    - JWT válido
    - model_id en la URL
    - Payload JSON con los features requeridos
    
    Query params:
    - debug=1 o debug=true para obtener información adicional
    """
    try:
        # Obtener metadata del modelo
        model_metadata = ModelMetadataRepository.get_by_model_id(model_id)
        if not model_metadata:
            return jsonify({'error': f'Modelo {model_id} no encontrado'}), 404
        
        if not model_metadata.is_active:
            return jsonify({'error': f'Modelo {model_id} no está activo'}), 410
        
        # Parsear payload
        payload = request.get_json(silent=True) or {}
        debug = request.args.get('debug') in ("1", "true", "True")
        
        # Cargar modelo y scaler
        try:
            model, scaler = ModelService.load_model_and_scaler(
                model_metadata.model_path,
                model_metadata.scaler_path,
                model_metadata.is_pipeline
            )
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return jsonify({'error': f'Error cargando modelo: {str(e)}'}), 500
        
        # Realizar predicción y almacenar
        result, errors = predict_and_store(
            model_metadata,
            model,
            scaler,
            payload,
            debug=debug
        )
        
        if errors:
            return jsonify({'errors': errors}), 422
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
