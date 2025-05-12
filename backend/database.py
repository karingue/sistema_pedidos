import mysql.connector

# Função para criar e retornar a conexão com o banco de dados
def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Endereço do servidor de banco de dados
        user="root",  # Usuário do banco de dados
        password="xxxxxxxxx",  # Senha do banco de dados
        database="sistema_pedidos"  # Nome do banco de dados
    )
