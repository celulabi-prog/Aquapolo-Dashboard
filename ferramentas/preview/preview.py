import pathlib
# -*- coding: utf-8 -*-
"""Monta a página inteira e tira um print, para comparar com a referência."""
import html, io, sys
import dados, molde, prep
from estilo import *

c = dados.calcular(sys.argv[1] if len(sys.argv) > 1 else 'Todos Clientes')
P = prep.paineis(c)

# cada painel é um visual separado no Power BI: um iframe reproduz isso fielmente
def visual(conteudo, x, y, w, h):
    return ("<iframe scrolling='no' style='position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;"
            "border:0' srcdoc=\"%s\"></iframe>" % (x, y, w, h, html.escape(conteudo, quote=True)))


def slicer(rotulo, valor, x, y, w, h, destaque=False):
    """Aproximação da segmentação nativa do Power BI, só para julgar o espaço."""
    borda = AZUL if destaque else BORDA
    cab = ("<div style='font-size:10px;color:%s;margin-bottom:4px'>%s</div>" % (SEC, rotulo)) if rotulo else ''
    alt = h - (20 if rotulo else 0)
    return ("<div style='position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;"
            "font-family:Segoe UI,sans-serif'>%s"
            "<div style='height:%dpx;background:#0d2440;border:1px solid %s;border-radius:5px;"
            "display:flex;align-items:center;padding:0 11px;color:#e8f1fb;font-size:13px'>%s"
            "<span style='margin-left:auto;color:%s;font-size:10px'>&#9662;</span></div></div>"
            % (x, y, w, h, cab, alt, borda, valor, SEC))


partes = [
    visual(P['cabecalho'], MARG, Y_CAB, LARG, H_CAB),
    visual(P['cliente'], X[0], Y_CARD, COL[0], H_CARD),
    visual(P['volume'], X[1], Y_CARD, COL[1], H_CARD),
    visual(P['situacao'], X[2], Y_CARD, COL[2], H_CARD),
    visual(P['resumo'], X[0], Y_PAN, COL[0], H_PAN),
    visual(P['historico'], X[1], Y_PAN, COL[1], H_PAN),
    visual(P['diagnostico'], X[2], Y_PAN, COL[2], H_PAN),
    visual(P['variacao'], MARG, Y_VAR, LARG, H_VAR),
    slicer('Mês de referência', 'Todos', MARG + LARG - 440, Y_CAB + 26, 186, 58, destaque=True),
    slicer('', c['cliente'] if c['cliente'] != 'Todos Clientes' else 'Todos',
           X[0] + 16, Y_CARD + 44, COL[0] - 32, 44),
]

pagina = ("<!doctype html><html><head><meta charset='utf-8'><style>"
          "html,body{margin:0;padding:0;width:1920px;height:1080px;background:" + PAG + "}"
          "</style></head><body>" + ''.join(partes) + "</body></html>")
io.open('preview.html', 'w', encoding='utf-8').write(pagina)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    pg.goto(pathlib.Path('preview.html').resolve().as_uri())
    pg.wait_for_timeout(500)
    pg.screenshot(path='preview.png')
    b.close()
print('preview.png gerado')
