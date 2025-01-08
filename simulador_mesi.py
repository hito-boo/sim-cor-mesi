# Simulador de Coerência MESI
# Aluno: Vitor da Rocha Machado (RA: 132769)

from dataclasses import dataclass
from sys import argv
import codecs
import io
import math

class MemoriaPrincipal:
    '''
    Representa uma Memória Principal
    '''

    def carrega_bloco(self, tamanho_linha: int, numero_bits_linha_cache) -> list[str]:
        '''
        Simula o carregamento de um bloco da memória principal na memória cache.
        '''
        palavras = []
        palavra = 0
        while palavra < tamanho_linha:
            palavras.append(bin(palavra)[2:].zfill(numero_bits_linha_cache))
            palavra += 1
        return palavras

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
        self.linhas_cache[endereco[:self.numero_bits_tag]] = memoriaPrincipal.carrega_bloco(self.tamanho_linhas, 32 - self.numero_bits_tag)
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
                tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, numero_processadores, politica_substituicao, numero_bits_tag = le_configuracao(arq_conf)
                simulador_mesi(tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, numero_processadores, politica_substituicao, numero_bits_tag, arq_entrada)
    else:
        print('\nERRO: Número de argumentos inválido.')
        print('Modo de uso: python trabalho.py nome_arquivo_configuracao nome_arquivo_entrada')

# Função de Simulação ---------------------------------------------------

def le_configuracao(arq_cong: io.TextIOWrapper) -> tuple:
    '''
    Lê o arquivo de configuração e retorna as configurações da simulação.
    '''
    try:
        tamanho_bloco = int(arq_cong.readline())
        tamanho_cache_privada = int(arq_cong.readline())
        tamanho_cache_compartilhada = int(arq_cong.readline())
        numero_processadores = int(arq_cong.readline())
        politica_substituicao = int(arq_cong.readline())
    except:
        raise ValueError('ERRO: Leitura das configurações inválida - Colocar apenas um número inteiro por linha!')
    else:
        if tamanho_bloco <= 0:
            raise ValueError('ERRO: Valor inválido para tamanho de bloco!')
        elif tamanho_cache_privada <= 0:
            raise ValueError('ERRO: Valor inválido para quantidade de linhas nas Memórias Caches Privadas!')
        elif tamanho_cache_compartilhada <= 0:
            raise ValueError('ERRO: Valor inválido para quantidade de linhas na Memória Cache Compartilhada!')
        elif numero_processadores <= 0:
            raise ValueError('ERRO: Valor inválido para número de processadores!')
        elif politica_substituicao != 0 and politica_substituicao != 1:
            raise ValueError('ERRO: Valor inválido para política de substituição - Deve ser 0 (LRU) ou 1 (FIFO)!')
        elif tamanho_cache_privada >= tamanho_cache_compartilhada:
            raise ValueError('ERRO: Tamanho das Memórias Caches Privadas deve ser menor que o tamanho da Memória Cache Compartilhada!')
        numero_bits_tag = 32 - int(math.log(tamanho_bloco, 2))
        arq_cong.close()
    return tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, numero_processadores, politica_substituicao, numero_bits_tag

