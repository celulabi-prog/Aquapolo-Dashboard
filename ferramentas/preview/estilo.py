# -*- coding: utf-8 -*-
"""Paleta e geometria — fonte única para o preview e para o gerador de DAX."""

PAG     = '#0b1628'
PANEL   = '#0f1f38'
HEADBG  = '#152a48'
BORDA   = '#1e3150'
BRANCO  = '#ffffff'
CLARO   = '#c3d8ee'
SEC     = '#8fa9c4'
TER     = '#5f7d9c'
AZUL    = '#4a9eff'
VERDE   = '#22c55e'
AMARELO = '#eab308'
VERMELHO= '#ef4444'
CINZA   = '#64809c'
TRILHO  = '#152840'
BARRA   = '#3b82f6'

COR = {'verde': VERDE, 'amarelo': AMARELO, 'vermelho': VERMELHO, 'cinza': CINZA}

# ---- grade da página (1920x1080) -------------------------------------------
MARG   = 24          # margem lateral
TOPO   = 22          # margem superior
COL    = [531, 720, 569]          # larguras das três colunas
GAP    = 26                        # vão entre colunas
H_CAB  = 92          # faixa do cabeçalho
H_CARD = 104         # faixa dos cartões
H_PAN  = 500         # faixa dos painéis
H_VAR  = 256         # faixa do gráfico de variação
V1, V2, V3 = 24, 30, 30            # vãos verticais

X = [MARG, MARG + COL[0] + GAP, MARG + COL[0] + GAP + COL[1] + GAP]
Y_CAB  = TOPO
Y_CARD = Y_CAB + H_CAB + V1
Y_PAN  = Y_CARD + H_CARD + V2
Y_VAR  = Y_PAN + H_PAN + V3
LARG   = COL[0] + COL[1] + COL[2] + 2 * GAP

CARD = ('height:100vh;width:100%;box-sizing:border-box;overflow:hidden;display:flex;'
        'flex-direction:column;background:' + PANEL + ';border:1px solid ' + BORDA
        + ';border-radius:8px')


def cabecalho_painel(titulo, contexto):
    """Quadradinho azul + titulo em CAIXA ALTA espacada + contexto cinza a direita."""
    return ("<div style='padding:9px 15px;background:" + HEADBG + ";border-bottom:1px solid " + BORDA
            + ";display:flex;align-items:center;gap:8px;flex:none'>"
            + "<span style='color:" + AZUL + ";font-size:9px;line-height:1'>&#9632;</span>"
            + "<span style='font-size:12px;font-weight:700;color:" + BRANCO
            + ";letter-spacing:1.1px'>" + titulo + "</span>"
            + "<span style='margin-left:auto;font-size:10px;color:" + TER + "'>" + contexto + "</span>"
            + "</div>")
