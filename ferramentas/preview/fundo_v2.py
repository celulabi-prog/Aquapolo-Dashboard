# -*- coding: utf-8 -*-
"""Monta o PNG de fundo da página Visão Geral v2.

É imagem só o que não depende de dado: a faixa do cabeçalho (a mesma arte da
Visão Geral, reduzida a 104 px de altura e esmaecida à direita), o divisor e a
palavra "Período" ao lado dos controles nativos, e os três trechos de tubo que
ligam uma coluna do trem à outra (ficam no vão entre os visuais).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont
from fundo_op import rgb, FAIXA
from estilo_v2 import *

REPO = pathlib.Path(__file__).resolve().parents[2]
NOME = 'fundo_visao_geral_v2.png'
SAIDA = REPO / NOME
RECURSO = REPO / 'Dashboard - Aquapolo.Report' / 'StaticResources' / 'RegisteredResources' / NOME
LARG_ARTE, CORTE_ARTE, ESMAECE = 1280, 1066, 0.82      # a arte reduzida, onde é cortada e de onde some


def montar():
    pag = Image.new('RGB', (LARG_PAG, ALT_PAG), rgb(PAG))
    d = ImageDraw.Draw(pag)
    d.rectangle([0, 0, LARG_PAG, H_CAB - 1], fill=rgb(CAB))
    arte = Image.open(FAIXA).convert('RGB').resize((LARG_ARTE, H_CAB), Image.LANCZOS).crop((0, 0, CORTE_ARTE, H_CAB - 1))
    mascara = Image.new('L', arte.size, 255)
    ini = int(CORTE_ARTE * ESMAECE)
    for x in range(ini, CORTE_ARTE):
        ImageDraw.Draw(mascara).line([x, 0, x, H_CAB], fill=int(255 * (CORTE_ARTE - x) / float(CORTE_ARTE - ini)))
    pag.paste(arte, (0, 0), mascara)
    d.line([0, H_CAB - 1, LARG_PAG, H_CAB - 1], fill=rgb(LINHA))
    d.line([X_DIV, 20, X_DIV, 83], fill=rgb(LINHA))
    d.text((X_DTS, Y_PER + 9), 'Período', fill=rgb(SEC), font=ImageFont.truetype('segoeui.ttf', 17))
    for i in range(3):          # o tubo entre uma coluna e a seguinte
        x = X_COL[i] + COLS[i]
        d.rectangle([x, Y_TUBO, x + VAO - 1, Y_TUBO + 5], fill=rgb(AZUL))
    pag.save(SAIDA)
    RECURSO.parent.mkdir(parents=True, exist_ok=True)
    pag.save(RECURSO)
    return SAIDA


if __name__ == '__main__':
    print('ESCRITO:', montar())
    print('ESCRITO:', RECURSO)
