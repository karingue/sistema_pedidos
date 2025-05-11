from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/database'
db = SQLAlchemy(app)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    itens = db.relationship('Item', backref='pedido', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    itens_data = data.get('itens')

    pedido = Pedido(cliente_id=cliente_id)
    db.session.add(pedido)
    db.session.commit()

    for item_data in itens_data:
        item = Item(pedido_id=pedido.id, nome=item_data['nome'], preco_unitario=item_data['preco_unitario'], quantidade=item_data['quantidade'])
        db.session.add(item)

    db.session.commit()
    return jsonify({'message': 'Pedido criado com sucesso!'}), 201

@app.route('/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({'error': f'O pedido {pedido_id} não foi encontrado!'}), 404

    itens = [{
        'nome': item.nome,
        'preco_unitario': item.preco_unitario,
        'quantidade': item.quantidade
    } for item in pedido.itens]

    return jsonify({'pedido': {'cliente_id': pedido.cliente_id, 'itens': itens}})

@app.route('/pedidos/<int:pedido_id>', methods=['PUT'])
def editar_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({'error': f'O pedido {pedido_id} não foi encontrado!'}), 404

    data = request.get_json()
    pedido.cliente_id = data.get('cliente_id', pedido.cliente_id)

    db.session.commit()

    for item_data in data.get('itens', []):
        item = Item.query.filter_by(pedido_id=pedido_id, nome=item_data['nome']).first()
        if item:
            item.preco_unitario = item_data['preco_unitario']
            item.quantidade = item_data['quantidade']
        else:
            new_item = Item(pedido_id=pedido_id, nome=item_data['nome'], preco_unitario=item_data['preco_unitario'], quantidade=item_data['quantidade'])
            db.session.add(new_item)

    db.session.commit()
    return jsonify({'message': 'Pedido atualizado com sucesso!'}), 200

@app.route('/pedidos/<int:pedido_id>', methods=['DELETE'])
def excluir_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({'error': f'O pedido {pedido_id} não foi encontrado!'}), 404

    db.session.delete(pedido)
    db.session.commit()
    return jsonify({'message': 'Pedido excluído com sucesso!'}), 200

@app.route('/pedidos/item/<int:item_id>', methods=['DELETE'])
def excluir_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item não encontrado!'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item excluído com sucesso!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
