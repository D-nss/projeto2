import sys
from criptogramas import mensagens
from texto import legivel, pontuar

BLOCO = 10

def colunas(criptograma):
    return [[criptograma[i] for i in range(p, len(criptograma), BLOCO)] for p in range(BLOCO)]

def difusao_do_contador(textos):
    print("Difusão do contador (valores distintos por coluna / número de blocos):")
    for indice, (_, criptograma) in enumerate(textos, start=1):
        cols = colunas(criptograma)
        blocos = len(cols[0])
        if blocos < 2:
            print(f"  mensagem {indice}: {blocos} bloco, sem o que comparar")
            continue
        distintos = [len(set(coluna)) for coluna in cols]
        print(f"  mensagem {indice}: {blocos} blocos, distintos por coluna {distintos}"
              f"  ({'keystream renovado a cada bloco' if min(distintos) == blocos else 'possível repetição'})")

def recuperacao_por_coluna(textos):
    print("\nRecuperação por coluna (deveria sair português se houvesse keystream repetido):")
    for indice, (_, criptograma) in enumerate(textos, start=1):
        keystream = []
        for posicao, coluna in enumerate(colunas(criptograma)):
            mascara = 0x7F if posicao == 0 else 0xFF
            _, chave = max(
                (pontuar(bytes((b ^ k) & mascara for b in coluna)), k) for k in range(mascara + 1)
            )
            keystream.append(chave)
        claro = bytes(criptograma[i] ^ keystream[i % BLOCO] for i in range(len(criptograma)))
        print(f"  mensagem {indice}: {legivel(claro)!r}")

if __name__ == "__main__":
    textos = mensagens("S01")
    difusao_do_contador(textos)
    recuperacao_por_coluna(textos)
