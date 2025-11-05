from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from service.diabetes_service import predict_and_store


diabetes_bp = Blueprint('diabetes', __name__)


@diabetes_bp.route('/predict/diabetes', methods=['POST'])
@jwt_required()
def predict_diabetes():
    payload = request.get_json(silent=True) or {}
    debug = request.args.get('debug') in ("1", "true", "True")
    result, errors = predict_and_store(payload, debug=debug)
    if errors:
        return jsonify({'errors': errors}), 422
    return jsonify(result), 200
