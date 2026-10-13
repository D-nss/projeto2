import os
import random
import importlib.util
import spn
import feistel

def importar_cifra(identificador):
    pasta_origem = 'SPN'
    if identificador.startswith('F'):
        pasta_origem = 'Rede de Feistel'

    caminho_arquivo = os.path.join(pasta_origem, identificador, 'my_cipher.py')
    especificacao = importlib.util.spec_from_file_location("modulo_cifra", caminho_arquivo)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)

    chave_mestra = 0x23453456343453450124
    caixa_s = modulo.SBOX
    
    caixa_p = modulo.FEISTEL_PBOX
    if identificador.startswith('S'):
        caixa_p = modulo.SPN_PBOX

    return caixa_s, caixa_p, chave_mestra

def analisar_efeito_avalanche(identificador, caixa_s, caixa_p, chave, rodadas, total_amostras=30):
    if identificador.startswith('S'):
        cifra = spn.SPN80(caixa_s, caixa_p, rodadas, chave)
    else:
        cifra = feistel.Feistel80(caixa_s, caixa_p, rodadas, chave)

    taxas_alteracao = []
    dependencias = [[0] * 80 for _ in range(80)]

    for k in range(total_amostras):
        texto_claro = random.getrandbits(80)
        texto_cifrado_base = cifra.encrypt_block(texto_claro)

        for indice_bit in range(80):
            texto_cifrado_modificado = cifra.encrypt_block(texto_claro ^ (1 << indice_bit))
            diferenca = texto_cifrado_base ^ texto_cifrado_modificado
            
            bits_diferentes = bin(diferenca).count('1')
            taxas_alteracao.append(bits_diferentes / 80)

            for bit_alvo in range(80):
                if (diferenca >> bit_alvo) & 1:
                    dependencias[indice_bit][bit_alvo] += 1

    bits_inalterados = 0
    for linha in range(80):
        for coluna in range(80):
            if dependencias[linha][coluna] == 0:
                bits_inalterados += 1

    total_taxas = len(taxas_alteracao)
    media_geral = sum(taxas_alteracao) / total_taxas
    variancia = sum((valor - media_geral) ** 2 for valor in taxas_alteracao) / total_taxas
    desvio_padrao = variancia ** 0.5

    return media_geral, desvio_padrao, bits_inalterados

def calcular_estatisticas(texto_cifrado_hexa):
    valor_inteiro = int(texto_cifrado_hexa, 16)
    tamanho_desejado = len(texto_cifrado_hexa) * 4
    sequencia_bits = bin(valor_inteiro)[2:].zfill(tamanho_desejado)
    
    tamanho_total = len(sequencia_bits)
    media_peso_hamming = sequencia_bits.count('1') / tamanho_total

    contagem_sequencias = [1]
    for i in range(1, tamanho_total):
        if sequencia_bits[i] == sequencia_bits[i-1]:
            contagem_sequencias[-1] += 1
        else:
            contagem_sequencias.append(1)

    total_grupos = len(contagem_sequencias)
    media_sequencias = sum(contagem_sequencias) / total_grupos
    variancia_seq = sum((x - media_sequencias) ** 2 for x in contagem_sequencias) / total_grupos
    desvio_sequencias = variancia_seq ** 0.5

    zeros = sequencia_bits.count('0')
    uns = sequencia_bits.count('1')
    valor_esperado = tamanho_total / 2

    qui_quadrado = ((zeros - valor_esperado) ** 2 / valor_esperado) + ((uns - valor_esperado) ** 2 / valor_esperado)

    return media_peso_hamming, desvio_sequencias, qui_quadrado

if __name__ == "__main__":
    dados_teste = {
        "F01": ["2312", "3f82d9592c02", "23ad2dd622003772f51825ad2dd6280037"],
        "S01": ["f20b4ee2a94adef11faba11de987fc1f9a5a0d94e047dabda34cdb5254"],
        "S02": ["8dd53187c5733c9d730dac943dc8cd7268967c06e3d231ce807e3a917ca5a2"]
    }
    
    for identificador in ["F01", "S01", "S02"]:
        print(f"\n--- {identificador} ---")
        
        caixa_s, caixa_p, chave = importar_cifra(identificador)
        
        print("[ Efeito Avalanche ]")
        for rodada in range(1, 9):
            med, dp, nao_modficados = analisar_efeito_avalanche(
                identificador, caixa_s, caixa_p, chave, rodada
            )
            print(f" R{rodada}: Med={med:.4f} | Desvio={dp:.4f} | Não modificados={nao_modficados}")
            
        print("[ Testes Estatísticos ]")
        textos_cifrados = dados_teste.get(identificador, [])
        for indice, texto in enumerate(textos_cifrados):
            hw, dp_seq, qui2 = calcular_estatisticas(texto)
            print(f" CT{indice+1}: Média_HW={hw:.4f} | DP_Corridas={dp_seq:.4f} | Qui-Quadrado={qui2:.4f}")