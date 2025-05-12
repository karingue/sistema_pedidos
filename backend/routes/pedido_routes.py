from flask import Blueprint, request, jsonify
from database import get_connection

# Criando o Blueprint para pedidos
pedido_bp = Blueprint('pedido', __name__)

# ROTA: Listar todos os pedidos
@pedido_bp.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    conn = get_connection()  # Estabelecendo a conexão com o banco
    cursor = conn.cursor(dictionary=True)  # Usando cursor de dicionário para facilitar o mapeamento

    try:
        # Consultando pedidos e unindo com a tabela de clientes para pegar o nome do cliente
        cursor.execute("""
            SELECT p.id, p.cliente_id, p.valor_total, p.data_pedido, c.nome AS cliente
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
        """)
        pedidos = cursor.fetchall()

        # Para cada pedido, buscamos os itens associados a ele
        for pedido in pedidos:
            cursor.execute("""
                SELECT id, descricao_item, quantidade, preco_unitario
                FROM itens_pedido
                WHERE pedido_id = %s
            """, (pedido['id'],))
            pedido['itens'] = cursor.fetchall()

        return jsonify(pedidos)  # Retorna todos os pedidos encontrados

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Caso ocorra erro

    finally:
        cursor.close()
        conn.close()  # Fecha a conexão com o banco

# ROTA: Criar um novo pedido
@pedido_bp.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    data = request.get_json()  # Obtém os dados enviados no corpo da requisição
    cliente_id = data.get('cliente_id')
    itens_data = data.get('itens', [])  # Obtém os itens do pedido

    if not itens_data:  # Verifica se há itens no pedido
        return jsonify({'error': 'Lista de itens está vazia.'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Inserindo o pedido no banco
        cursor.execute("INSERT INTO pedidos (cliente_id) VALUES (%s)", (cliente_id,))
        pedido_id = cursor.lastrowid  # Obtém o ID do pedido recém-criado

        valor_total = 0  # Inicializa o valor total do pedido
        for item in itens_data:
            descricao = item['descricao_item']
            preco = float(item['preco_unitario'])
            quantidade = int(item['quantidade'])
            valor_total += preco * quantidade  # Calcula o valor total do pedido

            # Inserindo os itens do pedido
            cursor.execute("""
                INSERT INTO itens_pedido (pedido_id, descricao_item, preco_unitario, quantidade) 
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, descricao, preco, quantidade))

        # Atualizando o valor total do pedido
        cursor.execute("UPDATE pedidos SET valor_total = %s WHERE id = %s", (valor_total, pedido_id))
        conn.commit()  # Confirma a transação no banco

        return jsonify({'message': 'Pedido criado com sucesso!', 'pedido_id': pedido_id}), 201

    except Exception as e:
        conn.rollback()  # Faz rollback em caso de erro
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()  # Fecha a conexão

# ROTA: Obter um pedido por ID
@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Buscando o pedido pelo ID
        cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:  # Caso o pedido não seja encontrado
            return jsonify({'error': 'Pedido não encontrado'}), 404

        # Buscando os itens do pedido
        cursor.execute("""
            SELECT id, descricao_item, quantidade, preco_unitario 
            FROM itens_pedido 
            WHERE pedido_id = %s
        """, (pedido_id,))
        pedido['itens'] = cursor.fetchall()

        return jsonify(pedido)  # Retorna os dados do pedido

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ROTA: Editar um pedido existente
@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['PUT'])
def editar_pedido(pedido_id):
    data = request.get_json()  # Obtém os dados enviados no corpo da requisição
    cliente_id = data.get('cliente_id')
    itens_data = data.get('itens', [])

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Atualizando as informações do pedido
        cursor.execute("UPDATE pedidos SET cliente_id = %s WHERE id = %s", (cliente_id, pedido_id))

        for item_data in itens_data:
            descricao = item_data['descricao_item']
            preco_unitario = item_data['preco_unitario']
            quantidade = item_data['quantidade']
            item_id = item_data.get('id')

            # Caso o item já exista, atualiza; caso contrário, insere
            if item_id:
                cursor.execute("""
                    UPDATE itens_pedido
                    SET descricao_item = %s, preco_unitario = %s, quantidade = %s
                    WHERE id = %s AND pedido_id = %s
                """, (descricao, preco_unitario, quantidade, item_id, pedido_id))
            else:
                cursor.execute("""
                    INSERT INTO itens_pedido (pedido_id, descricao_item, preco_unitario, quantidade)
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id, descricao, preco_unitario, quantidade))

        # Atualiza o valor total do pedido
        valor_total = sum(item['preco_unitario'] * item['quantidade'] for item in itens_data)
        cursor.execute("UPDATE pedidos SET valor_total = %s WHERE id = %s", (valor_total, pedido_id))

        conn.commit()
        return jsonify({'message': 'Pedido atualizado com sucesso!'}), 200

    except Exception as e:
        conn.rollback()  # Faz rollback em caso de erro
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ROTA: Excluir um pedido
@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['DELETE'])
def excluir_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Excluindo os itens do pedido primeiro
        cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))
        # Excluindo o pedido
        cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
        conn.commit()  # Confirma a exclusão

        return jsonify({'message': 'Pedido excluído com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ROTA: Excluir um item individual de um pedido
@pedido_bp.route('/pedidos/item/<int:item_id>', methods=['DELETE'])
def excluir_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Excluindo o item do pedido
        cursor.execute("DELETE FROM itens_pedido WHERE id = %s", (item_id,))
        conn.commit()  # Confirma a exclusão

        return jsonify({'message': 'Item excluído com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ROTA: Consultar pedidos com filtros
@pedido_bp.route('/api/pedidos/consulta', methods=['GET'])
def consultar_pedidos():
    nome_cliente = request.args.get('nome_cliente')  # Obtém o parâmetro de nome do cliente
    data_inicio = request.args.get('data_inicio')  # Obtém o parâmetro de data inicial
    data_fim = request.args.get('data_fim')  # Obtém o parâmetro de data final

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Montando a consulta com filtros dinâmicos
        query = "SELECT pedidos.*, clientes.nome AS cliente_nome FROM pedidos JOIN clientes ON pedidos.cliente_id = clientes.id WHERE 1=1"
        params = []

        if nome_cliente:  # Adicionando filtro por nome do cliente
            query += " AND clientes.nome LIKE %s"
            params.append(f"%{nome_cliente}%")

        if data_inicio:  # Adicionando filtro por data inicial
            query += " AND pedidos.data_pedido >= %s"
            params.append(data_inicio)

        if data_fim:  # Adicionando filtro por data final
            query += " AND pedidos.data_pedido <= %s"
            params.append(data_fim)

        cursor.execute(query, params)
        pedidos = cursor.fetchall()

        # Consultando o total gasto por cliente
        total_gasto_query = """
            SELECT clientes.id, SUM(item.preco_unitario * item.quantidade) AS total_gasto
            FROM pedidos AS p
            JOIN itens_pedido AS item ON p.id = item.pedido_id
            JOIN clientes ON p.cliente_id = clientes.id
            GROUP BY clientes.id
        """
        cursor.execute(total_gasto_query)
        totais_clientes = cursor.fetchall()
        totais_gasto_dict = {total['id']: total['total_gasto'] for total in totais_clientes}

        # Adicionando o total gasto em cada pedido
        for pedido in pedidos:
            cliente_id = pedido['cliente_id']
            pedido['total_gasto'] = totais_gasto_dict.get(cliente_id, 0)

        return jsonify(pedidos), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
