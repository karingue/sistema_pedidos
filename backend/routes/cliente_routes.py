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
    print("Recebido",dados)
    if not nome or not email or not cpf or not data_nasc or not endereco:
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
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



@cliente_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def excluir_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        #Verificando se o cliente existe
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
        cliente = cursor.fetchone()
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
         #Reset do auto incremento do banco de dados
        cursor.execute("SELECT MAX(id) FROM clientes")
        max_id = cursor.fetchone()[0] or 0 #Pegando o maior ID Atual
        #Resetando o contador do auto incremento 
        if max_id is not None:
            cursor.execute(f"ALTER TABLE clientes AUTO_INCREMENT = {max_id + 1}")
        conn.commit() #Comitando as alterações para o banco de dados


        #Deletando o cliente
        cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
        conn.commit()
        return jsonify({'message': 'Cliente excluido com sucesso!!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()


@cliente_bp.route('/clientes/getClientes', methods=['GET'])
def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()

        return jsonify(clientes), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}),500 
    
    finally:
        cursor.close()
        conn.close()



