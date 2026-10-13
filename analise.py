import importlib.util
import os
import random
import feistel
import spn
import testes
from cipher_base import (
    BLOCK_SIZE,
    FEISTEL_ROUNDS,
    NIBBLE_SIZE,
    SBOX_ENTRIES,
    SPN_ROUNDS,
)
from criptogramas import mensagens

RAIZ = os.path.dirname(os.path.abspath(__file__))

CHAVE_ANALISE = 0x23453456343453450124
SEMENTE = 20251012
TIPO = {"S": "SPN", "F": "Feistel"}
RODADAS_OFICIAIS = {"S": SPN_ROUNDS, "F": FEISTEL_ROUNDS}

def carregar_projeto(identificador):
    pasta = "Rede de Feistel" if identificador.startswith("F") else "SPN"
    caminho = os.path.join(RAIZ, pasta, identificador, "my_cipher.py")
    especificacao = importlib.util.spec_from_file_location(f"cifra_{identificador}", caminho)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo

def construir(identificador, projeto, rodadas):
    if identificador.startswith("S"):
        return spn.SPN80(projeto.SBOX, projeto.SPN_PBOX, rodadas, CHAVE_ANALISE)
    return feistel.Feistel80(projeto.SBOX, projeto.FEISTEL_PBOX, rodadas, CHAVE_ANALISE)

def propriedades_sbox(sbox):
    distintos = len(set(sbox))
    ddt = max(
        sum(1 for x in range(SBOX_ENTRIES) if sbox[x] ^ sbox[x ^ a] == b)
        for a in range(1, SBOX_ENTRIES) for b in range(SBOX_ENTRIES)
    )
    lat = max(
        abs(sum(
            1 for x in range(SBOX_ENTRIES)
            if bin(x & a).count("1") % 2 == bin(sbox[x] & b).count("1") % 2
        ) - SBOX_ENTRIES // 2)
        for a in range(SBOX_ENTRIES) for b in range(1, SBOX_ENTRIES)
    )
    return {"bijetora": distintos == SBOX_ENTRIES, "valores_distintos": distintos,
            "ddt_max": ddt, "lat_vies_max": lat}

def efeito_avalanche(identificador, projeto, rodadas, amostras=200):
    cifra = construir(identificador, projeto, rodadas)
    rng = random.Random(SEMENTE + rodadas)

    soma = 0.0
    minimo = 1.0
    maximo = 0.0
    quantidade = 0
    muda = [[False] * BLOCK_SIZE for _ in range(BLOCK_SIZE)]

    for _ in range(amostras):
        claro = rng.getrandbits(BLOCK_SIZE)
        base = cifra.encrypt_block(claro)
        for bit_entrada in range(BLOCK_SIZE):
            diferenca = base ^ cifra.encrypt_block(claro ^ (1 << bit_entrada))
            fracao = bin(diferenca).count("1") / BLOCK_SIZE
            soma += fracao
            minimo = min(minimo, fracao)
            maximo = max(maximo, fracao)
            quantidade += 1
            while diferenca:
                bit_saida = (diferenca & -diferenca).bit_length() - 1
                muda[bit_entrada][bit_saida] = True
                diferenca &= diferenca - 1

    nunca = sum(1 for linha in muda for mudou in linha if not mudou)
    return {"media": soma / quantidade, "min": minimo, "max": maximo, "pares_fixos": nunca}

def saida_em_volume(identificador, projeto, nbytes=20000):
    cifra = construir(identificador, projeto, RODADAS_OFICIAIS[identificador[0]])
    bloco_bytes = BLOCK_SIZE // 8
    rng = random.Random(SEMENTE)
    saida = bytearray()
    while len(saida) < nbytes:
        saida += cifra.encrypt_block(rng.getrandbits(BLOCK_SIZE)).to_bytes(bloco_bytes, "big")
    return bytes(saida)


def formata(resultado):
    def p(teste):
        valor = resultado[teste]["p"]
        return f"{valor:.4f}" if valor == valor else "  -  "
    return f"monobit p={p('monobit')} | blocos p={p('blocos')} | corridas p={p('corridas')}"

def relatorio(identificadores=("S01", "S02", "F01")):
    for identificador in identificadores:
        projeto = carregar_projeto(identificador)
        tipo = TIPO[identificador[0]]
        oficiais = RODADAS_OFICIAIS[identificador[0]]
        print(f"\n===================== {identificador} ({tipo}, {oficiais} rodadas) =====================")

        prop = propriedades_sbox(projeto.SBOX)
        print("[ S-box / P-box ]")
        print(f"  S-box: {'bijetora' if prop['bijetora'] else 'NÃO bijetora'}"
              f" ({prop['valores_distintos']} valores distintos), "
              f"DDT máx = {prop['ddt_max']}/16, viés linear máx = {prop['lat_vies_max']}/8")

        print("[ Efeito avalanche ]  (fração de bits do criptograma que muda por bit do claro invertido)")
        for rodadas in range(1, 9):
            av = efeito_avalanche(identificador, projeto, rodadas)
            marca = "  <- rodadas oficiais" if rodadas == oficiais else ""
            print(f"  R{rodadas}: média={av['media']:.4f} | min={av['min']:.4f} | max={av['max']:.4f}"
                  f" | pares (entrada,saída) fixos={av['pares_fixos']:4d}/6400{marca}")

        print("[ Testes estatísticos nos criptogramas recebidos ]")
        for indice, (_, criptograma) in enumerate(mensagens(identificador), start=1):
            print(f"  msg {indice} ({len(criptograma):3d} bytes): {formata(testes.aplicar(criptograma))}")

        print("[ Testes estatísticos em 20 000 bytes gerados com a nossa chave ]")
        print(f"  volume:         {formata(testes.aplicar(saida_em_volume(identificador, projeto)))}")

if __name__ == "__main__":
    relatorio()
