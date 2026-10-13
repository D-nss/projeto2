from math import erfc, exp, lgamma, log, sqrt


def _igamc(a, x):
    """Gama incompleta superior regularizada Q(a, x), por série ou fração contínua (Numerical Recipes)."""
    if x <= 0:
        return 1.0
    if x < a + 1:  # série para P(a,x), devolve 1 - P
        termo = 1.0 / a
        soma = termo
        n = a
        for _ in range(1000):
            n += 1
            termo *= x / n
            soma += termo
            if abs(termo) < abs(soma) * 1e-15:
                break
        return 1.0 - soma * exp(-x + a * log(x) - lgamma(a))
    # fração contínua para Q(a,x) direto
    minusculo = 1e-300
    b = x + 1 - a
    c = 1.0 / minusculo
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < minusculo:
            d = minusculo
        c = b + an / c
        if abs(c) < minusculo:
            c = minusculo
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h * exp(-x + a * log(x) - lgamma(a))


def bits_de(dados):
    """Expande bytes numa lista de bits, do mais significativo ao menos significativo."""
    return [(byte >> (7 - i)) & 1 for byte in dados for i in range(8)]


def monobit(bits):
    """NIST 2.1. Soma de +-1; p-valor pela erfc. Mede o viés global de 0/1."""
    n = len(bits)
    s = sum(1 if bit else -1 for bit in bits)
    estatistica = abs(s) / sqrt(n)
    return {"n": n, "estatistica": estatistica, "p": erfc(estatistica / sqrt(2))}


def blocos(bits, tamanho=None):
    """NIST 2.2. Qui-quadrado da fração de 1 em blocos de M bits; p-valor por gama incompleta."""
    n = len(bits)
    if tamanho is None:
        tamanho = max(20, n // 100)  # NIST pede M >= 20 e M > 0,01 n
    quantidade = n // tamanho
    if quantidade == 0:
        return {"n": n, "blocos": 0, "p": float("nan")}
    soma = 0.0
    for indice in range(quantidade):
        trecho = bits[indice * tamanho:(indice + 1) * tamanho]
        pi = sum(trecho) / tamanho
        soma += (pi - 0.5) ** 2
    qui = 4 * tamanho * soma
    return {"n": n, "blocos": quantidade, "tamanho": tamanho, "qui2": qui,
            "p": _igamc(quantidade / 2, qui / 2)}


def corridas(bits):
    """NIST 2.3. Número de corridas (trocas 0<->1 + 1); p-valor pela erfc. Mede oscilação."""
    n = len(bits)
    pi = sum(bits) / n
    if abs(pi - 0.5) >= 2 / sqrt(n):  # pré-requisito do NIST: só faz sentido se o monobit passar
        return {"n": n, "pre_requisito": False, "p": 0.0}
    trocas = 1 + sum(1 for i in range(1, n) if bits[i] != bits[i - 1])
    esperado = 2 * n * pi * (1 - pi)
    desvio = 2 * sqrt(2 * n) * pi * (1 - pi)
    estatistica = abs(trocas - esperado) / desvio
    return {"n": n, "pre_requisito": True, "corridas": trocas, "esperado": esperado,
            "p": erfc(estatistica / sqrt(2))}


def aplicar(dados):
    """Roda os três testes sobre os bytes dados e devolve um dicionário com os p-valores."""
    bits = bits_de(dados)
    return {"monobit": monobit(bits), "blocos": blocos(bits), "corridas": corridas(bits)}
