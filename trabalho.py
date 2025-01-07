# Tirar dúvida com o professor:
# 1- O tamanho dos blocos da memória principal devem ser do tipo 2^n? Para que nenhum bit
# seja disperdiçado ao estruturar as palavras da cache?
# 2- Como determinar o tamanho da memória principal e da memória cache compartilhada?

from dataclasses import dataclass
from sys import argv
import io
import math

NUM_BITS_END = 32 # Constante

# Deverão ser entradas:
TAM_LINHA_CACHE = 16 # Tamanho do bloco da Memória Principal

NUM_BITS_LINHA_CACHE = int(math.log(TAM_LINHA_CACHE, 2))
NUM_BITS_TAG = NUM_BITS_END - NUM_BITS_LINHA_CACHE

NUM_LINHAS_CACHE_PRIVADA = 4
NUM_LINHAS_CACHE_COMPARTILHADA = NUM_LINHAS_CACHE_PRIVADA * 2
NUM_BLOCOS_MEMORIA_PRINCIPAL = NUM_LINHAS_CACHE_COMPARTILHADA * 2

NUM_PROCESSADORES = 7

SUBSTITUICAO = 0
# 0: LRU (Não teve acesso por mais tempo)
# 1: FIFO (Fila)

class MemoriaPrincipal:
    '''
    Representa uma Memória Principal
    '''
    blocos: dict # {Tag do bloco: [Últimos bits dos endereços do bloco]}
    tamanho_blocos: int # Guarda o tamanho dos blocos da memória principal
    quantidade_blocos: int # Quantidade de blocos da memória principal

    def __init__(self, tamanho_blocos, quantidade_blocos):
        self.blocos = {}
        self.tamanho_blocos = tamanho_blocos
        self.quantidade_blocos = quantidade_blocos

class CacheCompartilhada:
    '''
    Representa uma Memória Cache Compartilhada
    '''
    linhas_cache: dict # {Tag do bloco: [Últimos bits dos endereços do bloco]}
    lista_subs: list[str] # Lista de substituição
    numero_bits_tag: int # Número de bits da tag
    tamanho_linhas: int # Tamanho do bloco da Memória Principal, ou seja, da linha da cache
    quantidade_linhas: int # Quantidade de linhas da cache
    substituicao: int # 0: LRU; 1: FIFO

    def __init__(self, tamanho_linhas, numero_bits_tag, quantidade_linhas, substituicao):
        self.linhas_cache = {}
        self.lista_subs = []
        self.numero_bits_tag = numero_bits_tag
        self.tamanho_linhas = tamanho_linhas
        self.quantidade_linhas = quantidade_linhas
        self.substituicao = substituicao
    
    def cache_hit(self, endereco: str) -> None:
        '''
        Operação de Cache Hit na Cache Compartilhada
        '''
        # Manutenção das posições de substituição
        if self.substituicao == 0:
            self.lista_subs.remove(endereco[:self.numero_bits_tag])
            self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None
    
    def cache_miss(self, endereco: str, memoriaPrincipal: MemoriaPrincipal) -> None:
        '''
        Operação de Cache Miss na Cache Compartilhada
        '''
        # Verificação da quantidade de linhas presentes na cache
        if len(self.lista_subs) == self.quantidade_linhas:
            # Remoção de um bloco para substituição
            tag_rem = self.lista_subs.pop(0)
            self.linhas_cache.pop(tag_rem)
        self.linhas_cache[endereco[:self.numero_bits_tag]] = __carrega_bloco_provisorio__(self.tamanho_linhas, 32 - self.numero_bits_tag)
        self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None

