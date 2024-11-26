import pygame
import pygame.gfxdraw
import sys
import numpy as np
import time
import math
import random
import pygame.mixer

# Heurística utilizada é uma avaliação baseada em pontuação de "janelas" de quatro células.

# Inicialização do Pygame e do mixer de som
pygame.init()
pygame.mixer.init()
som_bolinha = pygame.mixer.Sound("sounds/8-bit-game.mp3")  # Substitua pelo caminho do seu arquivo de som
som_bolinha.play(loops=-1)

# Configurações do jogo
LARGURA = 800
ALTURA = 650
TAMANHO_CELULA = 80
RAIO_PECA = TAMANHO_CELULA // 2 - 5
LINHAS = 7
COLUNAS = 8
ESPACO_LATERAL = (LARGURA - (COLUNAS * TAMANHO_CELULA)) // 2

# Cores
FUNDO_TABULEIRO = (33, 48, 64)
FUNDO_SUPERIOR = (16, 27, 39)
VERMELHO = (231, 76, 60)
VERDE = (26, 188, 156)
BRANCO = (255, 255, 255)
AMARELO_DOURADO = (255, 215, 0)

# Inicialização do Pygame
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Connect 4")
fonte = pygame.font.SysFont("monospace", 50)
fonte_pontuacao = pygame.font.SysFont("monospace", 30)

# Pontuações iniciais
pontuacao_human = 0
pontuacao_skynet = 0
VITORIA_PONTUACAO = float('inf')

# Configuraçãoes Padrão
algoritmo_selecionado = "Minimax"
PLY = 3


def criar_tabuleiro():
    """Cria e retorna uma matriz 2D inicializada com zeros para representar o tabuleiro do jogo."""
    return np.zeros((LINHAS, COLUNAS))

def soltar_peca(tabuleiro, linha, coluna, peca):
    """Coloca a peça especificada na posição (linha, coluna) do tabuleiro."""
    tabuleiro[linha][coluna] = peca

def verificar_espaco(tabuleiro, coluna):
    """Verifica se a coluna escolhida ainda possui espaço para inserir uma peça."""
    return tabuleiro[0][coluna] == 0

def obter_linha_disponivel(tabuleiro, coluna):
    """Retorna a linha mais baixa disponível em uma coluna específica."""
    for linha in range(LINHAS - 1, -1, -1):
        if tabuleiro[linha][coluna] == 0:
            return linha

