# Tirar dúvida com o professor:
# 1- O tamanho dos blocos da memória principal devem ser do tipo 2^n? Para que nenhum bit
# seja disperdiçado ao estruturar as palavras da cache?
# 2- É necessário exibir o carregamento das palavras para uma linha cache?

from sys import argv
import io
import math

NUM_BITS_END = 32 # Constante

# Deverão ser entradas:
TAM_LINHA_CACHE = 16 # Tamanho do bloco da Memória Principal

NUM_BITS_LINHA_CACHE = int(math.log(TAM_LINHA_CACHE, 2))
NUM_BITS_TAG = NUM_BITS_END - NUM_BITS_LINHA_CACHE

NUM_LINHAS_CACHE = 4

NUM_PROCESSADORES = 7

SUBSTITUICAO = 0
# 0: LRU (Não teve acesso por mais tempo)
# 1: FIFO (Fila)

class Cache:
    linhas_cache: dict
    lista_subs: list[str]

    def __init__(self):
        self.linhas_cache = {}
        self.lista_subs = []

# Função Principal ------------------------------------------------------

def main() -> None:
    '''
    Função principal do programa.
    '''
    if len(argv) == 3:
        try:
            arq_entrada = open(argv[2], 'r')
        except FileNotFoundError:
            print('\nERRO: Arquivo de entrada não encontrado.')
        else:
            # Código de simulação
            simulador_mesi(arq_entrada)
    else:
        print('\nERRO: Número de argumentos inválido.')
        print('Modo de uso: python trabalho.py nome_arquivo_entrada')

# Função de Simulação --------------------------------------------------

def simulador_mesi(arq_entrada: io.TextIOWrapper) -> None:
    campos = arq_entrada.readline().split()
    while len(campos) > 0:
        proc, oper, ender = campos[0], campos[1], campos[2]

def inicia_caches() -> list[Cache]:
    '''
    Inicia os processadores e suas memórias caches para a simulação.
    '''
    caches = []
    for n in range(NUM_PROCESSADORES):
        caches.append(Cache())
    return caches

# Funções de gerenciamento da Memória Cache Privada

def cache_hit(cache: Cache, endereco: str) -> None:
    '''
    Trata um cache-hit que ocorreu na *cache*.
    '''
    if SUBSTITUICAO == 0:
        cache.lista_subs.remove(endereco[:NUM_BITS_TAG])
        cache.lista_subs.append(endereco[:NUM_BITS_TAG])

def cache_miss(cache: Cache, endereco: str) -> None:
    '''
    Trata um cache-miss que ocorreu na *cache*, carregando o *endereco* nela.
    '''
    if len(cache.linhas_cache) < NUM_LINHAS_CACHE:
        cache.lista_subs.append(endereco[:NUM_BITS_TAG])
        cache.linhas_cache[endereco[:NUM_BITS_TAG]] = carrega_bloco()
    else:
        substituicao(cache, endereco)
    return None

def substituicao(cache: Cache, endereco: str):
    '''
    Realiza uma substituição na memória *cache* para carregar o bloco do *endereço*.
    '''
    tag = cache.lista_subs.pop(0)
    cache.linhas_cache.pop(tag)
    cache.lista_subs.append(endereco[:NUM_BITS_TAG])
    cache.linhas_cache[endereco[:NUM_BITS_TAG]] = carrega_bloco()
    return None

def carrega_bloco() -> list[str]:
    '''
    Carrega as palavras de um bloco da memória principal na memória cache.
    '''
    palavras = []
    i = 0
    while i < TAM_LINHA_CACHE:
        palavras.append(bin(i)[2:].zfill(NUM_BITS_LINHA_CACHE))
        i += 1
    return palavras

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

def visualizar_enderecos():
    arq = open('small2.data', 'r')
    linha = arq.readline()
    while linha:
        endereco = linha.split()[2]
        print(endereco)
        # 16: Interpretação como hexadecimal
        # 32: Quantidade de bits utilizados para endereçamento
        print(bin(int(endereco, 16))[2:].zfill(32))
        linha = arq.readline()
    arq.close()

def testa_substituicao_e_cache_miss():
    end1 = '01111100010110010000010000000000'
    end2 = '00111100010101010000010000000000'
    end3 = '00011100010101000000010000000000'
    end4 = '00001100010101000000010000000000'
    end5 = '00000100010101000000010000000000'

    print('\nCriação da cache')
    cache = Cache()
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)
    print('\nInserção do primeiro endereço: ' + end1)
    cache_miss(cache, end1)
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)
    print('\nInserção do segundo endereço: ' + end2)
    cache_miss(cache, end2)
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)
    print('\nInserção do terceiro endereço: ' + end3)
    cache_miss(cache, end3)
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)
    print('\nInserção do quarto endereço: ' + end4)
    cache_miss(cache, end4)
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)
    print('\nInserção do quinto endereço: ' + end5)
    cache_miss(cache, end5)
    print('Linhas:')
    print(cache.linhas_cache)
    print('Lista de substituição:')
    print(cache.lista_subs)

def teste():
    ...

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

# Início do Programa ---------------------------------------------------

if __name__ == "__main__":
    teste()