class CachePrivadaInstrucoes:
    '''
    Representa uma Memória Cache Privada de Instruções
    '''
    linhas_cache: dict # {Tag do bloco: [Últimos bits dos endereços do bloco]}
    lista_subs: list[str] # Lista de substituição
    numero_bits_tag: int # Número de bits da tag
    tamanho_linhas: int # Tamanho do bloco da Memória Principal, ou seja, da linha da cache
    quantidade_linhas: int # Quantidade de linhas da cache
    substituicao: int # 0: LRU; 1: FIFO

    def __init__(self, tamanho_linhas, numero_bits_tag, quantidade_linhas, substituicao):
        self.linhas_cache = {}
        self.lista_subs = []
        self.numero_bits_tag = numero_bits_tag
        self.tamanho_linhas = tamanho_linhas
        self.quantidade_linhas = quantidade_linhas
        self.substituicao = substituicao

    def cache_hit(self, endereco: str) -> None:
        '''
        Operação de Cache Hit na Cache Privada de Instruções
        '''
        # Manutenção das posições de substituição
        if self.substituicao == 0:
            self.lista_subs.remove(endereco[:self.numero_bits_tag])
            self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None

    def cache_miss(self, endereco: str, cacheCompartilhada: CacheCompartilhada, memoriaPrincipal: MemoriaPrincipal) -> None:
        '''
        Operação de Cache Miss na Cache Privada de Instruções
        '''
        # Verificação do bloco na Memória Cache Compartilhada
        if endereco[:self.numero_bits_tag] not in cacheCompartilhada.linhas_cache:
            cacheCompartilhada.cache_miss(endereco[:self.numero_bits_tag], memoriaPrincipal)
        else:
            cacheCompartilhada.cache_hit(endereco[:self.numero_bits_tag])
        # Verificação da quantidade de linhas presentes na cache
        if len(self.lista_subs) == self.quantidade_linhas:
            # Remoção de um bloco para substituição
            tag_rem = self.lista_subs.pop(0)
            self.linhas_cache.pop(tag_rem)
        self.linhas_cache[endereco[:self.numero_bits_tag]] = cacheCompartilhada.linhas_cache[endereco[:self.numero_bits_tag]]
        self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None

@dataclass
class Bloco_Cache_Privada_Dados:
    '''
    Representa um bloco presente em uma linha de uma Memória Cache Privada de Dados
    '''
    palavras: list[str] # últimos bits dos endereços do bloco na memória cache privada de dados
    estado: str # Representa o estado MESI do bloco na memória cache privada de dados

class CachePrivadaDados:
    '''
    Representa uma Memória Cache Privada de Dados
    '''
    linhas_cache: dict # {Tag do bloco: Bloco_Cache_Privada_Dados([Últimos bits dos endereços do bloco], Estado MESI do Bloco)}
    lista_subs: list[str] # Lista para substituição
    tamanho_linhas: int # Tamanho do bloco da Memória Principal, ou seja, da linha da cache
    numero_bits_tag: int # Número de bits da tag
    quantidade_linhas: int # Quantidade de linhas da cache
    substituicao: int # 0: LRU; 1: FIFO

    def __init__(self, tamanho_linhas: int, numero_bits_tag: int, quantidade_linhas: int, substituicao: int):
        self.linhas_cache = {}
        self.lista_subs = []
        self.tamanho_linhas = tamanho_linhas
        self.numero_bits_tag = numero_bits_tag
        self.quantidade_linhas = quantidade_linhas
        self.substituicao = substituicao

    def cache_hit(self, endereco: str) -> None:
        '''
        Operação de Cache Hit na Cache Privada de Dados
        '''
        # Manutenção das posições de substituição
        if self.substituicao == 0:
            self.lista_subs.remove(endereco[:self.numero_bits_tag])
            self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None

    def cache_miss(self, endereco: str, estado: str, cacheCompartilhada: CacheCompartilhada, memoriaPrincipal: MemoriaPrincipal) -> None:
        '''
        Operação de Cache Miss na Cache Privada de Dados
        '''
        # Verificação do bloco na Memória Cache Compartilhada
        if endereco[:self.numero_bits_tag] not in cacheCompartilhada.linhas_cache:
            cacheCompartilhada.cache_miss(endereco[:self.numero_bits_tag], memoriaPrincipal)
        else:
            cacheCompartilhada.cache_hit(endereco[:self.numero_bits_tag])
        # Verificação da quantidade de linhas presentes na cache
        if len(self.lista_subs) == self.quantidade_linhas:
            # Remoção de um bloco para substituição
            tag_rem = self.lista_subs.pop(0)
            self.linhas_cache.pop(tag_rem)
        self.linhas_cache[endereco[:self.numero_bits_tag]] = Bloco_Cache_Privada_Dados(cacheCompartilhada.linhas_cache[endereco[:self.numero_bits_tag]], estado)
        self.lista_subs.append(endereco[:self.numero_bits_tag])
        return None

