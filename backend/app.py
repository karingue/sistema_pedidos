from flask import Flask, render_template
from flask_cors import CORS
from routes.cliente_routes import cliente_bp
from routes.pedido_routes import pedido_bp

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir requisições de origens diferentes

# Registrar Blueprints (Modulariza as rotas em partes reutilizáveis)
app.register_blueprint(cliente_bp)  # Blueprint para gerenciar clientes
app.register_blueprint(pedido_bp, name='pedido_bp')  # Blueprint para gerenciar pedidos
app.register_blueprint(pedido_bp, url_prefix='/api', name='pedido_api_bp')  # Blueprint de API para pedidos

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de clientes
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

# Rota para a página de pedidos
@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

if __name__ == '__main__':
    app.run(debug=False)  # Executa a aplicação em modo de depuração
