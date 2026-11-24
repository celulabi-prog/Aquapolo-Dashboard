# -*- coding: utf-8 -*-
"""Refaz em Python as contas das medidas do Painel Operacional, para o preview.

Espelha o que o Power BI faz com a planilha 'Dados BI.xlsx':
  ler()      = a consulta M da tabela 'Dados BI' (Data, Indicador, Valor; só números)
  calcular() = as medidas DAX '<indicador> Período' e '<indicador> Período Anterior'
  atualizacao() = a conta da medida 'HTML Status' (indicador de atualização)

A planilha só é lida, nunca gravada.

    python dados_op.py                  # os números de hoje, período mensal
    python dados_op.py 2026-09-14       # como o painel estaria nesse dia
    python dados_op.py 2026-09-14 7     # idem, com o seletor em Semanal (7 dias)
"""
import os
import pandas as pd
import indicadores_op as IX

ARQUIVO = r'G:\OME\Operacao\BI\Dados BI.xlsx'     # o mesmo do parâmetro ArquivoDadosBI
ABA = 'Dados BI'


def num(v, casas=0):
    """Número no formato pt-BR."""
    return '—' if v is None or pd.isna(v) else IX.br(v, casas)


def pct(v, casas=1, sufixo='%'):
    if v is None or pd.isna(v):
        return '—'
    return ('%+.*f' % (casas, v)).replace('.', ',') + sufixo


def ler(arquivo=ARQUIVO):
    """Linha 1 = grupos, linha 2 = nomes, dados da linha 3 em diante. Fica só o que é número."""
    bruto = pd.read_excel(arquivo, sheet_name=ABA, header=None)
    t = bruto.iloc[2:].copy()
    t.columns = ['Data'] + [str(c).strip() for c in bruto.iloc[1, 1:]]
    longa = t.melt(id_vars='Data', var_name='Indicador', value_name='Valor')
    numero = longa['Valor'].map(lambda v: isinstance(v, (int, float)) and not isinstance(v, bool))
    longa = longa[numero & longa['Valor'].notna() & longa['Data'].notna()]
    return longa.assign(Data=pd.to_datetime(longa['Data']), Valor=longa['Valor'].astype(float))


def _serie(longa, ind, hoje):
    """Os dias que valem como leitura do indicador: até hoje e, em geral, diferentes de zero."""
    s = longa[(longa['Indicador'] == ind['coluna']) & (longa['Data'] <= hoje)].set_index('Data')['Valor']
    if ind['conta'] == 'mediana':
        return s[s > 0]
    return s if ind['zero_vale'] else s[s != 0]


def _periodo(s, peso, conta, ini, fim):
    """O número do período (ini, fim], pela conta do indicador."""
    w = s[(s.index > ini) & (s.index <= fim)]
    if not len(w):
        return None
    if conta == 'mediana':
        return float(w.median())
    if conta == 'ponderada':
        p = peso.reindex(w.index).dropna()
        return float((w[p.index] * p).sum() / p.sum()) if p.sum() else None
    return float(w.mean())


def atualizacao(c, agora=None, arquivo=ARQUIVO):
    """Em que pé está a atualização dos dados. No preview, 'Power BI atualizado
    em' é agora: a planilha acabou de ser lida."""
    agora = pd.Timestamp(agora) if agora is not None else pd.Timestamp.now()
    hoje, dados = agora.normalize(), c['ult']
    plan = pd.Timestamp.fromtimestamp(os.path.getmtime(arquivo))
    bi = agora
    atraso = None if pd.isna(dados) else (hoje - dados.normalize()).days
    nivel = (0 if atraso is None else 1 if atraso <= IX.ATRASO_EM_DIA
             else 2 if atraso <= IX.ATRASO_PENDENTE else 3)
    falta = ('nada' if nivel == 1 else 'bi' if bi.normalize() < hoje
             else 'planilha' if plan.normalize() < hoje else 'origem')
    return {'nivel': nivel, 'atraso': atraso, 'dados': dados, 'plan': plan, 'bi': bi, 'falta': falta}


def calcular(hoje=None, dias=None, de=None, ate=None, arquivo=ARQUIVO):
    """dias = o tamanho do período (o que o seletor Período escolhe no Power BI).
    de/ate = a opção Datas exatas: o período é esse intervalo, igual para todos."""
    hoje = pd.Timestamp(hoje) if hoje else pd.Timestamp.today().normalize()
    longa = ler(arquivo)
    faltam = [i['coluna'] for i in IX.TODOS if i['coluna'] not in set(longa['Indicador'])]
    if faltam:
        raise SystemExit('Colunas de indicadores_op.py que não existem (ou estão vazias) na planilha: %s'
                         % faltam)
    peso = longa[longa['Indicador'] == IX.PESO].groupby('Data')['Valor'].mean()
    exatas = de is not None and ate is not None
    if exatas:
        de, ate = pd.Timestamp(de), pd.Timestamp(ate)
    d = pd.Timedelta(days=(ate - de).days + 1 if exatas else int(dias or IX.JANELA))

    validas = longa[(longa['Valor'] != 0) & (longa['Data'] <= hoje)]
    out = {'ult': validas['Data'].max(), 'dias': int(d.days), 'exatas': exatas,
           'ate': ate if exatas else None}
    for ind in IX.TODOS:
        s = _serie(longa, ind, hoje)
        r = {'v': None, 'ant': None, 'fim': None, 'rmin': ind['meta_min'], 'rmax': ind['meta_max']}
        # com datas exatas o período termina no 'até' para todos; senão, na última leitura do indicador
        fim = r['fim'] = ate if exatas else (s.index.max() if len(s) else None)
        if fim is not None:
            r['v'] = _periodo(s, peso, ind['conta'], fim - d, fim)
            r['ant'] = _periodo(s, peso, ind['conta'], fim - 2 * d, fim - d)
        for k in ('v', 'ant'):
            if r[k] is not None:
                r[k] = r[k] * ind['fator']
        r['ref'] = IX.referencia(ind)
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
    c = calcular(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else None)
    a = atualizacao(c, sys.argv[1] if len(sys.argv) > 1 else None)
    print('última data da planilha:', c['ult'].date(), '| período de', sys.argv[2] if len(sys.argv) > 2 else IX.JANELA, 'dias')
    print('atualização: %s (atraso de %s dias) | planilha salva em %s | %s'
          % (IX.NIVEIS[a['nivel']][0], a['atraso'], a['plan'].strftime('%d/%m/%Y %H:%M'), IX.FALTA[a['falta']]))
    print('%-18s %10s %10s %10s %10s %8s' % ('indicador', 'valor', 'anterior', 'ref', 'atingim.', 'var'))
    for ind in IX.TODOS:
        r = c[ind['k']]
        print('%-18s %10s %10s %10s %10s %8s' % (
            ind['k'], num(r['v'], ind['dec']), num(r['ant'], ind['dec']),
            num(r['ref'], ind['dec_ref']),
            ('%.0f%%' % (r['at'] * 100)) if r['at'] else '—',
            pct(r['var'], 1, '%' if ind['tipo_var'] == '%' else ' p.p.')))