# -------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------
def __carrega_bloco_provisorio__(tamanho_linha: int, numero_bits_linha_cache) -> list[str]:
    '''
    PROVISÓRIO: LACUNA NA REPRESENTAÇÃO DA MEMÓRIA PRINCIPAL
    Simula o carregamento de um bloco da memória principal na memória cache.
    '''
    palavras = []
    palavra = 0
    while palavra < tamanho_linha:
        palavras.append(bin(palavra)[2:].zfill(numero_bits_linha_cache))
        palavra += 1
    return palavras
# -------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------

# Função Principal ------------------------------------------------------

def main() -> None:
    '''
    Função principal do programa.
    '''
    if len(argv) == 3:
        try:
            arq_conf = open(argv[1], 'r')
        except FileNotFoundError:
            print('\nERRO: Arquivo de entrada não encontrado.')
        else:
            try:
                arq_entrada = open(argv[2], 'r')
            except FileNotFoundError:
                print('\nERRO: Arquivo de entrada não encontrado.')
            else:
                tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, quantidade_blocos_memoria_principal, numero_processadores, politica_substituicao, numero_bits_tag = le_configuracao(arq_conf)
                simulador_mesi(tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, quantidade_blocos_memoria_principal, numero_processadores, politica_substituicao, numero_bits_tag, arq_entrada)
    else:
        print('\nERRO: Número de argumentos inválido.')
        print('Modo de uso: python trabalho.py nome_arquivo_configuracao nome_arquivo_entrada')

# Função de Simulação ---------------------------------------------------

def le_configuracao(arq_cong: io.TextIOWrapper) -> tuple:
    '''
    Lê o arquivo de configuração e retorna as configurações da simulação.
    '''
    tamanho_bloco = int(arq_cong.readline())
    tamanho_cache_privada = int(arq_cong.readline())
    tamanho_cache_compartilhada = int(arq_cong.readline())
    quantidade_blocos_memoria_principal = int(arq_cong.readline())
    numero_processadores = int(arq_cong.readline())
    politica_substituicao = int(arq_cong.readline())
    numero_bits_tag = 32 - int(math.log(TAM_LINHA_CACHE, 2))
    arq_cong.close()
    return tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, quantidade_blocos_memoria_principal, numero_processadores, politica_substituicao, numero_bits_tag

