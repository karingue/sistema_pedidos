from flask import Flask, render_template
from flask_cors import CORS
from routes.cliente_routes import cliente_bp
from routes.pedido_routes import pedido_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(cliente_bp)
app.register_blueprint(pedido_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

if __name__ == '__main__':
    app.run(debug=True); 