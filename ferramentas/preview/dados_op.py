# -*- coding: utf-8 -*-
"""Refaz em Python as contas das medidas do Painel Operacional, para o preview.

Espelha o DAX:
  [Valor 30d]          = DIVIDE(SUM(Numerador), SUM(Denominador)) nos 30 dias
                         até a última data COM DADO daquele indicador
  [Valor 30d Anterior] = mesma conta nos 30 dias anteriores a esses
"""
import pandas as pd
import indicadores_op as IX

BASE = r'C:\Aquapolo\Base_PowerBI'


def num(v, casas=0):
    """Número no formato pt-BR."""
    if v is None or pd.isna(v):
        return '—'
    s = '{:,.{}f}'.format(v, casas).replace(',', '§').replace('.', ',').replace('§', '.')
    return s


def pct(v, casas=1, sufixo='%'):
    if v is None or pd.isna(v):
        return '—'
    return ('%+.*f' % (casas, v)).replace('.', ',') + sufixo


def _janela(f, ids, ini, fim):
    s = f[f['ID_Indicador'].isin(ids) & (f['Data'] > ini) & (f['Data'] <= fim)]
    den = s['Denominador'].sum()
    if not len(s) or den == 0:
        return None
    return s['Numerador'].sum() / den


def calcular():
    f = pd.read_parquet(BASE + r'\fato_indicadores.parquet')
    d = pd.read_parquet(BASE + r'\dim_indicadores.parquet')
    alvo = d.set_index('ID_Indicador')[['Target_Min', 'Target_Max']]
    d30 = pd.Timedelta(days=30)

    out = {'ult': f['Data'].max()}
    for ind in IX.TODOS:
        ids = ind['ids']
        r = {'v': None, 'ant': None, 'rmin': None, 'rmax': None}
        if ids:
            sub = f[f['ID_Indicador'].isin(ids)]
            if len(sub):
                fim = sub['Data'].max()
                r['v'] = _janela(f, ids, fim - d30, fim)
                r['ant'] = _janela(f, ids, fim - 2 * d30, fim - d30)
            vistos = alvo.reindex(ids)
            for c, k in (('Target_Min', 'rmin'), ('Target_Max', 'rmax')):
                vs = vistos[c].dropna()
                r[k] = float(vs.max()) if len(vs) else None
        g = ind['fator']
        for k in ('v', 'ant', 'rmin', 'rmax'):
            if r[k] is not None:
                r[k] = r[k] * g
        r['ref'] = r['rmax'] if ind['tipo'] in ('menor', 'faixa') else r['rmin']
        r['at'] = (r['v'] / r['ref']) if (r['v'] is not None and r['ref']) else None
        if r['v'] is not None and r['ant'] not in (None, 0):
            r['var'] = (r['v'] / r['ant'] - 1) * 100 if ind['tipo_var'] == '%' else (r['v'] - r['ant'])
        else:
            r['var'] = None
        out[ind['k']] = r
    return out


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    c = calcular()
    print('última data da base:', c['ult'].date())
    print('%-18s %10s %10s %10s %10s %8s' % ('indicador', 'valor', 'anterior', 'ref', 'atingim.', 'var'))
    for ind in IX.TODOS:
        r = c[ind['k']]
        print('%-18s %10s %10s %10s %10s %8s' % (
            ind['k'], num(r['v'], ind['dec']), num(r['ant'], ind['dec']),
            num(r['ref'], ind['dec_ref']),
            ('%.0f%%' % (r['at'] * 100)) if r['at'] else '—',
            pct(r['var'], 1, '%' if ind['tipo_var'] == '%' else ' p.p.')))
