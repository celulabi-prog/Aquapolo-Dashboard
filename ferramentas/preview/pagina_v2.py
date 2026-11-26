# -*- coding: utf-8 -*-
"""Escreve a página "Visão Geral v2" no formato PBIR.

Onze visuais sobre o fundo com o cabeçalho: as quatro colunas do trem (EEBC, TMBR,
OR, Clientes), a faixa de utilidades, a faixa de situação, o estado dos dados, a
caixa do período e a legenda (HTML), mais duas segmentações nativas, o seletor
Período e o controle de datas. Essas duas são cópias próprias desta página: não
estão sincronizadas com as da Visão Geral.

Só grava os visuais desta lista, na pasta desta página. Não apaga nada e não toca
na página Visão Geral atual. O registro da página em pages.json e o da imagem em
report.json são feitos à mão, uma vez só.
"""
import copy, json, pathlib
import pagina_op as PO
import gerar_v2 as GV
import fundo_v2
from estilo_v2 import *

PAGE_ID = 'visao_geral_v2'
NOME_PAGINA = 'Visão Geral v2'


def painel(chave):
    x, y, w, h, z = POS[chave]
    medida = GV.NOME[chave]
    v = PO.painel('v2_' + chave, medida, x, y, w, h, z, z)
    proj = v['visual']['query']['queryState']['content']['projections'][0]
    proj['field']['Measure']['Expression']['SourceRef']['Entity'] = GV.TABELA      # o mesmo objeto serve à ordenação
    proj['queryRef'] = GV.TABELA + '.' + medida
    return v


VISUAIS = {'v2_' + k: painel(k) for k in POS}
VISUAIS['v2_seletor_periodo'] = PO.seletor('v2_seletor_periodo', 'Período Painel', 'Período', PO.PERIODO_PADRAO,
                                           X_PER, Y_PER, W_PER, H_PER, 2000, 2000)
VISUAIS['v2_datas'] = PO.intervalo('v2_datas', 'Datas Painel', 'Data', X_DTS, Y_DTS, W_DTS, H_DTS, 2100, 2100)

page = copy.deepcopy(PO.page)
page['name'], page['displayName'] = PAGE_ID, NOME_PAGINA
fundo = page['objects']['background'][0]['properties']
fundo['color'] = PO.cor(PAG)
fundo['image']['image']['name'] = PO.L("'" + fundo_v2.NOME + "'")
fundo['image']['image']['url']['expr']['ResourcePackageItem']['ItemName'] = fundo_v2.NOME

if __name__ == '__main__':
    destino = PO.PAGES / PAGE_ID
    for nome, v in VISUAIS.items():
        d = destino / 'visuals' / nome
        d.mkdir(parents=True, exist_ok=True)
        (d / 'visual.json').write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding='utf-8')
    (destino / 'page.json').write_text(json.dumps(page, indent=2, ensure_ascii=False), encoding='utf-8')
    print('OK:', len(VISUAIS), 'visuais escritos em', PAGE_ID)
    for nome, v in VISUAIS.items():
        p = v['position']
        print('   %-20s x=%4d y=%4d  %4dx%-4d z=%d' % (nome, p['x'], p['y'], p['width'], p['height'], p['z']))
