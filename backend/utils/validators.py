import re
from validate_docbr import CPF
from datetime import datetime


def validate_email(email):
    #Valida o formate do email, para verificar se é um email valido
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_cpf(cpf):
    #Valida o CPF, faz a verificação se o CPF é um CPF valido
    cpf_validator = CPF()
    return cpf_validator.validate(cpf)

def ofAge(data_nasc):
    #Verifica se o cliente ja é maior de idade
    birth = datetime.strptime(data_nasc, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return age >= 18

def dentro_limite_24h(data_pedido_str):
    """
    Verifica se a data/hora do pedido está dentro do limite de 24 horas.
    Recebe a data em string no formato ISO (ex: '2025-05-08T14:30:00')
    """
    try:
        data_pedido = datetime.fromisoformat(data_pedido_str)
    except ValueError:
        return False

    agora = datetime.now()
    diferenca = agora - data_pedido
    return diferenca.total_seconds() <= 86400  # 24h em segundos
