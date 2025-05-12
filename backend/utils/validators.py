import re
from validate_docbr import CPF
from datetime import datetime, timedelta

# Função para validar o formato de um e-mail
def validate_email(email):
    # Valida o formato do e-mail, utilizando uma expressão regular para verificar se o padrão é válido
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)  # Expressão regular simples para validar e-mail

# Função para validar o CPF
def validate_cpf(cpf):
    # Cria uma instância do validador de CPF da biblioteca 'validate_docbr'
    cpf_validator = CPF()
    # Verifica se o CPF fornecido é válido utilizando a função 'validate' da biblioteca
    return cpf_validator.validate(cpf)

# Função para verificar se a data de nascimento indica maioridade
def ofAge(data_nasc):
    # Recebe a data de nascimento como string no formato 'YYYY-MM-DD'
    birth = datetime.strptime(data_nasc, "%Y-%m-%d")  # Converte a string para um objeto datetime
    today = datetime.now()  # Obtém a data e hora atuais
    # Calcula a idade subtraindo o ano de nascimento do ano atual, ajustando para considerar o mês e o dia
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    # Retorna True se a idade for maior ou igual a 18 anos, indicando que é maior de idade
    return age >= 18

# Função para verificar se o pedido foi feito dentro do limite de 24 horas
def dentro_limite_24h(data_pedido):
    # 'data_pedido' já é um objeto datetime vindo do banco de dados
    agora = datetime.now()  # Obtém a data e hora atuais
    # Compara se a diferença entre a data atual e a data do pedido é de até 24 horas
    return (agora - data_pedido) <= timedelta(hours=24)
