# -*- coding: utf-8 -*-
"""Monta a página Visão Geral v2 inteira e tira um print. Cada visual vira um iframe,
igual a um visual HTML do Power BI.

    python preview_v2.py            # dados reais da planilha (precisa da unidade G:)
    python preview_v2.py hoje       # os números do print de 03/11 a 18/11, sem ler a planilha
    python preview_v2.py t1 ... t7  # casos fictícios, para ver os extremos do destaque
    python preview_v2.py t3 saida.png

Os dois controles nativos (datas e Período) aparecem como caixas aproximadas: no
Power BI são segmentações, por cima do cabeçalho.
"""
import html, io, pathlib, sys
import prep_v2, fundo_v2
from estilo_v2 import *

AQUI = pathlib.Path(__file__).parent
nome = sys.argv[1] if len(sys.argv) > 1 else ''
saida = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else AQUI / 'preview_v2.png'
if nome:
    c, S, a = prep_v2.caso(nome)
else:
    import dados_op
    c = dados_op.calcular()
    S = prep_v2.series(c, dados_op.ler(), __import__('pandas').Timestamp.today().normalize())
    a = dados_op.atualizacao(c)
P = prep_v2.paineis(c, S, a)
fundo_v2.montar()


def visual(conteudo, x, y, w, h, z):
    # O visual HTML do Power BI injeta o conteúdo num <div> sem altura definida.
    miolo = "<div class='pbi-host'>" + conteudo + "</div>"
    return ("<iframe scrolling='no' style='position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border:0;"
            "z-index:%d' srcdoc=\"%s\"></iframe>" % (x, y, w, h, z, html.escape(miolo, quote=True)))


def controle(txt, x, y, w, h):
    return ("<div style='position:absolute;z-index:2000;left:%dpx;top:%dpx;width:%dpx;height:%dpx;box-sizing:border-box;"
            "display:flex;align-items:center;padding:0 12px;background:%s;border:1px solid %s;border-radius:3px;"
            "font:600 17px Segoe UI;color:%s'>%s</div>" % (x, y, w, h, BOTAO, BOTAO_B, TEXTO, txt))


partes = ["<img src='%s' style='position:absolute;left:0;top:0;width:%dpx;height:%dpx'>"
          % (fundo_v2.SAIDA.as_uri(), LARG_PAG, ALT_PAG)]
partes += [visual(P[k], *POS[k]) for k in POS]
partes += [controle('de &#8211; até', X_DTS, Y_DTS, W_DTS, H_DTS), controle('Período &#9662;', X_PER, Y_PER, W_PER, H_PER)]
pagina = ("<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;padding:0;width:%dpx;height:%dpx;"
          "background:%s}</style></head><body>%s</body></html>" % (LARG_PAG, ALT_PAG, PAG, ''.join(partes)))
arq = saida.with_suffix('.html')
io.open(arq, 'w', encoding='utf-8').write(pagina)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': LARG_PAG, 'height': ALT_PAG}, device_scale_factor=1)
    pg.goto(arq.as_uri())
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(saida))
    b.close()
print(saida.name, 'gerado')
