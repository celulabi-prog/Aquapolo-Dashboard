# -*- coding: utf-8 -*-
"""Escreve a página 1 (Visão Geral — Painel Operacional) no formato PBIR.

Dez visuais sobre o fundo com o cabeçalho: os cinco painéis e o rodapé (HTML),
as duas caixas do cabeçalho — período exibido e status da atualização (HTML) —
e duas segmentações nativas: o seletor Período e o controle de datas.
As posições saem de estilo_op.py, as mesmas que o preview usa.

Só grava os visuais desta lista; não apaga nada. Se um visual sair da lista,
apague a pasta dele à mão em definition/pages/<página>/visuals.
"""
import json, pathlib
import indicadores_op as IX
from estilo_op import *

REPO = pathlib.Path(__file__).resolve().parents[2]
PAGES = REPO / 'Dashboard - Aquapolo.Report' / 'definition' / 'pages'
PAGE_ID = 'a822121ef6e9b05473aa'
HTMLV = 'htmlContent443BE3AD55E043BF878BED274D3A6855'
IMAGEM = 'fundo_painel_operacional3936334463390476.png'
S_VIS = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json'
S_PAGE = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
PERIODO_PADRAO = 'Mensal'      # a opção que já vem marcada (tabela 'Período Painel')


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


def seletor(nome, tabela, coluna, marcado, x, y, w, h, z, tab):
    """Lista suspensa de escolha única. O fundo opaco, na cor da caixa pintada no
    cabeçalho, é o que esconde o "Mensal v" da imagem."""
    col = lambda fonte: {'Column': {'Expression': {'SourceRef': fonte}, 'Property': coluna}}
    zero = L('0D')
    return {
        '$schema': S_VIS, 'name': nome,
        'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': tab},
        'visual': {
            'visualType': 'slicer',
            'query': {'queryState': {'Values': {'projections': [
                {'field': col({'Entity': tabela}), 'queryRef': tabela + '.' + coluna,
                 'nativeQueryRef': coluna, 'active': True}]}}},
            'objects': {
                'data': [{'properties': {'mode': L("'Dropdown'")}}],
                'selection': [{'properties': {'singleSelect': L('true'),
                                              'strictSingleSelect': L('true'),
                                              'selectAllCheckboxEnabled': L('false')}}],
                'header': [{'properties': {'show': L('false')}}],
                'items': [{'properties': {
                    'fontColor': cor(BRANCO), 'background': cor(BOTAO), 'textSize': L('16D'),
                    'fontFamily': L("'''Segoe UI Semibold'', wf_segoe-ui_semibold, helvetica, arial, sans-serif'")}}],
                # A moldura clara em volta da lista é do próprio controle (segue a cor da
                # fonte); outlineColor e outlineWeight não mexem nela.
                'general': [{'properties': {'filter': {'filter': {
                    'Version': 2,
                    'From': [{'Name': 'p', 'Entity': tabela, 'Type': 0}],
                    'Where': [{'Condition': {'In': {
                        'Expressions': [col({'Source': 'p'})],
                        'Values': [[{'Literal': {'Value': "'" + marcado + "'"}}]]}}}]}}}}],
            },
            'visualContainerObjects': {
                'title': [{'properties': {'show': L('false')}}],
                'background': [{'properties': {'show': L('true'), 'color': cor(BOTAO),
                                               'transparency': zero}}],
                'border': [{'properties': {'show': L('false')}}],
                'dropShadow': [{'properties': {'show': L('false')}}],
                'padding': [{'properties': {'top': zero, 'bottom': zero, 'left': zero, 'right': zero}}],
                'visualHeader': [{'properties': {'show': L('false')}}],
            },
            'drillFilterOtherVisuals': True,
        },
    }


def intervalo(nome, tabela, coluna, x, y, w, h, z, tab):
    """Duas caixas de data, de e até, sem a régua deslizante. Fica sem nada
    marcado: nesse estado as caixas mostram o primeiro e o último dia com dado."""
    campo = {'Column': {'Expression': {'SourceRef': {'Entity': tabela}}, 'Property': coluna}}
    zero = L('0D')
    return {
        '$schema': S_VIS, 'name': nome,
        'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': tab},
        'visual': {
            'visualType': 'slicer',
            'query': {'queryState': {'Values': {'projections': [
                {'field': campo, 'queryRef': tabela + '.' + coluna, 'nativeQueryRef': coluna, 'active': True}]}}},
            'objects': {
                'data': [{'properties': {'mode': L("'Between'")}}],
                'header': [{'properties': {'show': L('false')}}],
                'slider': [{'properties': {'show': L('false')}}],
                'date': [{'properties': {'fontColor': cor(BRANCO), 'background': cor(BOTAO),
                                         'textSize': L('11D')}}],
            },
            'visualContainerObjects': {
                'title': [{'properties': {'show': L('false')}}],
                'background': [{'properties': {'show': L('true'), 'color': cor(BOTAO), 'transparency': zero}}],
                'border': [{'properties': {'show': L('true'), 'color': cor(BOTAO_B), 'radius': L('8D')}}],
                'dropShadow': [{'properties': {'show': L('false')}}],
                'visualHeader': [{'properties': {'show': L('false')}}],
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

VISUAIS = {nome: painel(nome, medida, x, y, w, h, tab, tab)
           for tab, (nome, medida, x, y, w, h) in enumerate(PAINEIS)}
# As duas caixas do cabeçalho ficam por cima dos painéis: o detalhe de cada uma
# abre para baixo, sobre o topo deles.
for nome, medida, x, y, w, h, z in (('status', 'HTML Status', X_STA, Y_STA, W_STA, H_STA, 1000),
                                    ('periodo', 'HTML Período', X_DAT, Y_DAT, W_DAT, H_DAT, 1100)):
    v = painel(nome, medida, x, y, w, h, z, z)
    obj = v['visual']['visualContainerObjects']
    # Sem a folga interna padrão do visual: a caixa precisa cair alinhada com a do seletor pintado.
    obj['padding'] = [{'properties': {lado: L('0D') for lado in ('top', 'bottom', 'left', 'right')}}]
    # Sem os ícones que o Power BI mostra no canto do visual ao passar o mouse.
    obj['visualHeader'] = [{'properties': {'show': L('false')}}]
    VISUAIS[nome] = v
VISUAIS['seletor_periodo'] = seletor('seletor_periodo', 'Período Painel', 'Período', PERIODO_PADRAO,
                                     X_PER, Y_PER, W_PER, H_PER, 2000, 2000)
VISUAIS['datas'] = intervalo('datas', 'Datas Painel', 'Data', X_DTS, Y_DTS, W_DTS, H_DTS, 2100, 2100)

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

if __name__ == '__main__':
    destino = PAGES / PAGE_ID
    for nome, v in VISUAIS.items():
        d = destino / 'visuals' / nome
        d.mkdir(parents=True, exist_ok=True)
        (d / 'visual.json').write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding='utf-8')
    (destino / 'page.json').write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding='utf-8')
    print('OK:', len(VISUAIS), 'visuais escritos em', PAGE_ID)
    for nome, v in VISUAIS.items():
        p = v['position']
        print('   %-16s x=%4d y=%4d  %4dx%-4d z=%d' % (nome, p['x'], p['y'], p['width'], p['height'], p['z']))