def simulador_mesi(tamanho_bloco: int, tamanho_cache_privada: int, tamanho_cache_compartilhada: int, numero_processadores: int, politica_substituicao: int, numero_bits_tag: int, arq_entrada: io.TextIOWrapper) -> None:
    '''
    Realiza a simulação de um protocolo MESI em um multiprocessador a partir das configurações passadas.
    '''
    # Iniciando a construção do Log
    log = codecs.open('simulador.txt', 'w', 'utf-8')
    console_configuracao(log, tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, numero_processadores, politica_substituicao)
    # Inicia o sistema de memórias
    cachesPrivadasDados, cachesPrivadasInstrucoes, cacheCompartilhada, memoriaPrincipal = inicia_sistema_memoria(tamanho_bloco, tamanho_cache_privada, tamanho_cache_compartilhada, numero_processadores, politica_substituicao, numero_bits_tag)
    print('\nSistema de Memória Criado\n')
    log.write('\nSistema de Memória Criado\n')
    console_sistema_memoria(log, cacheCompartilhada, cachesPrivadasInstrucoes, cachesPrivadasDados)
    # Acesso à memória
    entrada = arq_entrada.readline().split()
    while len(entrada) > 0:
        processador, tipo_operacao, endereco = int(entrada[0]), entrada[1], bin(int(entrada[2], 16))[2:].zfill(32)
        console_acesso(log, processador, tipo_operacao, endereco)
        # ERRO: Processador fora de alcance!
        if processador >= len(cachesPrivadasDados):
            raise ValueError('ERRO: Processador fora de alcance!')
        # Leitura de instrução
        elif tipo_operacao == '0':
            if endereco[:numero_bits_tag] in cachesPrivadasInstrucoes[processador].linhas_cache:
                # Cache Hit
                cachesPrivadasInstrucoes[processador].cache_hit(endereco)
                log.write('BARRAMENTO: Cache Hit para leitura de instrução.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Hit para leitura de instrução.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
            else:
                # Cache Miss
                cachesPrivadasInstrucoes[processador].cache_miss(endereco, cacheCompartilhada, memoriaPrincipal)
                log.write('BARRAMENTO: Cache Miss para leitura de instrução.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Miss para leitura de instrução.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
        # Leitura de dado
        elif tipo_operacao == '2':
            if endereco[:numero_bits_tag] in cachesPrivadasDados[processador].linhas_cache:
                # Cache Hit
                cachesPrivadasDados[processador].cache_hit(endereco)
                cachesPrivadasDados[processador].linhas_cache[endereco[:numero_bits_tag]].estado = 'E'
                log.write('BARRAMENTO: Cache Hit para leitura de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Hit para leitura de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
            else:
                # Cache Miss
                # Entra como 'Bloco Exclusivo', provisoriamente (há a verificação da presença do bloco nas demais caches logo após a entrada do bloco)
                cachesPrivadasDados[processador].cache_miss(endereco, 'E', cacheCompartilhada, memoriaPrincipal)
                log.write('BARRAMENTO: Cache Miss para leitura de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Miss para leitura de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
            # Alteração do estado do bloco do endereço nas demais caches
            presente_em_outro_proc = False
            for proc in range(len(cachesPrivadasDados)):
                if proc != processador and endereco[:numero_bits_tag] in cachesPrivadasDados[proc].linhas_cache and cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado != 'I':
                    presente_em_outro_proc = True
                    if (cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado == 'M' or cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado == 'E'):
                        cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado = 'S'
            # Correção do Estado no Processador
            if presente_em_outro_proc:
                cachesPrivadasDados[processador].linhas_cache[endereco[:numero_bits_tag]].estado = 'S'
        # Escrita de dado
        elif tipo_operacao == '3':
            if endereco[:numero_bits_tag] in cachesPrivadasDados[processador].linhas_cache:
                # Cache Hit
                cachesPrivadasDados[processador].cache_hit(endereco)
                log.write('BARRAMENTO: Cache Hit para escrita de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Hit para escrita de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                cachesPrivadasDados[processador].linhas_cache[endereco[:numero_bits_tag]].estado = 'M'
            else:
                # Cache Miss
                log.write('BARRAMENTO: Cache Miss para escrita de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                print('BARRAMENTO: Cache Miss para escrita de dado.\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n')
                cachesPrivadasDados[processador].cache_miss(endereco, 'M', cacheCompartilhada, memoriaPrincipal)
            # Alteração do estado do bloco do endereço nas demais caches
            for proc in range(len(cachesPrivadasDados)):
                if proc != processador and endereco[:numero_bits_tag] in cachesPrivadasDados[proc].linhas_cache:
                    cachesPrivadasDados[proc].linhas_cache[endereco[:numero_bits_tag]].estado = 'I'
        # Operação não identificada
        else:
            print('ERRO: Operação não identificada!')
        console_sistema_memoria(log, cacheCompartilhada, cachesPrivadasInstrucoes, cachesPrivadasDados)
        entrada = arq_entrada.readline().split()
    arq_entrada.close()
    log.close()
    return None

def inicia_sistema_memoria(tamanho_bloco: int, tamanho_cache_privada: int, tamanho_cache_compartilhada: int, numero_processadores: int, politica_substituicao: int, numero_bits_tag: int) -> tuple:
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
    memoriaPrincipal = MemoriaPrincipal()
    return cachesPrivadasDados, cachesPrivadasInstrucoes, cacheCompartilhada, memoriaPrincipal

# Funções de console e log ----------------------------------------------

def console_configuracao(log: io.TextIOWrapper, tamanho_bloco: int, tamanho_cache_privada: int, tamanho_cache_compartilhada: int, numero_processadores: int, politica_substituicao: int) -> None:
    '''
    Cria o texto de console da configuração utilizada na simulação.
    '''
    texto = 'Configuração da Simulação\n'
    texto += 'Tamanho do Bloco de Memória: ' + str(tamanho_bloco) + ' palavras.\n'
    texto += 'Quantidade de Bits necessários para mapeamento do bloco: ' + str(32 - int(math.log(tamanho_bloco, 2))) + ' Bits.\n'
    texto += 'Quantidade de linhas presentes nas Memórias Caches Privadas: ' + str(tamanho_cache_privada) + ' linhas.\n'
    texto += 'Quantidade de linhas presentes na Memória Cache Compartilhada: ' + str(tamanho_cache_compartilhada) + ' linhas.\n'
    texto += 'Quantidade de processadores: ' + str(numero_processadores) + ' processadores.\n'
    if politica_substituicao == 0:
        texto += 'Política de Substituição: 0 - Least Recently Used (LRU - Menos Usado Recentemente)\n'
    elif politica_substituicao == 1:
        texto += 'Política de Substituição: 1 - First In First Out (FIFO - Primeiro a entrar é o primeiro a sair; fila)\n'
    else:
        texto += 'ERRO: POLÍTICA DE SUBSTITUIÇÃO INVÁLIDA! 0- LRU; 1- FIFO\n'
    print(texto)
    log.write(texto)
    return None

def console_acesso(log: io.TextIOWrapper, processador: int, tipo_operacao: str, endereco: str) -> None:
    '''
    Cria o texto de console do acesso realizado pelos multiprocessadores.
    '''
    texto = '---------------------------------------------------------------------------------------------------------------------------------------------------------\n'
    texto += '---------------------------------------------------------------------------------------------------------------------------------------------------------\n'
    texto += 'Processador Id. ' + str(processador) + ' - ' + tipo_operacao
    if tipo_operacao == '0':
        texto += ' (Operação de Leitura de Instrução) - Endereço: ' + endereco + '\n'
    elif tipo_operacao == '2':
        texto += ' (Operação de Leitura de Dado) - Endereço ' + endereco + '\n'
    elif tipo_operacao == '3':
        texto += ' (Operação de Escrita de Dado) - Endereço ' + endereco + '\n'
    else:
        texto += 'ERRO: OPERAÇÃO NÃO RECONHECIDA!\n'
    texto += '---------------------------------------------------------------------------------------------------------------------------------------------------------\n'
    texto += '---------------------------------------------------------------------------------------------------------------------------------------------------------\n'
    print(texto)
    log.write(texto)
    return None

def console_sistema_memoria(log: io.TextIOWrapper, cacheCompartilhada: CacheCompartilhada, cachesPrivadasInstrucoes: list[CachePrivadaInstrucoes], cachesPrivadasDados: list[CachePrivadaDados]) -> None:
    '''
    Cria o texto de console exibindo o estado do sistema de memória.
    '''
    print('\nMemória Cache Compartilhada -------------------------------------------------------------------------------------------------------------------------------------\n')
    log.write('\nMemória Cache Compartilhada -----------------------------------------------------------------------------------------------------------------------------\n')
    console_cache_compartilhada(log, cacheCompartilhada)
    print('\nMemórias Caches Privadas de Instruções --------------------------------------------------------------------------------------------------------------------------\n')
    log.write('\Memórias Caches Privadas de Instruções -------------------------------------------------------------------------------------------------------------------\n')
    for indice in range(len(cachesPrivadasInstrucoes)):
        console_cache_privada_instrucoes(log, cachesPrivadasInstrucoes[indice], indice)
    print('\nMemórias Caches Privadas de Dados -------------------------------------------------------------------------------------------------------------------------------\n')
    log.write('\nMemórias Caches Privadas de Dados -----------------------------------------------------------------------------------------------------------------------\n')
    for indice in range(len(cachesPrivadasDados)):
        console_cache_privada_dados(log, cachesPrivadasDados[indice], indice)
    return None

def console_cache_compartilhada(log: io.TextIOWrapper, cacheCompartilhada: CacheCompartilhada) -> None:
    '''
    Cria o texto de console exibindo o estado da Memória Cache Compartilhada.
    '''
    tags = cacheCompartilhada.linhas_cache.keys()
    texto = 'Memória Cache Compartilhada:\n'
    for tag in tags:
        texto += 'Tag: ' + tag + ' - Linhas: '
        for linha in cacheCompartilhada.linhas_cache[tag]:
            texto += linha + ', '
        texto += '\n'
    texto += 'Lista de Prioridade de Substituição: '
    for posicao in range(len(cacheCompartilhada.lista_subs)):
        texto += 'Pos. ' + str(posicao) + ': ' + cacheCompartilhada.lista_subs[posicao] + ' - '
    print(texto + '\n\n')
    log.write(texto + '\n\n')
    return None

def console_cache_privada_instrucoes(log: io.TextIOWrapper, cachePrivadaInstrucoes: CachePrivadaInstrucoes, indice: int) -> None:
    '''
    Cria o texto de console exibindo o estado da Memória Cache Privada de Instruções.
    '''
    tags = cachePrivadaInstrucoes.linhas_cache.keys()
    texto = 'Memória Cache Privada de Instruções ' + str(indice) + '\n'
    for tag in tags:
        texto += 'Tag: ' + tag + ' - Linhas: '
        for linha in cachePrivadaInstrucoes.linhas_cache[tag]:
            texto += linha + ', '
        texto += '\n'
    texto += 'Lista de Prioridade de Substituição: '
    for posicao in range(len(cachePrivadaInstrucoes.lista_subs)):
        texto += 'Pos. ' + str(posicao) + ': ' + cachePrivadaInstrucoes.lista_subs[posicao] + ' - '
    print(texto + '\n\n')
    log.write(texto + '\n\n')
    return None

def console_cache_privada_dados(log: io.TextIOWrapper, cachePrivadaDados: CachePrivadaDados, indice: int) -> None:
    '''
    Cria o texto de console exibindo o estado da Memória Cache Privada de Dados.
    '''
    tags = cachePrivadaDados.linhas_cache.keys()
    texto = 'Memória Cache Privada de Dados Id. ' + str(indice) + '\n'
    for tag in tags:
        texto += 'Tag: ' + tag + ' - Estado: ' + cachePrivadaDados.linhas_cache[tag].estado + ' - Linhas: '
        for linha in cachePrivadaDados.linhas_cache[tag].palavras:
            texto += linha + ', '
        texto += '\n'
    texto += 'Lista de Prioridade de Substituição: '
    for posicao in range(len(cachePrivadaDados.lista_subs)):
        texto += 'Pos. ' + str(posicao) + ': ' + cachePrivadaDados.lista_subs[posicao] + ' - '
    print(texto + '\n\n')
    log.write(texto + '\n\n')
    return None

# Início do Programa ----------------------------------------------------

if __name__ == "__main__":
    main()