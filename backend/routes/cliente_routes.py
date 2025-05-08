from flask import Blueprint, jsonify, request
from utils.validators import validate_email, validate_cpf, ofAge
from database import get_connection



cliente_bp = Blueprint('cliente', __name__)
@cliente_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    cpf = dados.get('cpf')
    data_nasc = dados.get('data_nascimento')
    endereco = dados.get('endereco')


    #Criação da Validação dos dados

    if not validate_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    if not validate_cpf(cpf):
        return jsonify({'error': 'CPF inválido'}), 400
    if not ofAge(data_nasc):
        return jsonify({'error': 'Cliente menor de idade'}), 400

    #Conectar com o banco de dados
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO clientes (nome, email, cpf, data_nascimento, endereco) VALUES (%s,%s,%s,%s,%s)",
                       (nome, email, cpf, data_nasc, endereco))
        conn.commit()

        return jsonify({'message': 'Cliente criado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()
