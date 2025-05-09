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
        cursor.execute("INSERT INTO pedidos (cliente_id, data_pedido, valor_total) VALUES (%s,%s,%s)," (cliente_id, data_pedido, valor_total))
        pedido_id = cursor.lastrowid

        #Inserindo os itens do pedido no banco de dados
        for item in itens:
            cursor.execute("INSERT INTO itens_pedido (pedido_id, descricao_item, quantidade, preco_unitario) VALUES (%s,%s,%s,%s)",
                           (pedido_id, item['descricao_item'], item['quantidade'], item['preco_unitario']))
        
        conn.commit()
        return jsonify({'message': 'Pedido criado com sucesso!', 'pedido_id': pedido_id}), 201 

    except Exception as e:
        conn.roolback()  
        return jsonify({'error': str(e)}), 500 

    finally:
        cursor.close()
        conn.close()



@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['PUT'])
def att_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    #Buscando a data do pedido 
    cursor.execute("SELECT data_pedido FROM pedidos WHERE id = %s", (pedido_id))
    pedido = cursor.fetchone()


    if not pedido:
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    #Verificação do tempo de criação do pedido desde sua criação
    data_pedido = pedido['data_pedido']
    if (datetime.now() - data_pedido).total_seconds() > 86400:
        return jsonify({'error': 'Pedido não pode ser alterado após 24 horas'}), 403
    

    return jsonify({'message': 'Seu pedido foi atualizado com sucesso!'})
