from flask import Blueprint, jsonify, request
from database import get_connection

# Criando o Blueprint para clientes
cliente_bp = Blueprint('cliente', __name__)

# Rota para criar um novo cliente (POST)
@cliente_bp.route('/api/clientes', methods=['POST'])
def criar_cliente():
    dados = request.get_json()  # Obtém os dados enviados no corpo da requisição
    nome = dados.get('nome')
    email = dados.get('email')
    cpf = dados.get('cpf')
    data_nasc = dados.get('data_nascimento')
    endereco = dados.get('endereco')

    # Verificando se todos os dados obrigatórios foram passados
    if not nome or not email or not cpf or not data_nasc or not endereco:
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400  # Retorna erro se faltar algum campo obrigatório

    # Conectando com o banco de dados
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Inserindo os dados do cliente no banco de dados
        cursor.execute("INSERT INTO clientes (nome, email, cpf, data_nascimento, endereco) VALUES (%s, %s, %s, %s, %s)",
                       (nome, email, cpf, data_nasc, endereco))
        conn.commit()  # Confirma a transação no banco de dados

        return jsonify({'message': 'Cliente criado com sucesso!'}), 201  # Retorna sucesso
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Retorna erro em caso de falha
    finally:
        cursor.close()
        conn.close()  # Fecha a conexão com o banco de dados

# Rota para listar todos os clientes (GET)
@cliente_bp.route('/api/clientes', methods=['GET'])
def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Usando cursor com dicionário para facilitar o mapeamento

    try:
        # Buscando todos os clientes no banco de dados
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()  # Obtém todos os clientes

        return jsonify(clientes), 200  # Retorna os clientes encontrados
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Retorna erro em caso de falha
    finally:
        cursor.close()
        conn.close()

# Rota para listar clientes sem pedidos (GET)
@cliente_bp.route('/api/clientes/disponiveis', methods=['GET'])
def listar_clientes_disponiveis():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Usando LEFT JOIN para buscar clientes sem pedidos
        cursor.execute(""" 
            SELECT clientes.* 
            FROM clientes
            LEFT JOIN pedidos ON clientes.id = pedidos.cliente_id
            WHERE pedidos.cliente_id IS NULL
        """)
        clientes_disponiveis = cursor.fetchall()  # Obtém clientes sem pedidos

        # Formatando os clientes para retornar apenas os dados necessários
        clientes_formatados = [
            {
                "id": cliente[0],
                "nome": cliente[1],
                "email": cliente[2],     
                "telefone": cliente[3]   # Ajuste conforme os campos que você deseja retornar
            }
            for cliente in clientes_disponiveis
        ]

        return jsonify({"clientes_disponiveis": clientes_formatados}), 200  # Retorna clientes disponíveis
    except Exception as erro:
        print("Erro ao listar clientes disponíveis:", erro)
        return jsonify({"erro": "Erro ao listar clientes disponíveis"}), 500  # Retorna erro em caso de falha
    finally:
        cursor.close()
        conn.close()

# Rota para excluir um cliente (DELETE)
@cliente_bp.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def excluir_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificando se o cliente existe
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
        cliente = cursor.fetchone()
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404  # Retorna erro se o cliente não existir

        # Excluindo o cliente
        cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
        conn.commit()  # Confirma a exclusão no banco de dados

        return jsonify({'message': 'Cliente excluído com sucesso!'}), 200  # Retorna sucesso
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Retorna erro em caso de falha
    finally:
        cursor.close()
        conn.close()
