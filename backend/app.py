from flask import Flask
from flask_cors import CORS
from routes.cliente_routes import cliente_bp
from routes.pedido_routes import pedido_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(cliente_bp)
app.register_blueprint(pedido_bp)

@app.route('/home')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True); 