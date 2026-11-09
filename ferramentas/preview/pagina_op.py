# -*- coding: utf-8 -*-
"""Escreve a página 1 (Visão Geral — Painel Operacional) no formato PBIR.

Seis visuais HTML — cinco painéis e o rodapé — sobre o fundo com o cabeçalho.
As posições saem de estilo_op.py, as mesmas que o preview usa.
"""
import json, pathlib, shutil
import indicadores_op as IX
from estilo_op import *

REPO = pathlib.Path(r'C:\Users\Iza\Documents\dashboard aquapolo claude')
PAGES = REPO / 'Dashboard - Aquapolo.Report' / 'definition' / 'pages'
PAGE_ID = 'a822121ef6e9b05473aa'
HTMLV = 'htmlContent443BE3AD55E043BF878BED274D3A6855'
IMAGEM = 'fundo_painel_operacional3936334463390476.png'
S_VIS = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json'
S_PAGE = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'


def L(v):
    return {'expr': {'Literal': {'Value': v}}}


def cor(c):
    return {'solid': {'color': L("'" + c + "'")}}


def painel(nome, medida, x, y, w, h, z, tab):
    f = {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas HTML'}}, 'Property': medida}}
    return {
        '$schema': S_VIS, 'name': nome,
        'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': tab},
        'visual': {
            'visualType': HTMLV,
            'query': {
                'queryState': {'content': {'projections': [
                    {'field': f, 'queryRef': 'Medidas HTML.' + medida, 'nativeQueryRef': medida}]}},
                'sortDefinition': {'sort': [{'field': f, 'direction': 'Descending'}],
                                   'isDefaultSort': True},
            },
            'objects': {'compatibility': [{'properties': {'legacyRendering': L('false')}}]},
            'visualContainerObjects': {
                'title': [{'properties': {'show': L('false')}}],
                'background': [{'properties': {'show': L('false')}}],
                'border': [{'properties': {'show': L('false')}}],
            },
            'drillFilterOtherVisuals': True,
        },
    }


POS = {
    'eebc':    (X_SUP[0], Y_SUP, COL_SUP[0], H_SUP),
    'tmbr':    (X_SUP[1], Y_SUP, COL_SUP[1], H_SUP),
    'or':      (X_SUP[2], Y_SUP, COL_SUP[2], H_SUP),
    'consumo': (X_INF[0], Y_INF, COL_INF[0], H_INF),
    'volumes': (X_INF[1], Y_INF, COL_INF[1], H_INF),
}
PAINEIS = [('painel_' + p['k'], p['medida']) + POS[p['k']] for p in IX.PAINEIS]
PAINEIS.append(('rodape', 'HTML Rodapé', MARG, Y_ROD, LARG, H_ROD))

destino = PAGES / PAGE_ID
if (destino / 'visuals').exists():
    shutil.rmtree(destino / 'visuals')
(destino / 'visuals').mkdir(parents=True, exist_ok=True)

for tab, (nome, medida, x, y, w, h) in enumerate(PAINEIS):
    d = destino / 'visuals' / nome
    d.mkdir(parents=True)
    (d / 'visual.json').write_text(
        json.dumps(painel(nome, medida, x, y, w, h, tab, tab), indent=2, ensure_ascii=False),
        encoding='utf-8')

page = {
    '$schema': S_PAGE, 'name': PAGE_ID, 'displayName': 'Visão Geral',
    'displayOption': 'FitToPage', 'height': ALT_PAG, 'width': LARG_PAG,
    'objects': {
        'background': [{'properties': {
            'color': cor(PAG),
            'image': {'image': {
                'name': L("'fundo_painel_operacional.png'"),
                'url': {'expr': {'ResourcePackageItem': {
                    'PackageName': 'RegisteredResources', 'PackageType': 1, 'ItemName': IMAGEM}}},
                'scaling': L("'Fit'"),
            }},
            'transparency': L('0D'),
        }}],
        'outspace': [{'properties': {'color': cor('#02080f'), 'transparency': L('0D')}}],
    },
}
(destino / 'page.json').write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding='utf-8')
print('OK:', len(PAINEIS), 'visuais escritos em', PAGE_ID)
for nome, medida, x, y, w, h in PAINEIS:
    print('   %-16s %-22s x=%4d y=%4d  %4dx%-4d' % (nome, medida, x, y, w, h))
