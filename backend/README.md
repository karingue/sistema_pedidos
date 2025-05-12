
# 📦 Sistema de Gerenciamento de Pedidos

Este projeto é um sistema web simples desenvolvido com **Python (Flask)** e **MySQL**, com rotas para **CRUD de clientes e pedidos**, além de uma interface web com HTML, CSS e JavaScript.

## 📁 Estrutura do Projeto


backend/
├── app.py
├── database.py
├── routes/
│   ├── cliente_routes.py
│   └── pedido_routes.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── clientes.js
│       └── pedidos.js
├── templates/
│   ├── clientes.html
│   ├── index.html
│   ├── layout.html
│   └── pedidos.html
├── utils/
│   └── validators.py
└── README.md




## ⚙️ Pré-requisitos

- Python 3.10+
- MySQL Server instalado e rodando
- MySQL Workbench ou outro gerenciador de banco de dados



## 🔧 Instalação

1. **Clone o repositório**:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd backend
```

2. **Instale as dependências necessárias**:

```bash
pip install flask mysql-connector-python
```


## 🗃️ Criação do Banco de Dados

Execute o script SQL abaixo no seu MySQL para criar as tabelas:

```sql
CREATE DATABASE IF NOT EXISTS sistema_pedidos;
USE sistema_pedidos;

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    endereco TEXT NOT NULL
);

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    data_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE CASCADE
);

CREATE TABLE itens_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    descricao_item VARCHAR(255) NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    preco_unitario DECIMAL(10, 2) NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        ON DELETE CASCADE
);
```


## 🚀 Executando a Aplicação

1. **Configure a conexão com o banco em `database.py`**:

```python
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='SEU_USUARIO',
        password='SUA_SENHA',
        database='sistema_pedidos'
    )
```

2. **Inicie o servidor Flask**:

```bash
python app.py
```

3. Acesse o navegador em:  
`http://localhost:5000`


## 📌 Funcionalidades

- ✅ Cadastro, listagem, edição e exclusão de clientes
- ✅ Cadastro e gerenciamento de pedidos com itens
- ✅ Filtro por nome e data nos pedidos
- ✅ Interface web responsiva com HTML + CSS + JS
- ✅ API REST integrada para consumo externo


## 📮 API REST

- Endpoints disponíveis:
  - `GET /api/clientes`
  - `POST /api/clientes`
  - `PUT /api/clientes/<id>`
  - `DELETE /api/clientes/<id>`
  - `GET /api/pedidos`
  - `POST /api/pedidos`
  - `PUT /api/pedidos/<id>`
  - `DELETE /api/pedidos/<id>`
  - `GET /api/pedidos/consulta`

- Para testar, importe o arquivo `.json` no [Postman](https://www.postman.com/).


## 🛠 Tecnologias Usadas

- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript


## 👨‍💻 Autor

Gabriel Henrique Karing  
Engenharia de Software – Católica de Jaraguá do Sul  