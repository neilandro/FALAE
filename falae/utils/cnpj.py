import re


_TAMANHO_CNPJ = 14
_PESOS_PRIMEIRO_DV = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_SEGUNDO_DV = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def normalizar_cnpj(valor) -> str:
    """Remove separadores, converte para maiúsculas e preserva A-Z/0-9."""
    texto = str(valor or "").strip().upper()
    return re.sub(r"[^A-Z0-9]", "", texto)


def _valor_caractere(caractere: str) -> int:
    """Converte o caractere para o valor ASCII menos 48, conforme a RFB."""
    return ord(caractere) - 48


def _calcular_digito(base: str, pesos: tuple[int, ...]) -> str:
    soma = sum(
        _valor_caractere(caractere) * peso
        for caractere, peso in zip(base, pesos)
    )

    resto = soma % 11
    digito = 0 if resto in (0, 1) else 11 - resto
    return str(digito)


def calcular_digitos_verificadores(base: str) -> str:
    base_normalizada = normalizar_cnpj(base)

    if len(base_normalizada) != 12:
        raise ValueError("A base do CNPJ deve possuir 12 posições.")

    if not re.fullmatch(r"[A-Z0-9]{12}", base_normalizada):
        raise ValueError("A base do CNPJ contém caracteres inválidos.")

    primeiro = _calcular_digito(
        base_normalizada,
        _PESOS_PRIMEIRO_DV
    )

    segundo = _calcular_digito(
        base_normalizada + primeiro,
        _PESOS_SEGUNDO_DV
    )

    return primeiro + segundo


def validar_cnpj(valor) -> bool:
    cnpj = normalizar_cnpj(valor)

    if len(cnpj) != _TAMANHO_CNPJ:
        return False

    if not re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", cnpj):
        return False

    if len(set(cnpj)) == 1:
        return False

    base = cnpj[:12]
    informado = cnpj[12:]

    try:
        calculado = calcular_digitos_verificadores(base)
    except ValueError:
        return False

    return informado == calculado


def formatar_cnpj(valor) -> str:
    cnpj = normalizar_cnpj(valor)

    if len(cnpj) != _TAMANHO_CNPJ:
        return cnpj

    return (
        f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
        f"{cnpj[8:12]}-{cnpj[12:14]}"
    )


def tipo_cnpj(valor) -> str | None:
    cnpj = normalizar_cnpj(valor)

    if len(cnpj) != _TAMANHO_CNPJ:
        return None

    return "ALFANUMERICO" if re.search(r"[A-Z]", cnpj[:12]) else "NUMERICO"