def menu_principal():
    """Tela principal do menu com as opções Play, Opções, About, Comparar e Quit."""
    global PLY, algoritmo_selecionado

    # Carregando a fonte personalizada
    caminho_fonte = "fonts/joystix monospace.otf"
    fonte_custom = pygame.font.Font(caminho_fonte, 50) 
    fonte_custom_pequena = pygame.font.Font(caminho_fonte, 30)

    # Opções do menu principal
    opcoes = ["PLAY", "OPÇÕES", "ABOUT", "COMPARAR", "QUIT"]
    indice_selecionado = 0

    while True:
        tela.fill(FUNDO_SUPERIOR)
        titulo = fonte_custom.render("MENU PRINCIPAL", True, (255, 215, 0))
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))

        # Exibindo as opções
        for i, opcao in enumerate(opcoes):
            cor = VERDE if i == indice_selecionado else BRANCO
            label = fonte_custom_pequena.render(opcao, True, cor)
            label_rect = label.get_rect(center=(LARGURA // 2, 150 + i * 50))

            # Verifica se o mouse está sobre a opção
            if label_rect.collidepoint(pygame.mouse.get_pos()):
                cor = VERDE
                indice_selecionado = i  # Atualiza o índice da seleção com base no mouse

            # Atualiza a cor com base na seleção
            label = fonte_custom_pequena.render(opcao, True, cor)
            tela.blit(label, label_rect)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    indice_selecionado = (indice_selecionado - 1) % len(opcoes)
                elif evento.key == pygame.K_DOWN:
                    indice_selecionado = (indice_selecionado + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN:
                    if opcoes[indice_selecionado] == "PLAY":
                        jogo()
                    elif opcoes[indice_selecionado] == "OPÇÕES":
                        menu_inicial()
                    elif opcoes[indice_selecionado] == "ABOUT":
                        menu_about()  # Chama o menu About
                    elif opcoes[indice_selecionado] == "COMPARAR":
                        return "comparar"
                    elif opcoes[indice_selecionado] == "QUIT":
                        pygame.quit()
                        sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique esquerdo do mouse
                    pos_y = evento.pos[1]
                    for i, opcao in enumerate(opcoes):
                        label_rect = fonte_custom_pequena.render(opcao, True, BRANCO).get_rect(
                            center=(LARGURA // 2, 150 + i * 50)
                        )
                        if label_rect.collidepoint(evento.pos):  # Verifica colisão total (x e y)
                            if opcao == "PLAY":
                                jogo()
                            elif opcao == "OPÇÕES":
                                menu_inicial()
                            elif opcao == "ABOUT":
                                menu_about()  # Chama o menu About
                            elif opcao == "COMPARAR":
                                return "comparar"  # Corrige a funcionalidade do clique
                            elif opcao == "QUIT":
                                pygame.quit()
                                sys.exit()

def menu_about():
    """Tela About com informações sobre o jogo."""
    caminho_fonte = "fonts/joystix monospace.otf"
    fonte_custom = pygame.font.Font(caminho_fonte, 30)

    while True:
        tela.fill(FUNDO_SUPERIOR)
        titulo = fonte_custom.render("ABOUT", True, (255, 215, 0))
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))

        # Informações sobre o jogo
        linhas = [
            "Connect 4 Game",
            "Developed by Micael Resende",
            "Version: 1.0",
            "Thank you for playing!",
        ]
        for i, linha in enumerate(linhas):
            texto = fonte_custom.render(linha, True, BRANCO)
            tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 150 + i * 40))

        # Adicionando o botão "Voltar"
        voltar_label = fonte_custom.render("Voltar", True, BRANCO)
        voltar_rect = voltar_label.get_rect(center=(LARGURA // 2, ALTURA - 100))
        pygame.draw.rect(tela, FUNDO_TABULEIRO, voltar_rect.inflate(20, 10))  # Fundo do botão
        tela.blit(voltar_label, voltar_rect)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return  # Volta ao menu principal

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if voltar_rect.collidepoint(evento.pos):
                    return  # Volta ao menu principal
              
def menu_inicial():
    """Tela inicial para configurar o algoritmo e a dificuldade."""
    global PLY, algoritmo_selecionado

    dropdowns_abertos = {"algoritmo": False, "dificuldade": False}

    # Opções para os dropdowns
    opcoes_algoritmo = ["Minimax", "Alfa-Beta"]
    opcoes_dificuldade = ["Fácil (1 Ply)", "Médio (2 Ply)", "Difícil (3 Ply)", "Muito Difícil (4 Ply)"]
    dificuldade_valores = [1, 2, 3, 4]  # Valores correspondentes

    while True:
        tela.fill(FUNDO_SUPERIOR)
        titulo = fonte.render("CONFIGURAÇÕES", True, BRANCO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))

        # Renderiza o menu de algoritmo
        algoritmo_label = fonte_pontuacao.render(f"Algoritmo: {algoritmo_selecionado}", True, BRANCO)
        algoritmo_rect = algoritmo_label.get_rect(topleft=(100, 150))
        tela.blit(algoritmo_label, algoritmo_rect)

        # Renderiza o menu de dificuldade
        dificuldade_label = fonte_pontuacao.render(f"Dificuldade: {opcoes_dificuldade[PLY - 1]}", True, BRANCO)
        dificuldade_rect = dificuldade_label.get_rect(topleft=(100, 272))  # Mais espaçamento entre menus
        tela.blit(dificuldade_label, dificuldade_rect)

        # Desenha opções se dropdown estiver aberto
        if dropdowns_abertos["algoritmo"]:
            for i, opcao in enumerate(opcoes_algoritmo):
                label = fonte_pontuacao.render(opcao, True, VERDE if opcao == algoritmo_selecionado else BRANCO)
                rect = label.get_rect(topleft=(100, 185 + i * 40))
                tela.blit(label, rect)

        if dropdowns_abertos["dificuldade"]:
            for i, opcao in enumerate(opcoes_dificuldade):
                label = fonte_pontuacao.render(opcao, True, VERDE if PLY == dificuldade_valores[i] else BRANCO)
                rect = label.get_rect(topleft=(100, 310 + i * 40))  # Ajustado para refletir o novo espaçamento
                tela.blit(label, rect)

        # Adiciona botão "Voltar"
        voltar_label = fonte_pontuacao.render("Voltar", True, BRANCO)
        voltar_rect = voltar_label.get_rect(topleft=(20, ALTURA - 100))  # Alinhado à esquerda
        pygame.draw.rect(tela, FUNDO_TABULEIRO, voltar_rect.inflate(20, 10))  # Fundo do botão
        tela.blit(voltar_label, voltar_rect)

        # Adiciona botão "Play"
        play_label = fonte_pontuacao.render("Play", True, BRANCO)
        play_rect = play_label.get_rect(topright=(LARGURA - 20, ALTURA - 100))  # Alinhado à direita
        pygame.draw.rect(tela, FUNDO_TABULEIRO, play_rect.inflate(20, 10))  # Fundo do botão
        tela.blit(play_label, play_rect)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos

                # Verifica clique em "Algoritmo"
                if algoritmo_rect.collidepoint(pos):
                    dropdowns_abertos["algoritmo"] = not dropdowns_abertos["algoritmo"]
                    dropdowns_abertos["dificuldade"] = False

                # Verifica clique em "Dificuldade"
                elif dificuldade_rect.collidepoint(pos):
                    dropdowns_abertos["dificuldade"] = not dropdowns_abertos["dificuldade"]
                    dropdowns_abertos["algoritmo"] = False

                # Verifica clique nas opções do dropdown de algoritmo
                elif dropdowns_abertos["algoritmo"]:
                    for i, opcao in enumerate(opcoes_algoritmo):
                        rect = pygame.Rect(100, 185 + i * 40, 300, 30)
                        if rect.collidepoint(pos):
                            algoritmo_selecionado = opcao
                            dropdowns_abertos["algoritmo"] = False

                # Verifica clique nas opções do dropdown de dificuldade
                elif dropdowns_abertos["dificuldade"]:
                    for i, opcao in enumerate(opcoes_dificuldade):
                        rect = pygame.Rect(100, 310 + i * 40, 300, 30) 
                        if rect.collidepoint(pos):
                            PLY = dificuldade_valores[i]
                            dropdowns_abertos["dificuldade"] = False

                # Verifica clique no botão "Voltar"
                elif voltar_rect.collidepoint(pos):
                    return  # Sai do menu e volta ao Menu Principal

                # Verifica clique no botão "Play"
                elif play_rect.collidepoint(pos):
                    return "play"  # Inicia o jogo


def verificar_vitoria(tabuleiro, peca):
    """Verifica se há quatro peças consecutivas (em linha, coluna ou diagonal) para o jogador."""
    for linha in range(LINHAS):
        for col in range(COLUNAS - 3):
            if all(tabuleiro[linha][col + i] == peca for i in range(4)):
                return True

    for col in range(COLUNAS):
        for linha in range(LINHAS - 3):
            if all(tabuleiro[linha + i][col] == peca for i in range(4)):
                return True

    for linha in range(LINHAS - 3):
        for col in range(COLUNAS - 3):
            if all(tabuleiro[linha + i][col + i] == peca for i in range(4)):
                return True

    for linha in range(3, LINHAS):
        for col in range(COLUNAS - 3):
            if all(tabuleiro[linha - i][col + i] == peca for i in range(4)):
                return True

    return False

def avaliar_tabuleiro(tabuleiro, peca):
    """
    Calcula uma pontuação do tabuleiro, favorecendo alinhamentos do jogador e bloqueando os do oponente.
    """
    score = 0
    oponente = 1 if peca == 2 else 2

    # Priorizar a coluna central
    coluna_central = [int(i) for i in list(tabuleiro[:, COLUNAS // 2])]
    central_count = coluna_central.count(peca)
    score += central_count * 3

    # Avaliação das janelas
    for linha in range(LINHAS):
        for col in range(COLUNAS - 3):
            # é usada para percorrer as colunas do tabuleiro de jogo, porém com uma limitação para 
            # evitar ultrapassar os limites do tabuleiro ao verificar uma sequência de quatro peças consecutivas.
            janela = tabuleiro[linha, col:col + 4]
            score += avaliar_janela(janela, peca, oponente)

    for linha in range(LINHAS - 3):
        for col in range(COLUNAS):
            janela = [tabuleiro[linha + i][col] for i in range(4)]
            score += avaliar_janela(janela, peca, oponente)

    for linha in range(LINHAS - 3):
        for col in range(COLUNAS - 3):
            janela = [tabuleiro[linha + i][col + i] for i in range(4)]
            score += avaliar_janela(janela, peca, oponente)

    for linha in range(LINHAS - 3):
        for col in range(COLUNAS - 3):
            janela = [tabuleiro[linha + 3 - i][col + i] for i in range(4)]
            score += avaliar_janela(janela, peca, oponente)

    return score


def avaliar_janela(janela, peca, oponente):
    """
    Analisa uma sequência de 4 células, atribuindo pontos por vantagens do jogador ou penalizando alinhamentos do oponente.
    """
    score = 0
    janela = list(janela)
    
    if janela.count(peca) == 4:
        score += 100  # Vitória garantida
    elif janela.count(peca) == 3 and janela.count(0) == 1:
        score += 10  # Grande vantagem
    elif janela.count(peca) == 2 and janela.count(0) == 2:
        score += 5  # Configuração favorável

    if janela.count(oponente) == 3 and janela.count(0) == 1:
        score -= 50  # Bloquear vitória do oponente
    
    return score


def movimentos_validos(tabuleiro):
    """Retorna uma lista de colunas onde é possível inserir uma peça."""
    return [col for col in range(COLUNAS) if verificar_espaco(tabuleiro, col)]


def calcular_profundidade(tabuleiro):
    peças = np.count_nonzero(tabuleiro)
    if peças < 10:  # Fase inicial
        return 2
    elif peças < 30:  # Fase intermediária
        return 4
    else:  # Fase final
        return 5


def simular_jogada(tabuleiro, coluna, peca):
    """
    Cria uma cópia do tabuleiro e simula uma jogada em uma coluna específica.
    """
    temp_tabuleiro = tabuleiro.copy()
    linha = obter_linha_disponivel(temp_tabuleiro, coluna)
    if linha is not None:  # Verifica se a jogada é válida
        soltar_peca(temp_tabuleiro, linha, coluna, peca)
    return temp_tabuleiro


def minimax(tabuleiro, profundidade, alpha, beta, maximizando):
    """
    Explora a árvore de jogadas possíveis usando Minimax com poda Alfa-Beta, 
    retornando a melhor jogada e sua pontuação.
        * Maximiza a pontuação para a IA e minimiza para o jogador humano.
    """
    movimentos = movimentos_validos(tabuleiro)

    movimentos_ordenados = sorted(
        movimentos,
        key=lambda col: avaliar_tabuleiro(simular_jogada(tabuleiro, col, 2 if maximizando else 1), 2 if maximizando else 1),
        reverse=True
    ) 
    # lambda é uma forma de criar uma função anônima (ou seja, sem nome) em uma única linha. Sendo usada em funções como sorted(), min(), max()
    # key indica o critério de ordenação ou seleção..
    
    terminal = verificar_vitoria(tabuleiro, 1) or verificar_vitoria(tabuleiro, 2) or len(movimentos) == 0
    if profundidade == 0 or terminal:
        if terminal:
            if verificar_vitoria(tabuleiro, 2):
                return (None, VITORIA_PONTUACAO)
            elif verificar_vitoria(tabuleiro, 1):
                return (None, -VITORIA_PONTUACAO)
            else:
                return (None, 0)
        else:
            return (None, avaliar_tabuleiro(tabuleiro, 2 if maximizando else 1))

    if maximizando:
        valor = -math.inf
        melhor_coluna = movimentos_ordenados[0]
        for coluna in movimentos_ordenados:
            linha = obter_linha_disponivel(tabuleiro, coluna)
            temp_tabuleiro = tabuleiro.copy()
            soltar_peca(temp_tabuleiro, linha, coluna, 2)
            nova_pontuacao = minimax(temp_tabuleiro, profundidade - 1, alpha, beta, False)[1] # chamada recursiva que corresponde a um nó da árvore.
            if nova_pontuacao > valor:
                valor = nova_pontuacao
                melhor_coluna = coluna
            alpha = max(alpha, valor)
            if alpha >= beta:
                break
        return melhor_coluna, valor
    else:
        valor = math.inf
        melhor_coluna = movimentos_ordenados[0]
        for coluna in movimentos_ordenados:
            linha = obter_linha_disponivel(tabuleiro, coluna)
            temp_tabuleiro = tabuleiro.copy()
            soltar_peca(temp_tabuleiro, linha, coluna, 1)
            nova_pontuacao = minimax(temp_tabuleiro, profundidade - 1, alpha, beta, True)[1]
            if nova_pontuacao < valor:
                valor = nova_pontuacao
                melhor_coluna = coluna
            beta = min(beta, valor)
            if alpha >= beta:
                break
            # A recursão termina quando a profundidade máxima(PLY) é atingida ou o jogo chega a um estado terminal.
        return melhor_coluna, valor


def desenhar_tabuleiro(tabuleiro, pontuacao_human, pontuacao_skynet, coluna_destacada=None):
    """Renderiza o estado atual do tabuleiro na tela, incluindo peças e destaques."""
    tela.fill(FUNDO_SUPERIOR)

    # Exibe o saldo de vitórias com a imagem do usuário
    caminho_imagem_human = "images/boy.png" 
    caminho_imagem_ia = "images/robot.png"

    # Desenha a imagem do jogador humano com o nome e pontuação
    exibir_nome_e_imagem(f"Você: {pontuacao_human}", caminho_imagem_human, (140, 10))

    # Desenha a imagem da IA com o nome e pontuação
    exibir_nome_e_imagem(f"IA: {pontuacao_skynet}", caminho_imagem_ia, (LARGURA - 200, 10))

    # Destaque da coluna
    if coluna_destacada is not None:
        # Criar uma superfície semitransparente
        destaque = pygame.Surface((TAMANHO_CELULA, ALTURA - TAMANHO_CELULA), pygame.SRCALPHA)
        destaque.fill((200, 200, 200, 100))
        tela.blit(
            destaque,
            (coluna_destacada * TAMANHO_CELULA + ESPACO_LATERAL, TAMANHO_CELULA)
        )

    # Desenha o tabuleiro e as células
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            pygame.draw.rect(
                tela,
                FUNDO_TABULEIRO,
                (coluna * TAMANHO_CELULA + ESPACO_LATERAL, linha * TAMANHO_CELULA + TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA),
            )
            pygame.gfxdraw.aacircle(
                tela,
                coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                RAIO_PECA,
                FUNDO_SUPERIOR,
            )
            pygame.gfxdraw.filled_circle(
                tela,
                coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                RAIO_PECA,
                FUNDO_SUPERIOR,
            )

    # Desenha as peças no tabuleiro
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            if tabuleiro[linha][coluna] == 1:
                pygame.gfxdraw.aacircle(
                    tela,
                    coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                    linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                    RAIO_PECA,
                    VERMELHO,
                )
                pygame.gfxdraw.filled_circle(
                    tela,
                    coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                    linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                    RAIO_PECA,
                    VERMELHO,
                )
            elif tabuleiro[linha][coluna] == 2:
                pygame.gfxdraw.aacircle(
                    tela,
                    coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                    linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                    RAIO_PECA,
                    VERDE,
                )
                pygame.gfxdraw.filled_circle(
                    tela,
                    coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
                    linha * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
                    RAIO_PECA,
                    VERDE,
                )

    pygame.display.update()


def exibir_nome_e_imagem(nome, caminho_imagem, posicao_nome):
    """
    Exibe o nome do jogador junto com sua imagem circular.
    """
    try:
        # Carrega a imagem do jogador
        imagem = pygame.image.load(caminho_imagem)
        imagem = pygame.transform.smoothscale(imagem, (50, 50))  # Redimensiona para caber no círculo

        # Cria a superfície circular
        circulo = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(circulo, 25, 25, 25, (0, 0, 0, 0))
        pygame.gfxdraw.filled_circle(circulo, 25, 25, 25, (255, 255, 255))  # Preenchimento branco

        # Aplica a imagem no círculo
        circulo.blit(imagem, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Posiciona o círculo à esquerda do texto
        posicao_circulo = (posicao_nome[0] - 60, posicao_nome[1])
        tela.blit(circulo, posicao_circulo)

    except pygame.error as e:
        print(f"Erro ao carregar a imagem: {e}")

    # Renderiza o nome
    fonte = pygame.font.SysFont("monospace", 30)
    texto = fonte.render(nome, True, BRANCO)
    tela.blit(texto, posicao_nome)

def animar_peca_caindo(tabuleiro, coluna, peca):
    """Anima a peça caindo até a posição correta na coluna escolhida."""
    
    # Calcula a linha final onde a peça deve parar
    linha_final = obter_linha_disponivel(tabuleiro, coluna)
    
    for linha_atual in range(linha_final + 1):
        desenhar_tabuleiro(tabuleiro, pontuacao_human, pontuacao_skynet)
        pygame.gfxdraw.aacircle(
            tela,
            coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
            linha_atual * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
            RAIO_PECA,
            VERDE if peca == 2 else VERMELHO,
        )
        pygame.gfxdraw.filled_circle(
            tela,
            coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2 + ESPACO_LATERAL,
            linha_atual * TAMANHO_CELULA + TAMANHO_CELULA + TAMANHO_CELULA // 2,
            RAIO_PECA,
            VERDE if peca == 2 else VERMELHO,
        )
        pygame.display.update()
        pygame.time.wait(60)  # Controla a velocidade da animação, 50ms por iteração

    # Solta a peça no tabuleiro
    soltar_peca(tabuleiro, linha_final, coluna, peca)


def tela_fim_de_jogo(mensagem):
    """Exibe a tela de fim de jogo com a mensagem do vencedor e opções de reinício ou saída."""
    
    """Exibe a tela de fim de jogo com a mensagem do vencedor e opções."""
    global pontuacao_human, pontuacao_skynet

    while True:
        tela.fill(FUNDO_SUPERIOR)

        # Exibe a mensagem do vencedor
        titulo = fonte.render(mensagem, True, BRANCO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 150))

        # Botão "Jogar Novamente"
        jogar_novamente_label = fonte_pontuacao.render("Jogar Novamente", True, BRANCO)
        jogar_novamente_rect = jogar_novamente_label.get_rect(center=(LARGURA // 2, ALTURA // 2))
        pygame.draw.rect(tela, FUNDO_TABULEIRO, jogar_novamente_rect.inflate(20, 10))
        tela.blit(jogar_novamente_label, jogar_novamente_rect)

        # Botão "Voltar"
        voltar_label = fonte_pontuacao.render("Voltar", True, BRANCO)
        voltar_rect = voltar_label.get_rect(center=(LARGURA // 2, ALTURA // 2 + 100))
        pygame.draw.rect(tela, FUNDO_TABULEIRO, voltar_rect.inflate(20, 10))
        tela.blit(voltar_label, voltar_rect)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                if jogar_novamente_rect.collidepoint(pos):
                    return "replay"  # Retorna para reiniciar o jogo
                elif voltar_rect.collidepoint(pos):
                    return "menu"  # Retorna ao menu inicial

def jogo():
    """
    Controla a lógica principal do jogo; 
    Alterna turnos entre o jogador humano e a IA;
    Executa animações e atualiza o tabuleiro;
    Verifica vitórias e chama a tela de fim de jogo, se necessário.
    """
    
    global pontuacao_human, pontuacao_skynet, PLY
    tabuleiro = criar_tabuleiro()
    game_over = False
    turno = random.choice([0, 1])  # Escolha aleatória de quem começa
    
    if turno == 0:
        print("O jogador humano comeca!")
    else:
        print("A IA comeca!")
    
    coluna_destacada = None  # Armazena a coluna sob o mouse

    desenhar_tabuleiro(tabuleiro, pontuacao_human, pontuacao_skynet)
    pygame.display.update()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()

            # Detectar a coluna sob o mouse para destacá-la
            if evento.type == pygame.MOUSEMOTION:
                pos_x = evento.pos[0]
                if ESPACO_LATERAL <= pos_x <= LARGURA - ESPACO_LATERAL:
                    coluna_destacada = (pos_x - ESPACO_LATERAL) // TAMANHO_CELULA
                else:
                    coluna_destacada = None
                desenhar_tabuleiro(tabuleiro, pontuacao_human, pontuacao_skynet, coluna_destacada)

            # Jogada do humano
            if evento.type == pygame.MOUSEBUTTONDOWN and turno == 0:
                if coluna_destacada is not None and verificar_espaco(tabuleiro, coluna_destacada):
                    animar_peca_caindo(tabuleiro, coluna_destacada, 1)

                    # Verifica se o humano venceu
                    sequencia_vencedora = verificar_vitoria_com_sequencia(tabuleiro, 1)
                    if sequencia_vencedora:
                        pontuacao_human += 1
                        destacar_sequencia_vencedora(tabuleiro, sequencia_vencedora)
                        pygame.time.wait(3000)  # Pausa de 3 segundos
                        print("Humano venceu!")
                        mensagem = "Você venceu!"
                        acao = tela_fim_de_jogo(mensagem)  # Vai para a tela de fim de jogo
                        if acao == "replay":
                            return "replay"  # Reinicia o jogo mantendo a lógica
                        elif acao == "menu":
                            return "menu"  # Volta ao menu inicial
                    turno = 1  # Passa o turno para a IA

        # Turno da IA
        if turno == 1 and not game_over:
            # Captura o tempo de início do algoritmo
            start_time = time.time()

            if PLY == 1:  # Modo fácil - movimento aleatório
                movimentos = movimentos_validos(tabuleiro)
                coluna = random.choice(movimentos)
            else:  # Modo intermediário/difícil - usando Minimax
                coluna, minimax_score = minimax(tabuleiro, PLY, -math.inf, math.inf, True)

            # Calcula o tempo total de execução
            end_time = time.time()
            exec_time = end_time - start_time

            if 0 <= coluna < COLUNAS and verificar_espaco(tabuleiro, coluna):
                animar_peca_caindo(tabuleiro, coluna, 2)

                # Verifica se a IA venceu
                sequencia_vencedora = verificar_vitoria_com_sequencia(tabuleiro, 2)
                if sequencia_vencedora:
                    pontuacao_skynet += 1
                    destacar_sequencia_vencedora(tabuleiro, sequencia_vencedora)
                    pygame.time.wait(3000)  # Pausa de 3 segundos
                    print(f"IA venceu! Tempo de execucao do algoritmo: {exec_time:.4f} segundos")
                    mensagem = "A IA venceu!"
                    acao = tela_fim_de_jogo(mensagem)  # Vai para a tela de fim de jogo
                    if acao == "replay":
                        return "replay"  # Reinicia o jogo mantendo a lógica
                    elif acao == "menu":
                        return "menu"  # Volta ao menu inicial
                else:
                    print(f"IA executou sem vitoria. Tempo de execucao do algoritmo: {exec_time:.4f} segundos")
            turno = 0  # Passa o turno para o humano

        # Atualiza o tabuleiro com a coluna destacada
        desenhar_tabuleiro(tabuleiro, pontuacao_human, pontuacao_skynet, coluna_destacada)


def verificar_vitoria_com_sequencia(tabuleiro, peca):
    # Verifica linhas
    for linha in range(LINHAS):
        for col in range(COLUNAS - 3): # COLUNAS - 3 porque estamos verificando uma sequência de quatro peças, e precisamos evitar sair dos limites da matriz.
            if all(tabuleiro[linha][col + i] == peca for i in range(4)):
                return [(linha, col + i) for i in range(4)]

    # Verifica colunas
    for col in range(COLUNAS):
        for linha in range(LINHAS - 3):
            if all(tabuleiro[linha + i][col] == peca for i in range(4)): # Verifica se todas as quatro células consecutivas na linha atual contêm a mesma peça do jogador.
                return [(linha + i, col) for i in range(4)]

    # Verifica diagonais crescentes
    for linha in range(LINHAS - 3):
        for col in range(COLUNAS - 3):
            if all(tabuleiro[linha + i][col + i] == peca for i in range(4)):
                return [(linha + i, col + i) for i in range(4)]

    # Verifica diagonais decrescentes
    for linha in range(3, LINHAS):
        for col in range(COLUNAS - 3):
            if all(tabuleiro[linha - i][col + i] == peca for i in range(4)):
                return [(linha - i, col + i) for i in range(4)]

    return None


def destacar_sequencia_vencedora(tabuleiro, sequencia):
    for linha, coluna in sequencia:
        pygame.draw.rect(
            tela,
            (255, 215, 0),  # Amarelo dourado
            (coluna * TAMANHO_CELULA + ESPACO_LATERAL,
             linha * TAMANHO_CELULA + TAMANHO_CELULA,
             TAMANHO_CELULA, TAMANHO_CELULA),
            width=5  # Define apenas a borda com 5px de largura
        )
    pygame.display.update()
    
def comparar_algoritmos(tabuleiro, profundidades, jogador=2):
    """
    Compara os tempos de execução entre Minimax e Poda Alfa-Beta para diferentes profundidades.
    :param tabuleiro: O estado atual do tabuleiro.
    :param profundidades: Lista de profundidades para testar.
    :param jogador: Jogador atual (2 por padrão, a IA).
    """
    print("Comparando tempos de execucao dos algoritmos:")
    print("Profundidade | Minimax (s) | Alfa-Beta (s)")
    print("-----------------------------------------")
    for profundidade in profundidades:
        # Testando Minimax
        start_minimax = time.time()
        minimax(tabuleiro, profundidade, -math.inf, math.inf, True)
        end_minimax = time.time()
        tempo_minimax = end_minimax - start_minimax

        # Testando Alfa-Beta
        start_alfa_beta = time.time()
        minimax(tabuleiro, profundidade, -math.inf, math.inf, True)  # Minimax com poda Alfa-Beta
        end_alfa_beta = time.time()
        tempo_alfa_beta = end_alfa_beta - start_alfa_beta

        print(f"{profundidade:^11} | {tempo_minimax:^12.4f} | {tempo_alfa_beta:^13.4f}")


if __name__ == "__main__":
    while True:
        acao = menu_principal()  # Menu principal com as opções Play, Opções, Comparar e Quit

        if acao == "play":
            menu_inicial()  # Vai para o menu de configurações
            while True:
                turno = random.choice([0, 1]) 
                resultado = jogo()  # Começa o jogo
                if resultado == "replay":
                    continue  # Reinicia o jogo sem voltar ao menu
                elif resultado == "menu":
                    break  # Volta ao menu principal

        elif acao == "opcoes":
            menu_inicial()  # Vai para o menu de configurações diretamente

        elif acao == "comparar":
            # Executa a comparação de algoritmos
            tabuleiro = criar_tabuleiro()  # Cria um tabuleiro vazio
            profundidades = [1, 2, 3, 4]  # Defina as profundidades para teste
            comparar_algoritmos(tabuleiro, profundidades)  # Chama a função de comparação

        elif acao == "quit":
            sys.exit()  # Sai do programa



# A heurística de avaliação do tabuleiro calcula uma pontuação para representar a "vantagem" 
# do jogador em relação ao oponente, considerando as possíveis combinações de 4 peças em linha.

# A coluna central é considerada uma boa jogada porque possibilita mais combinações futuras.
# Baseada no número de peças presentes do jogador e do oponente.