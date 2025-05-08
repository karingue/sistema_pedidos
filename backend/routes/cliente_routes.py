from flask import Blueprint, jsonify, request
from utils.validators import validate_email, validate_cpf, ofAge
from database import get_connection



cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    