
# Sistema de Gerenciamento de Pedidos

Este é um sistema web desenvolvido com **Python (Flask)** e **MySQL** para gerenciamento de clientes e pedidos. A aplicação permite cadastrar clientes, registrar pedidos com múltiplos itens, listar, editar e excluir registros, além de aplicar filtros e análises.

---

## 📁 Estrutura do Projeto

```
backend/
├── app.py
├── database.py
├── requirements.txt
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
└── utils/
    └── validators.py
```

---

## 🛠️ Como rodar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio/backend
```

### 2. Crie o banco de dados

Execute o script SQL abaixo no MySQL Workbench ou outro cliente:

```sql
-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS sistema_pedidos;
USE sistema_pedidos;

-- Tabela: clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    endereco TEXT NOT NULL
);

-- Tabela: pedidos
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    data_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE CASCADE
);

-- Tabela: itens_pedido
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

### 3. Instale as dependências

Certifique-se de estar na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

---

### 4. Configure o banco

No arquivo `database.py`, configure com suas credenciais:

```python
config = {
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'host': 'localhost',
    'database': 'sistema_pedidos'
}
```

---

### 5. Execute a aplicação

```bash
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

---

## 📄 Documentação da API

Você pode importar o arquivo `.json` de documentação no [Postman](https://www.postman.com/) para testar as rotas da API.

---

## ✍️ Autor

Gabriel Henrique Karing – [karing.com.br](https://karing.com.br)

---
