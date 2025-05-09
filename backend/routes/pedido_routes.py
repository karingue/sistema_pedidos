from flask import Blueprint, jsonify, request
from database import get_connection
from datetime import datetime

pedido_bp = Blueprint('pedido', __name__)

@pedido_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.get_json()
    cliente_id = dados.get('cliente_id')
    itens = dados.get('itens')

    if not itens or len(itens) == 0: return jsonify({'error': 'Pedido deve conter pelo menos um item'}), 400

    data_pedido = datetime.now()
    valor_total = sum(item['quantidade'] * item['preco_unitario']for item in itens)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        #Inserindo o pedido no banco de dados
        cursor.execute("INSERT INTO pedidos (cliente_id, data_pedido, valor_total) VALUES (%s,%s,%s)", 
                       (cliente_id, data_pedido, valor_total))
        pedido_id = cursor.lastrowid

        #Inserindo os itens do pedido no banco de dados
        for item in itens:
            cursor.execute("INSERT INTO itens_pedido (pedido_id, descricao_item, quantidade, preco_unitario) VALUES (%s,%s,%s,%s)",
                           (pedido_id, item['descricao_item'], item['quantidade'], item['preco_unitario']))
        
        conn.commit()
        return jsonify({'message': 'Pedido criado com sucesso!', 'pedido_id': pedido_id}), 201 

    except Exception as e:
        conn.rollback()  
        return jsonify({'error': str(e)}), 500 

    finally:
        cursor.close()
        conn.close()


@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['PUT'])
def atualizar_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica se o pedido existe e pega a data
        cursor.execute("SELECT data_pedido FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404

        data_pedido = pedido['data_pedido']
        if (datetime.now() - data_pedido).total_seconds() > 86400:
            return jsonify({'error': 'Pedido não pode ser alterado após 24 horas'}), 403

        dados = request.get_json()
        itens = dados.get('itens')

        if not itens or len(itens) == 0:
            return jsonify({'error': 'Pedido deve conter pelo menos um item'}), 400

        # Apaga os itens antigos
        cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))

        # Insere os novos itens
        valor_total = 0
        for item in itens:
            valor_total += item['quantidade'] * item['preco_unitario']
            cursor.execute("""
                INSERT INTO itens_pedido (pedido_id, descricao_item, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, item['descricao_item'], item['quantidade'], item['preco_unitario']))

        # Atualiza valor_total do pedido
        cursor.execute("UPDATE pedidos SET valor_total = %s WHERE id = %s", (valor_total, pedido_id))

        conn.commit()
        return jsonify({'message': 'Pedido atualizado com sucesso!'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    conn = get_connection()  # Conexão com o banco
    cursor = conn.cursor(dictionary=True)

    try:
        # Buscando o pedido pelo ID
        cursor.execute("SELECT id, cliente_id, data_pedido, valor_total FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404

        # Buscando os itens do pedido
        cursor.execute("SELECT descricao_item, quantidade, preco_unitario FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))
        pedido['itens'] = cursor.fetchall()

        return jsonify(pedido)

    except Exception as e:
        # Aqui estamos capturando qualquer exceção que possa ocorrer
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@pedido_bp.route('/pedidos', methods=['GET'])
def listar_pedidos():
    nome = request.args.get('nome')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        base_query = """SELECT p.id, p.data_pedido, p.valor_total, c.nome AS cliente
                        FROM pedidos p
                        JOIN clientes c ON p.cliente_id = c.id
                        WHERE 1 = 1"""

        params = []

        if nome:
            base_query += " AND c.nome LIKE %s"
            params.append(f"%{nome}%")
        if inicio and fim:
            base_query += " AND p.data_pedido BETWEEN %s AND %s"
            params.extend([inicio, fim])

        cursor.execute(base_query, tuple(params))
        pedidos = cursor.fetchall()

        for pedido in pedidos:
            cursor.execute("SELECT descricao_item, quantidade, preco_unitario FROM itens_pedido WHERE pedido_id = %s", (pedido['id'],))
            pedido['itens'] = cursor.fetchall()

        return jsonify(pedidos)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()




@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['DELETE'])
def excluir_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        #Verificando se o pedido existe
        cursor.execute("SELECT id FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()
        if not pedido:
            return jsonify({'error': 'O pedido {pedido_id} não foi encontrado!!'}), 404

        #Deletando todos os itens do pedido
        cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))

        #Deletando o pedido 
        cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))

        #Reset do auto incremento do banco de dados
        cursor.execute("SELECT MAX(id) FROM pedidos")
        max_id = cursor.fetchone()[0] or 0 #Pegando o maior ID Atual
        #Resetando o contador do auto incremento 
        if max_id is not None:
            cursor.execute(f"ALTER TABLE pedidos AUTO_INCREMENT = {max_id + 1}")
        conn.commit() #Comitando as alterações para o banco de dados

        return jsonify({'message': f'Pedido {pedido_id} excluido com sucesso!!'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()