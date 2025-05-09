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
def att_pedido(pedido_id):
    dados = request.get_json()
    novos_itens = dados.get('itens')

    if not novos_itens or len(novos_itens) == 0:
        return jsonify({'error': 'Pedido deve ter ao menos um item'}), 400
    
    conn = get_connection()
    corsor = conn.cursor(dictionary=True)

    try:
        #Verificando se o pedido existe e qual a sua data
        cursor.execute("SELECT data_pedido FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404
        
        data_pedido = pedido['data_pedido']
        if (datetime.now() - data_pedido).total_seconds() > 86400:
            return jsonify({'error': 'Pedido não pode ser alterado após 24 horas'}), 403
        
        #Removendo os itens antigos do pedido atual
        cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))
        
        #Calculando um novo valor total do pedido
        novo_valor_total = sum(item['quantidade']* item['preco_unitario'] for item in novos_itens)

        #Adicionando os novos itens do pedido
        for item in novos_itens:
            cursor.execute("""
                           INSERT INTO itens_pedido (pedido_id, descricao_item, quantidade, preco_unitario)
                           VALUES (%s, %s, %s, %s)""",(pedido_id, item['descricao_item'], item['quantidade'], item['preco_unitario']))
            
        #Atualizando o valor total do pedido 
        cursor.execute("UPDATE pedidos SET valor_total = %s WHERE id = %s", (novo_valor_total, pedido_id))

        conn.commit()
        return jsonify({'message' : 'O Pedido foi atualizado com sucesso!'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
def list_orders():
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
            base_query += "AND c.nome LIKE %s"
            params.append(f"%{nome}%")
        if inicio and fim:
            base_query += "AND p.data_pedido BETWEEN %s AND %s"
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