# -*- coding: utf-8 -*-
"""Paleta e grade da página Visão Geral v2 (tela "Fluxo com destaque no lugar").

Os números vêm do protótipo aprovado (referencia_v2/D-Fluxo-Dinamico.dc.html).
Fonte única do preview, do gerador de DAX e do escritor dos visuais da v2.
A página Visão Geral atual não usa nada daqui.
"""
from estilo_op import LARG_PAG, ALT_PAG, BOTAO

# ---- cores -----------------------------------------------------------------
PAG     = '#000f21'      # fundo da página
PAINEL  = '#041729'      # miolo dos blocos e dos cartões
CAB     = '#00142a'      # faixa do cabeçalho
TEXTO   = '#f3f8fd'
SEC     = '#a8bfd6'      # unidades, rótulos
CLARO   = '#d3e1ef'
LINHA   = '#1f4263'      # contornos neutros
DIV     = '#11304c'      # linha entre indicadores
TRILHO  = '#143454'      # trilho do medidor
ZONA    = '#2b7d62'      # zona da meta no medidor e segmento "dentro" da fita
AZUL    = '#3aa7f2'      # tubulação, nós do trem, entrega
LIG     = '#2a77b0'      # ligação do nó ao bloco
TRAC    = '#5f88b0'      # ligações tracejadas, contagem zerada
BOTAO_B = '#2f6690'      # contorno dos controles do cabeçalho

FORA, ATENCAO, DENTRO = '#ff5c63', '#ffd257', '#57d68d'
COR   = {'f': FORA, 'a': ATENCAO, 'd': DENTRO}
RGB   = {'f': '255,92,99', 'a': '255,210,87'}
TINTA = {'f': '0.13', 'a': '0.08'}            # opacidade do fundo da linha em destaque
CORTE = {'f': '#261a2c', 'a': '#1c2424'}      # as duas barrinhas do medidor "além da escala"
NO_FORA, CAB_FORA, CAB_CALMO = '#1d1626', '#2a1524', '#0a2137'

FONTE = 'font-family:Segoe UI,sans-serif;font-variant-numeric:tabular-nums;color:' + TEXTO + ';'

# ---- regras do destaque ----------------------------------------------------
# Indicadores cuja frase do desvio sai na unidade (singular, plural), e não em %.
ABSOLUTOS = {'idade_lodo': ('dia', 'dias')}
BALDES = 90              # máximo de pontos de um minigráfico (períodos maiores viram médias)
CORTE_MINI = (6, 5)      # bloco com 6+ linhas e 5+ destaques: os minigráficos somem
ESCALA_MINI = 3          # o minigráfico corta em 3x o maior entre o valor do período e a meta

# ---- grade da página (1920x1080) -------------------------------------------
MARG   = 16
H_CAB  = 104             # faixa do cabeçalho (imagem de fundo)
Y_SIT, H_SIT = 112, 64   # faixa de situação
W_DADOS = 356            # bloco do atraso dos dados, à esquerda da faixa
H_DADOS = 224            # o visual dele é mais alto: o detalhe abre embaixo, sobre o trem
Y_COL  = 184             # topo das colunas (trem + bloco)
H_TREM, H_BLOCO = 88, 524
Y_UTIL = Y_COL + H_TREM + H_BLOCO      # 796: ligações (16) + utilidades (212)
H_LIG, H_UTIL = 16, 212
Y_LEG, H_LEG = 1032, 40
LARG   = LARG_PAG - 2 * MARG           # 1888

COLS = [460, 570, 430, 344]            # EEBC, TMBR, OR, Clientes
VAO  = 28
X_COL = [MARG + sum(COLS[:i]) + VAO * i for i in range(4)]     # 16, 504, 1102, 1560
GRADE = ' '.join('%dpx' % v for v in (COLS[0], VAO, COLS[1], VAO, COLS[2], VAO, COLS[3]))
Y_TUBO = Y_COL + 22 + 23               # 229: os trechos de tubo entre colunas (no PNG de fundo)

# ---- cabeçalho: caixa do período e controles nativos -----------------------
X_DTS, Y_DTS, W_DTS, H_DTS = 1630, 5, 274, 46        # controle de datas (de / até)
X_PER, Y_PER, W_PER, H_PER = 1714, 57, 190, 42       # lista suspensa Período
X_DIV = 1601                                         # divisor pintado no fundo
X_CXP, W_CXP, H_CXP = 1233, 340, 172                 # visual da caixa do período (detalhe abre embaixo)

# ---- os visuais HTML da página: (x, y, largura, altura, z) -------------------
# Cada coluna é um visual só, com a célula do trem em cima e o bloco embaixo. As
# caixas "dados" e "periodo" são mais altas que o que mostram: o detalhe delas abre
# embaixo, por cima de trechos que não respondem ao mouse.
POS = {
    'legenda':    (MARG, Y_LEG, LARG, H_LEG, 0),
    'utilidades': (MARG, Y_UTIL, LARG, H_LIG + H_UTIL, 1),
    'eebc':       (X_COL[0], Y_COL, COLS[0], H_TREM + H_BLOCO, 2),
    'tmbr':       (X_COL[1], Y_COL, COLS[1], H_TREM + H_BLOCO, 3),
    'or':         (X_COL[2], Y_COL, COLS[2], H_TREM + H_BLOCO, 4),
    'clientes':   (X_COL[3], Y_COL, COLS[3], H_TREM + H_BLOCO, 5),
    'situacao':   (MARG + W_DADOS + 12, Y_SIT, LARG - W_DADOS - 12, H_SIT, 6),
    'dados':      (MARG, Y_SIT, W_DADOS, H_DADOS, 1000),
    'periodo':    (X_CXP, 0, W_CXP, H_CXP, 1100),
}
