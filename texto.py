from math import log

FREQUENCIAS = {
    " ": 0.170, "a": 0.120, "e": 0.105, "o": 0.090, "s": 0.065, "r": 0.055, "i": 0.052,
    "n": 0.043, "d": 0.042, "m": 0.040, "u": 0.039, "t": 0.038, "c": 0.033, "l": 0.024,
    "p": 0.022, "v": 0.014, "g": 0.011, "h": 0.011, "q": 0.009, "b": 0.009, "f": 0.009,
    "z": 0.004, "j": 0.003, "x": 0.002, "k": 0.001, "w": 0.001, "y": 0.001,
}


def _tabela():
    tabela = [log(1e-7)] * 256
    for codigo in range(0x20, 0x7F):
        tabela[codigo] = log(4e-4)
    for codigo in range(0x80, 0xC0):
        tabela[codigo] = log(1e-3)
    tabela[0xC3] = log(4e-3)
    tabela[0x0A] = log(1e-3)
    for simbolo in ".,":
        tabela[ord(simbolo)] = log(8e-3)
    for simbolo in "!?:;'\"-()":
        tabela[ord(simbolo)] = log(1.5e-3)
    for digito in "0123456789":
        tabela[ord(digito)] = log(2e-3)
    for letra, frequencia in FREQUENCIAS.items():
        tabela[ord(letra)] = log(frequencia)
        if letra != " ":
            tabela[ord(letra.upper())] = log(frequencia * 0.04)
    return tabela


LOG_PROB = _tabela()


def pontuar(dados):
    return sum(LOG_PROB[byte] for byte in dados)


def legivel(dados):
    return "".join(chr(byte) if 0x20 <= byte < 0x7F else "." for byte in dados)
