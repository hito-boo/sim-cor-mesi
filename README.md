# Simulador de Coerência MESI
Trabalho para a disciplina de Arquitetura e Organização de Computadores II do curso de graduação em Ciência de Computação, na Universidade Estadual de Maringá.

# Objetivo e Implementação
O arquivo simulador_mesi.py presente no repositório é um **Simulador de Coerência MESI**, que funciona a partir de um sistema de memória composto por Memória Principal, Memória Cache Compartilhada e Memórias Caches Privadas reservadas para instruções e para dados. O mapeamento das linhas utilizado é o associativo e foi implementado por meio de dicionários, cujas chaves são _Tags_ (isto é, os _Bits_ mais significativos de um bloco de endereços) que referenciam uma lista de sequências compostas pelos _Bits_ menos significativos dos endereços de um bloco. Ou seja, apenas os endereços são ilustrados nas memórias, sem a representação das palavras, visto que a simulação não cobre a execução real de operações de leitura ou de escrita. Para as Memórias Caches Privadas de Dados, além do bloco, é presente um estado para ele no dicionário.

# Entradas e Modo de Uso
A execução da simulação exige dois arquivos de entrada.
O primeiro é um que contenha as configurações necessárias para a simulação, de forma que as seis primeiras linhas do arquivo devem conter apenas um número inteiro, os quais representam respectivamente:
1. Quantidade de endereços por linha (Tamanho do bloco)
    - Determina a quantidade de _Bits_ utilizados na _Tag_ e na linha.
2. Quantidade de linhas nas Memórias Caches Privadas
3. Quantidade de linhas na Memória Cache Compartilhada
4. Quantidade de blocos na Memória Principal
5. Quantidade de Processadores
6. Política de Substituição utilizada
    - 0: LRU - Least Recently Used (Menos recentemente utilizado)
    - 1: FIFO - First In First Out (Fila, isto é, primeiro a entrar será o primeiro a sair)

**É necessário que a quantidade de endereços por linha possa ser escrito da forma 2 elevado a N**. Isso se deve pela necessidade de haver uma quantidade exata de _Bits_ que represente de forma exata a quantidade de endereços presentes em uma linha. Além disso, a quantidadede linhas nas Memórias Caches Privadas **deve ser menor** que a quantidade de linhas na Memória Cache Compartilhada. Caso essas restrições não sejam seguidas, a simulação resultará em erros.

O segundo arquivo de entrada deve ser um arquivo que contenha os acessos realizado no processamento, no qual cada linha possui três elementos separados por espaço:
1. Índice do processador utilizado
    - Inicia-se a contagem em zero.
    - Levar em conta a quantidade de processadores considerada no arquivo de configuração.
2. Tipo da operação
    - 0: Leitura de instrução
    - 2: Leitura de dado
    - 3: Escrita de dado
3. Endereço do acesso

Dessa forma, a maneira de inicializar a simulação é: python simulador_mesi.py arquivo_configuração arquivo_acessos
Neste repositório, há exemplos de arquivos de configuração e de testes em suas respectivas pastas.

# Saída
Ao longo da simulação, todo o conteúdo exibido no console é escrito em um arquivo chamado _simulador.txt_. A saída se inicia mostrando as características utilizadas (lidas do arquivo de configuração), bem como a criação do sistema de memória. Então, para cada acesso ao longo da simulação, é mostrada a linha de acesso, o sinal envivado ao barramento de coerência e o estado do sistema de memória após a realização da operação.