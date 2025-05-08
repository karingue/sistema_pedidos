import mysql.connector


#Criando a conexão com o banco de dados
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="GA%0804&ka",
        database="sistema_pedidos"
    )

