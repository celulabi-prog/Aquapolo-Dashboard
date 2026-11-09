# -*- coding: utf-8 -*-
import json, pathlib, shutil
from estilo import *

REPO = pathlib.Path(r'C:\Users\Iza\Documents\dashboard aquapolo claude')
PAGES = REPO / 'Dashboard - Aquapolo.Report' / 'definition' / 'pages'
PAGE_ID = 'f41c7b2d9a6e05384cb1'
HTMLV = 'htmlContent443BE3AD55E043BF878BED274D3A6855'
S_VIS = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json'
S_PAGE = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
FUNDO, BORDA, TEXTO, CABEC = "'#0f2a47'", "'#1d4066'", "'#e8f1fb'", "'#13365a'"


def L(v):
    return {'expr': {'Literal': {'Value': v}}}


def cor(c):
    return {'solid': {'color': L(c)}}


def painel(nome, medida, x, y, w, h, z, tab):
    f = {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas Volumes'}}, 'Property': medida}}
    return {
        '$schema': S_VIS, 'name': nome,
        'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': tab},
        'visual': {
            'visualType': HTMLV,
            'query': {
                'queryState': {'content': {'projections': [
                    {'field': f, 'queryRef': 'Medidas Volumes.' + medida, 'nativeQueryRef': medida}]}},
                'sortDefinition': {'sort': [{'field': f, 'direction': 'Descending'}], 'isDefaultSort': True},
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


def filtro(nome, entidade, coluna, rotulo, x, y, w, h, z, tab):
    f = {'Column': {'Expression': {'SourceRef': {'Entity': entidade}}, 'Property': coluna}}
    return {
        '$schema': S_VIS, 'name': nome,
        'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': tab},
        'visual': {
            'visualType': 'slicer',
            'query': {'queryState': {'Values': {'projections': [
                {'field': f, 'queryRef': entidade + '.' + coluna, 'nativeQueryRef': coluna,
                 'displayName': rotulo, 'active': True}]}}},
            'objects': {
                'data': [{'properties': {'mode': L("'Dropdown'")}}],
                'selection': [{'properties': {
                    'singleSelect': L('true'), 'selectAllCheckboxEnabled': L('false')}}],
                'general': [{'properties': {
                    'orientation': L('1D'), 'responsive': L('false'),
                    'outlineColor': cor(BORDA), 'outlineWeight': L('1D')}}],
                'header': [{'properties': {
                    'show': L('true'), 'fontColor': cor("'#8fb0d0'"), 'background': cor(FUNDO),
                    'outline': L("'None'"), 'textSize': L('10D'), 'fontFamily': L("'Segoe UI'")}}],
                'items': [{'properties': {
                    'fontColor': cor(TEXTO), 'background': cor(CABEC),
                    'outline': L("'None'"), 'textSize': L('12D'), 'fontFamily': L("'Segoe UI'")}}],
            },
            'visualContainerObjects': {
                'title': [{'properties': {'show': L('false')}}],
                'background': [{'properties': {'show': L('true'), 'color': cor(CABEC), 'transparency': L('0D')}}],
                'border': [{'properties': {'show': L('true'), 'color': cor(BORDA), 'width': L('1D'), 'radius': L('6D')}}],
            },
            'drillFilterOtherVisuals': True,
        },
    }


PAINEIS = [
    ('html_cabecalho', 'HTML Vol Cabeçalho',         MARG,   Y_CAB,  LARG,   H_CAB,  0),
    ('card_cliente',   'HTML Vol Cartão Cliente',    X[0],   Y_CARD, COL[0], H_CARD, 1),
    ('card_volume',    'HTML Vol Cartão Volume',     X[1],   Y_CARD, COL[1], H_CARD, 2),
    ('card_situacao',  'HTML Vol Cartão Situação',   X[2],   Y_CARD, COL[2], H_CARD, 3),
    ('resumo',         'HTML Vol Resumo Clientes',   X[0],   Y_PAN,  COL[0], H_PAN,  4),
    ('historico',      'HTML Vol Histórico',         X[1],   Y_PAN,  COL[1], H_PAN,  5),
    ('diagnostico',    'HTML Vol Diagnóstico',       X[2],   Y_PAN,  COL[2], H_PAN,  6),
    ('variacao',       'HTML Vol Variação Ano',      MARG,   Y_VAR,  LARG,   H_VAR,  7),
]

FILTROS = [
    ('slicer_mesano', 'dCalendario', 'Mês/Ano', 'Mês de referência',
     MARG + LARG - 440, Y_CAB + 26, 186, 58, 30, True),
    ('slicer_cliente', 'Clientes', 'Cliente', 'Cliente',
     X[0] + 16, Y_CARD + 44, COL[0] - 32, 46, 31, False),
]

destino = PAGES / PAGE_ID
if (destino / 'visuals').exists():
    shutil.rmtree(destino / 'visuals')
(destino / 'visuals').mkdir(parents=True, exist_ok=True)

tab = 0
for nome, medida, x, y, w, h, z in PAINEIS:
    d = destino / 'visuals' / nome
    d.mkdir(parents=True)
    (d / 'visual.json').write_text(
        json.dumps(painel(nome, medida, x, y, w, h, z, tab), indent=2, ensure_ascii=False), encoding='utf-8')
    tab += 1
for nome, ent, col, rot, x, y, w, h, z, cab in FILTROS:
    d = destino / 'visuals' / nome
    d.mkdir(parents=True)
    v = filtro(nome, ent, col, rot, x, y, w, h, z, tab)
    v['visual']['objects']['header'][0]['properties']['show'] = L('true' if cab else 'false')
    if cab:
        v['visual']['visualContainerObjects']['border'][0]['properties']['color'] = cor("'#4a9eff'")
    (d / 'visual.json').write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding='utf-8')
    tab += 1

page = {
    '$schema': S_PAGE, 'name': PAGE_ID, 'displayName': 'Volumes',
    'displayOption': 'FitToPage', 'height': 1080, 'width': 1920,
    'objects': {
        'background': [{'properties': {'color': cor("'" + PAG + "'"), 'transparency': L('0D')}}],
        'outspace': [{'properties': {'color': cor("'#071022'"), 'transparency': L('0D')}}],
    },
}
(destino / 'page.json').write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding='utf-8')
print('OK:', len(PAINEIS), 'paineis +', len(FILTROS), 'filtros')
