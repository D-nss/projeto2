import importlib.util
import os
import ctr
import feistel
from cipher_base import FEISTEL_ROUNDS, HALF_SIZE, permutation, rotl, sbox_layer
from criptogramas import mensagens
from texto import legivel, pontuar

BLOCO = 10
JANELA = 15


def carregar_projeto(identificador):
    pasta = "Rede de Feistel" if identificador.startswith("F") else "SPN"
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), pasta, identificador, "my_cipher.py")
    especificacao = importlib.util.spec_from_file_location(f"cifra_{identificador}", caminho)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def tabela_f(projeto):
    return [permutation(sbox_layer(byte, projeto.SBOX, 2), projeto.FEISTEL_PBOX[:8]) for byte in range(256)]


def keystream_par(tabela, subchaves, esquerda, direita):
    for subchave in subchaves:
        esquerda, direita = direita, esquerda ^ tabela[direita ^ subchave]
    return direita, esquerda


def subchaves_do_par(u, par):
    return [((rotl(u, rodada, HALF_SIZE) ^ rodada) >> (8 * par)) & 0xFF for rodada in range(FEISTEL_ROUNDS)]


def atacar_par(tabela, textos, par):
    amostras = []
    for nonce, criptograma in textos:
        esquerda = (nonce >> (8 * par)) & 0xFF
        for inicio in range(0, len(criptograma), BLOCO):
            direita = ((inicio // BLOCO) >> (8 * par)) & 0xFF
            bloco = criptograma[inicio:inicio + BLOCO]
            alto = bloco[4 - par] if len(bloco) > 4 - par else None
            baixo = bloco[9 - par] if len(bloco) > 9 - par else None
            amostras.append((esquerda, direita, alto, baixo))

    base = (8 * par - 7) % HALF_SIZE
    resultados = []
    for valor in range(1 << JANELA):
        u = rotl(valor, base, HALF_SIZE)
        subchaves = subchaves_do_par(u, par)
        claro = bytearray()
        cache = {}
        for esquerda, direita, alto, baixo in amostras:
            if (esquerda, direita) not in cache:
                cache[(esquerda, direita)] = keystream_par(tabela, subchaves, esquerda, direita)
            k_alto, k_baixo = cache[(esquerda, direita)]
            if alto is not None:
                claro.append(alto ^ k_alto)
            if baixo is not None:
                claro.append(baixo ^ k_baixo)
        resultados.append((pontuar(claro), valor, bytes(claro)))
    resultados.sort(reverse=True)
    return base, resultados


def combinar(janelas):
    def encaixa(u, mascara, base, valor):
        bits = rotl(valor, base, HALF_SIZE)
        janela = rotl((1 << JANELA) - 1, base, HALF_SIZE)
        return (u ^ bits) & mascara & janela == 0, u | bits, mascara | janela

    melhor = None

    def busca(par, u, mascara, pontos):
        nonlocal melhor
        if par == len(janelas):
            if melhor is None or pontos > melhor[0]:
                melhor = (pontos, u)
            return
        base, candidatos = janelas[par]
        teto = candidatos[0][0]
        for pontos_janela, valor, _ in candidatos:
            if pontos_janela < teto - 25:
                break
            ok, novo_u, nova_mascara = encaixa(u, mascara, base, valor)
            if ok:
                busca(par + 1, novo_u, nova_mascara, pontos + pontos_janela)

    busca(0, 0, 0, 0.0)
    return melhor


if __name__ == "__main__":
    projeto = carregar_projeto("F01")
    textos = mensagens("F01")
    tabela = tabela_f(projeto)

    janelas = []
    for par in range(HALF_SIZE // 8):
        base, resultados = atacar_par(tabela, textos, par)
        janelas.append((base, resultados))
        teto = resultados[0][0]
        empatados = len({claro for pontos, _, claro in resultados if pontos == teto})
        segundo = next((pontos for pontos, _, _ in resultados if pontos < teto), teto)
        print(f"par {par} (bytes {4 - par} e {9 - par} do bloco, bits {base}..{(base + JANELA - 1) % HALF_SIZE} de u): "
              f"melhor {teto:.1f}, segundo {segundo:.1f}, textos distintos no topo {empatados}, "
              f"amostra '{legivel(resultados[0][2])}'")

    pontos, u = combinar(janelas)
    print(f"\nu = alta xor baixa da chave = 0x{u:010x} (pontuação total {pontos:.1f})")

    projeto.MASTER_KEY = u
    cifra = feistel.Feistel80.from_design(projeto)
    print(f"chave equivalente usada no ctr.py: 0x{u:020x}\n")
    for indice, (nonce, criptograma) in enumerate(textos, start=1):
        claro = ctr.apply_ctr(cifra, nonce, criptograma)
        print(f"mensagem {indice}: {claro.decode('utf-8', errors='replace')!r}")
