# -*- coding: utf-8 -*-
"""Monta a página Painel Operacional inteira e tira um print, para comparar
com a referência. Cada painel vira um iframe, igual a um visual do Power BI."""
import html, io, pathlib
import dados_op, prep_op, fundo_op
from estilo_op import *

AQUI = pathlib.Path(__file__).parent
c = dados_op.calcular()
P = prep_op.paineis(c)
fundo_op.montar()          # o cabeçalho do preview é o mesmo PNG que vai pro Power BI


def visual(conteudo, x, y, w, h):
    # O visual HTML do Power BI injeta o conteúdo dentro de um <div> SEM altura
    # definida. Reproduzir isso aqui é o que faz o preview mostrar o mesmo
    # colapso de altura que acontece no Power BI.
    miolo = "<div class='pbi-host'>" + conteudo + "</div>"
    return ("<iframe scrolling='no' style='position:absolute;left:%dpx;top:%dpx;width:%dpx;"
            "height:%dpx;border:0' srcdoc=\"%s\"></iframe>"
            % (x, y, w, h, html.escape(miolo, quote=True)))


partes = [
    "<img src='%s' style='position:absolute;left:0;top:0;width:%dpx;height:%dpx'>"
    % (fundo_op.SAIDA.as_uri(), LARG_PAG, ALT_PAG),
    visual(P['eebc'],    X_SUP[0], Y_SUP, COL_SUP[0], H_SUP),
    visual(P['tmbr'],    X_SUP[1], Y_SUP, COL_SUP[1], H_SUP),
    visual(P['or'],      X_SUP[2], Y_SUP, COL_SUP[2], H_SUP),
    visual(P['consumo'], X_INF[0], Y_INF, COL_INF[0], H_INF),
    visual(P['volumes'], X_INF[1], Y_INF, COL_INF[1], H_INF),
    visual(P['rodape'],  MARG,     Y_ROD, LARG,       H_ROD),
]

pagina = ("<!doctype html><html><head><meta charset='utf-8'><style>"
          "html,body{margin:0;padding:0;width:%dpx;height:%dpx;background:%s}"
          "</style></head><body>%s</body></html>"
          % (LARG_PAG, ALT_PAG, PAG, ''.join(partes)))
io.open(AQUI / 'preview_op.html', 'w', encoding='utf-8').write(pagina)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': LARG_PAG, 'height': ALT_PAG}, device_scale_factor=1)
    pg.goto((AQUI / 'preview_op.html').resolve().as_uri())
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(AQUI / 'preview_op.png'))
    b.close()
print('preview_op.png gerado')
