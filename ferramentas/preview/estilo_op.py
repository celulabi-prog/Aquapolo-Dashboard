# -*- coding: utf-8 -*-
"""Paleta e geometria da página Painel Operacional.

Os números vêm de medição direta do print de referência (1600x900), convertidos
para a página do Power BI (1920x1080) pelo fator 1,2. Fonte única do preview,
do gerador de DAX e do escritor dos visuais.
"""

# ---- cores (amostradas do print) -------------------------------------------
PAG      = '#000f21'      # fundo da página
PANEL    = '#001b2e'      # miolo dos painéis da faixa de cima
PANEL2   = '#001f3a'      # miolo dos painéis da faixa de baixo
CARTAO   = '#0b2740'      # cartão dentro dos painéis de baixo
BORDA    = '#143d5c'      # borda dos painéis
BORDA_C  = '#1b4a71'      # borda dos cartões
SEP      = '#102e4b'      # linha entre indicadores
TRILHO   = '#123855'      # trilho da barra
CHIP     = '#0f3c66'      # quadrado do ícone
CHIP_B   = '#1c5285'      # borda do quadrado do ícone

BRANCO   = '#ffffff'
CLARO    = '#dce9f7'
SEC      = '#93afc9'      # unidades, subtítulos
TER      = '#6b89a6'      # rótulos fracos
VERDE    = '#4ed15d'
AMARELO  = '#feb825'
VERMELHO = '#f4353f'
CINZA    = '#5c7791'
AZUL     = '#4a9eff'
TEAL     = '#2fd4c4'

COR = {'verde': VERDE, 'amarelo': AMARELO, 'vermelho': VERMELHO, 'cinza': CINZA}

# cabeçalhos de painel: (gradiente, cor do ícone)
CAB_AZUL = 'linear-gradient(90deg,#1a5a96 0%,#0d3a68 46%,#071f38 100%)'
CAB_TEAL = 'linear-gradient(90deg,#0a6a62 0%,#064b47 48%,#05282f 100%)'

# ---- grade da página (1920x1080) -------------------------------------------
LARG_PAG, ALT_PAG = 1920, 1080

MARG   = 16               # margem lateral
H_CAB  = 156              # faixa do cabeçalho (vem da imagem de fundo)

Y_SUP  = 168              # topo da faixa de painéis de cima
H_SUP  = 486              # altura dos painéis de cima
Y_INF  = 669              # topo da faixa de baixo
H_INF  = 304              # altura dos painéis de baixo
Y_ROD  = 989              # topo do rodapé
H_ROD  = 75               # altura do rodapé

GAP    = 15
COL_SUP = [647, 643, 568]                     # EEBC, TMBR, OR
COL_INF = [1238, 636]                         # Consumo, Volumes

X_SUP = [MARG,
         MARG + COL_SUP[0] + GAP,
         MARG + COL_SUP[0] + GAP + COL_SUP[1] + GAP]
X_INF = [MARG, MARG + COL_INF[0] + 14]
LARG  = LARG_PAG - 2 * MARG                   # 1888

H_FAIXA = 62              # faixa de título dentro do painel
RAIO    = 10              # raio da borda dos painéis

# ---- blocos de estilo reaproveitados ---------------------------------------
FONTE = "font-family:Segoe UI,sans-serif;"

def painel(fundo=PANEL, borda=BORDA):
    return ('height:100vh;width:100%;box-sizing:border-box;overflow:hidden;display:flex;'
            'flex-direction:column;background:' + fundo + ';border:1px solid ' + borda
            + ';border-radius:' + str(RAIO) + 'px')
