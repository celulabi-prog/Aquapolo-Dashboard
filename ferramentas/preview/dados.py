# -*- coding: utf-8 -*-
"""Reproduz em Python exatamente as contas das medidas DAX, para alimentar o preview."""
import json, pandas as pd

BASE = r'C:\Aquapolo\Base_PowerBI'
MES_PT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
ORDEM = ['Todos Clientes', 'Q3 ABC', 'PE7 ABC', 'UNIB3 ABC', 'PP4 BRK', 'Oxicap', 'Cabot',
         'Oxiteno P.', 'Paranapanema', 'Bridgestone', 'Hydro Extrusion', 'Vitopel']


def rot(i):
    return '%s/%02d' % (MES_PT[(i - 1) % 12], ((i - 1) // 12) % 100)


def num(v, casas=0):
    if v is None or pd.isna(v):
        return '—'
    s = ('%,.*f' % (casas, v)).replace(',', '§').replace('.', ',').replace('§', '.') if casas else '{:,.0f}'.format(v).replace(',', '.')
    return s


def pct(v, casas=1):
    if v is None or pd.isna(v):
        return '—'
    return ('%+.*f' % (casas, v * 100)).replace('.', ',') + '%'


def calcular(cliente='Todos Clientes'):
    f = pd.read_parquet(BASE + r'\fato_indicadores.parquet')
    d = pd.read_parquet(BASE + r'\dim_indicadores.parquet')
    ult_geral = f['Data'].max()
    v = f[f['Etapa'] == 'Volumes'].copy()
    v['MesIdx'] = v['Data'].dt.year * 12 + v['Data'].dt.month
    metas = d[d['Etapa'] == 'Volumes'].set_index('Indicador')['Target_Min']
    m = v.groupby(['Indicador', 'MesIdx']).agg(vol=('Valor', 'mean'), dias=('Valor', 'size'))

    # mês de referência = último mês COMPLETO (>= 25 dias), como na medida 'Vol Mês Idx'
    por_mes = v.groupby('MesIdx')['Data'].nunique()
    foco = int(max(i for i, n in por_mes.items() if n >= 25))

    s = m.loc[cliente]
    vol, ant = s.loc[foco, 'vol'], s.loc[foco - 1, 'vol']
    ano = s.loc[foco - 12, 'vol']
    janela = s.loc[foco - 12:foco - 1, 'vol']          # 12 meses ANTERIORES
    med, dp = janela.mean(), janela.std(ddof=0)
    cheios = s[s['dias'] >= 25]['vol']
    ult = v[v['Indicador'] == cliente]['Data'].max()
    d7 = v[(v['Indicador'] == cliente) & (v['Data'] > ult - pd.Timedelta(days=7))]['Valor'].mean()
    d30 = v[(v['Indicador'] == cliente) & (v['Data'] > ult - pd.Timedelta(days=30))]['Valor'].mean()
    dist = abs(vol - med)

    hist = []
    for i in range(foco - 12, foco + 1):
        hv, hd = s.loc[i, 'vol'], int(s.loc[i, 'dias'])
        hant = s.loc[i - 1, 'vol'] if (i - 1) in s.index else None
        hist.append({'rot': rot(i), 'vol': hv, 'ls': hv / 86.4, 'dias': hd,
                     'var': (hv / hant - 1) if hant else None, 'foco': i == foco})
    hist.reverse()

    linhas = []
    for c in ORDEM:
        sc = m.loc[c]
        cv = sc.loc[foco, 'vol']
        jan = sc.loc[foco - 12:foco - 1, 'vol']
        cmed, cdp = jan.mean(), jan.std(ddof=0)
        at = cv / metas[c]
        cdist = abs(cv - cmed)
        linhas.append({'nome': c, 'vol': cv, 'meta': metas[c], 'at': at,
                       'sit': 'verde' if cdist <= cdp else ('amarelo' if cdist <= 2 * cdp else 'vermelho')})

    barras = []
    for c in ORDEM[1:]:
        sc = m.loc[c]
        a, b = sc.loc[foco, 'vol'], sc.loc[foco - 12, 'vol']
        barras.append({'nome': c, 'var': a / b - 1})
    barras.sort(key=lambda x: -x['var'])

    return {
        'cliente': cliente, 'rot': rot(foco), 'rot_ant': rot(foco - 1), 'rot_ano': rot(foco - 12),
        'ult_atualizacao': ult_geral.strftime('%d/%m/%Y'),
        'vol': vol, 'ls': vol / 86.4, 'ant': ant, 'var_mes': vol / ant - 1,
        'ano': ano, 'var_ano': vol / ano - 1, 'meta': metas[cliente], 'at': vol / metas[cliente],
        'med': med, 'dp': dp, 'faixa': (med - dp, med + dp),
        'desvio_med': vol / med - 1, 'd7': d7, 'd30': d30, 'dias': int(s.loc[foco, 'dias']),
        'situacao': 'verde' if dist <= dp else ('amarelo' if dist <= 2 * dp else 'vermelho'),
        'pico': cheios.max(), 'pico_mes': rot(int(cheios.idxmax())),
        'vale': cheios.min(), 'vale_mes': rot(int(cheios.idxmin())),
        'hist': hist, 'linhas': linhas, 'barras': barras,
        'media13': sum(h['vol'] for h in hist if h['dias'] >= 25) / sum(1 for h in hist if h['dias'] >= 25),
        'min13': min(h['vol'] for h in hist if h['dias'] >= 25),
        'min13_mes': min((h for h in hist if h['dias'] >= 25), key=lambda h: h['vol'])['rot'],
        'max13': max(h['vol'] for h in hist if h['dias'] >= 25),
        'max13_mes': max((h for h in hist if h['dias'] >= 25), key=lambda h: h['vol'])['rot'],
    }


if __name__ == '__main__':
    c = calcular()
    print('mes de referencia:', c['rot'], '| cliente:', c['cliente'])
    print('volume %s m3/d  %s L/s  | vs %s: %s' % (num(c['vol']), num(c['ls']), c['rot_ant'], pct(c['var_mes'])))
    print('meta %s  atingimento %s' % (num(c['meta']), pct(c['at'] - 1)))
    print('media 12m anteriores %s | faixa %s - %s | desvio %s' % (num(c['med']), num(c['faixa'][0]), num(c['faixa'][1]), pct(c['desvio_med'])))
    print('pico %s (%s) | menor %s (%s)' % (num(c['pico']), c['pico_mes'], num(c['vale']), c['vale_mes']))
    print('linhas:', len(c['linhas']), '| hist:', len(c['hist']), '| barras:', len(c['barras']))
    print('ultima atualizacao:', c['ult_atualizacao'])
