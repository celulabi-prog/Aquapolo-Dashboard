# -*- coding: utf-8 -*-
"""Converte os dados reais em texto pronto para o molde (lado do preview)."""
from estilo import *
import molde
from dados import num, pct

SETA_CIMA, SETA_BAIXO, TRACO = '&#9650;', '&#9660;', '&#8212;'


def seta(v):
    return SETA_CIMA if (v is not None and v >= 0) else SETA_BAIXO


def cor_var(v):
    return CINZA if v is None else (VERDE if v >= 0 else VERMELHO)


def cor_meta(at):
    return VERDE if at >= 1 else (AMARELO if at >= 0.85 else VERMELHO)


def paineis(c):
    cab = molde.cabecalho({'ult': c['ult_atualizacao']})
    cli = molde.card_cliente({})
    vol = molde.card_volume({
        'rot': c['rot'], 'rot_ant': c['rot_ant'], 'vol': num(c['vol']), 'ls': num(c['ls']),
        'ant': num(c['ant']), 'var_mes': pct(c['var_mes']),
        'cor_var': cor_var(c['var_mes']), 'seta_var': seta(c['var_mes'])})
    verde = c['situacao'] == 'verde'
    txt = ('Consumo estável' if verde else
           ('Consumo acima do esperado' if c['desvio_med'] >= 0 else 'Consumo abaixo do esperado'))
    sit = molde.card_situacao({
        'cor': COR[c['situacao']], 'icone': '&#10003;' if verde else '&#33;', 'texto': txt,
        'faixa_min': num(c['faixa'][0]), 'faixa_max': num(c['faixa'][1])})

    linhas = ''
    for L in c['linhas']:
        cor = cor_meta(L['at'])
        todos = L['nome'] == 'Todos Clientes'
        linhas += molde.linha_resumo({
            'nome': L['nome'], 'vol': num(L['vol']), 'cor': cor,
            'cor_nome': BRANCO if todos else CLARO, 'peso': '700' if todos else '400',
            'larg': '%.0f' % (max(0.0, min(L['at'] / 1.3, 1.0)) * 100),
            'pct': '%.0f%%' % (L['at'] * 100)})
    res = molde.resumo({'rot': c['rot']}, linhas)

    piso = min(h['vol'] for h in c['hist']) * 0.94
    faixa = max(max(h['vol'] for h in c['hist']) - piso, 0.0001)
    lh = ''
    for h in c['hist']:
        lh += molde.linha_historico({
            'rot': h['rot'], 'vol': num(h['vol']), 'ls': num(h['ls']), 'dias': str(h['dias']),
            'larg': '%.0f' % (55 + (h['vol'] - piso) / faixa * 45),
            'fundo': '#16304f' if h['foco'] else 'transparent',
            'cor_rot': BRANCO if h['foco'] else SEC,
            'cor_dias': AMARELO if h['dias'] < 25 else SEC,
            'cor_var': cor_var(h['var']),
            'var': (seta(h['var']) + ' ' + pct(h['var'])) if h['var'] is not None else TRACO})
    hist = molde.historico({
        'cliente': c['cliente'].upper(), 'media13': num(c['media13']),
        'media13_ls': num(c['media13'] / 86.4), 'min13': num(c['min13']), 'min13_mes': c['min13_mes'],
        'max13': num(c['max13']), 'max13_mes': c['max13_mes']}, lh)

    ld = ''.join(molde.linha_diagnostico(x) for x in [
        {'rotulo': 'Meta contratual', 'valor': num(c['meta']), 'lado': num(c['meta'] / 86.4) + ' L/s'},
        {'rotulo': 'Média 12 meses anteriores', 'valor': num(c['med']), 'lado': num(c['med'] / 86.4) + ' L/s'},
        {'rotulo': 'Desvio vs. média 12 meses', 'valor': seta(c['desvio_med']) + ' ' + pct(c['desvio_med']),
         'cor': cor_var(c['desvio_med']), 'unidade': False},
        {'rotulo': 'Desvio vs. mesmo mês do ano anterior', 'sub': c['rot_ano'],
         'valor': seta(c['var_ano']) + ' ' + pct(c['var_ano']), 'cor': cor_var(c['var_ano']), 'unidade': False},
        {'rotulo': 'Pico histórico', 'sub': c['pico_mes'], 'valor': num(c['pico']),
         'lado': num(c['pico'] / 86.4) + ' L/s'},
        {'rotulo': 'Menor consumo histórico', 'sub': c['vale_mes'], 'valor': num(c['vale']),
         'lado': num(c['vale'] / 86.4) + ' L/s'}])
    dentro = abs(c['vol'] - c['med']) <= c['dp']
    diag = molde.diagnostico({
        'cliente': c['cliente'].upper(), 'cor_desvio': cor_var(c['desvio_med']),
        'desvio_txt': pct(abs(c['desvio_med'])).lstrip('+') + (' acima' if c['desvio_med'] >= 0 else ' abaixo'),
        'cor_faixa': VERDE if dentro else AMARELO, 'faixa_txt': 'dentro' if dentro else 'fora'}, ld)

    bs = c['barras']
    n = len(bs)
    maxp = max([b['var'] for b in bs] + [0])
    maxn = max([-b['var'] for b in bs] + [0])
    tot = max(maxp + maxn, 0.01)
    y0 = molde.TOPO_R + molde.ALTO_PLOT * (maxp / tot)
    gw = (molde.LARG_SVG - 16) / n
    bw = min(gw * 0.46, 80)
    bars = ''
    for i, b in enumerate(bs):
        cx = 8 + (i + 0.5) * gw
        h = max(abs(b['var']) / tot * molde.ALTO_PLOT, 1)
        sobe = b['var'] >= 0
        bars += molde.barra_variacao({
            'x': '%.0f' % (cx - bw / 2), 'y': '%.0f' % (y0 - h if sobe else y0),
            'w': '%.0f' % bw, 'h': '%.0f' % h, 'cx': '%.0f' % cx,
            'yr': '%.0f' % (y0 - h - 9 if sobe else y0 + h + 17),
            'cor': VERDE if sobe else VERMELHO, 'pct': pct(b['var']), 'nome': b['nome']})
    var = molde.variacao({'contexto': c['rot'] + ' vs. ' + c['rot_ano'] + ' &#183; todos os clientes, ordenado',
                          'y0': '%.0f' % y0}, bars)
    return {'cabecalho': cab, 'cliente': cli, 'volume': vol, 'situacao': sit,
            'resumo': res, 'historico': hist, 'diagnostico': diag, 'variacao': var}