def simulador_mesi(tamanho_bloco: int, tamanho_cache_privada: int, tamanho_cache_compartilhada: int, quantidade_blocos_memoria_principal: int, numero_processadores: int, politica_substituicao: int, numero_bits_tag: int, arq_entrada: io.TextIOWrapper) -> None:
    '''
    Realiza a simulação de um protocolo MESI em um multiprocessador a partir das configurações passadas.
    '''
    # Inicia o sistema de memórias
    cachesPrivadasDados, cachesPrivadasInstrucoes, cacheCompartilhada, memoriaPrincipal = inicia_sistema_memoria(tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, quantidade_blocos_memoria_principal, numero_processadores, politica_substituicao, numero_bits_tag)
    # Iniciando a construção do Log
    log = arq.open('simulador.log', 'w')

    # Acesso à memória
    entrada = arq_entrada.readline().split()
    while len(entrada) > 0:
        processador, instrucao, endereco = int(entrada[0]), entrada[1], bin(int(entrada[2], 16))[2:].zfill(32)
        # Leitura de instrução
        if instrucao == '0':
            if endereco[:numero_bits_tag] in cachesPrivadasInstrucoes[processador].linhas_cache:
                # Cache Hit
                print(f"Cache hit for instruction processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasInstrucoes[processador].cache_hit(endereco)
            else:
                # Cache Miss
                print(f"Cache miss for instruction processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasInstrucoes[processador].cache_miss(endereco, cacheCompartilhada, memoriaPrincipal)
        # Leitura de dado
        elif instrucao == '2':
            if endereco[:numero_bits_tag] in cachesPrivadasDados[processador].linhas_cache:
                # Cache Hit
                print(f"R - Cache hit for data processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasDados[processador].cache_hit(endereco)
                if endereco[:numero_bits_tag] in cachesPrivadasDados[proc].linhas_cache and cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado != 'M' and cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado != 'S':
                    cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado = 'E'
            else:
                # Cache Miss
                print(f"R - Cache miss for data processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasDados[processador].cache_miss(endereco, 'E', cacheCompartilhada, memoriaPrincipal)
            # Alteração do estado do bloco do endereço nas demais caches
            for proc in range(numero_processadores):
                if proc != processador and endereco[:numero_bits_tag] in cachesPrivadasDados[proc].linhas_cache and cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado != 'I':
                    cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado = 'S'
        # Escrita de dado
        elif instrucao == '3':
            if endereco[:numero_bits_tag] in cachesPrivadasDados[processador].linhas_cache:
                # Cache Hit
                print(f"W - Cache hit for data processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasDados[processador].cache_hit(endereco)
                cachesPrivadasDados[processador].linhas_cache[endereco[:numero_bits_tag]].estado = 'M'
            else:
                # Cache Miss
                print(f"W - Cache miss data for processor {processador} on address {endereco[:numero_bits_tag]}")
                cachesPrivadasDados[processador].cache_miss(endereco, 'M', cacheCompartilhada, memoriaPrincipal)
            # Alteração do estado do bloco do endereço nas demais caches
            for proc in range(numero_processadores):
                if proc != processador and endereco[:numero_bits_tag] in cachesPrivadasDados[proc].linhas_cache:
                    cachesPrivadasDados[processador].linhas_cache[endereco[:numero_bits_tag]].estado = 'I'
        # Operação não identificada
        else:
            print('ERRO: Operação não identificada!')
        entrada = arq_entrada.readline().split()
    arq_entrada.close()
    log.close()
    return None

def inicia_sistema_memoria(tamanho_bloco: int, tamanho_cache_privada: int, tamanho_cache_compartilhada: int, quantidade_blocos_memoria_principal: int, numero_processadores: int, politica_substituicao: int, numero_bits_tag: int) -> tuple:
    '''
    Inicia o sistema de memória a partir das configurações passadas.
    '''
    # Iniciando as caches privadas de dados.
    cachesPrivadasDados = []
    cachesPrivadasInstrucoes = []
    for _ in range(numero_processadores):
        cachesPrivadasDados.append(CachePrivadaDados(tamanho_bloco, numero_bits_tag, tamanho_cache_privada, politica_substituicao))
        cachesPrivadasInstrucoes.append(CachePrivadaInstrucoes(tamanho_bloco, numero_bits_tag, tamanho_cache_privada, politica_substituicao))
    # Iniciando a cache compartilhada.
    cacheCompartilhada = CacheCompartilhada(tamanho_bloco, numero_bits_tag, tamanho_cache_compartilhada, politica_substituicao)
    # Iniciando a memória principal.
    memoriaPrincipal = MemoriaPrincipal(tamanho_bloco, quantidade_blocos_memoria_principal)
    return cachesPrivadasDados, cachesPrivadasInstrucoes, cacheCompartilhada, memoriaPrincipal

# Funções de console e log ----------------------------------------------



# Início do Programa ----------------------------------------------------

if __name__ == "__main__":
    main()