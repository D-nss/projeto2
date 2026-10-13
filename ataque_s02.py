import sys
from criptogramas import mensagens
from texto import legivel, pontuar

BLOCO = 10

def colunas(criptograma):
    return [[criptograma[i] for i in range(p, len(criptograma), BLOCO)] for p in range(BLOCO)]

def melhor_byte(coluna, mascara=0xFF):
    pontos, chave = max(
        (pontuar(bytes((b ^ k) & mascara for b in coluna)), k) for k in range(mascara + 1)
    )
    return chave, pontos

def recuperar():
    textos = mensagens("S02")
    recuperado = []

    for nonce, criptograma in textos:
        cols = colunas(criptograma)
        keystream = []
        for posicao, coluna in enumerate(cols):
            mascara = 0x7F if posicao == 0 else 0xFF
            chave, _ = melhor_byte(coluna, mascara)
            keystream.append(chave)
        claro = bytes(criptograma[i] ^ keystream[i % BLOCO] for i in range(len(criptograma)))
        recuperado.append((nonce, claro))

    return recuperado

if __name__ == "__main__":
    for indice, (nonce, claro) in enumerate(recuperar(), start=1):
        texto = claro.decode("latin-1")
        marcado = "".join(c if 0x20 <= ord(c) < 0x7F else "·" for c in texto)
        print(f"mensagem {indice} (nonce 0x{nonce:010x}, {len(claro)} bytes):")
        print(f"   {marcado}\n")
