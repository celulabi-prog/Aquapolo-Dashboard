# -*- coding: utf-8 -*-
"""Converte os dados reais em texto pronto para o molde (lado do preview)."""
import molde_op as M
import indicadores_op as IX
import pandas as pd
import dados_op
from dados_op import num, pct
from estilo_op import *

SETA_CIMA, SETA_BAIXO, TRACO = '&#9650;', '&#9660;', '&#8212;'
GRAD = {'CAB_AZUL': CAB_AZUL, 'CAB_TEAL': CAB_TEAL}


def cor(r, ind):
    return IX.cor_de(r['v'], r['rmin'], r['rmax'], ind['tipo'],
                     VERDE, AMARELO, VERMELHO, CINZA)


def faixa(fim, dias, fmt='%d/%m'):
    """As datas de um período de `dias` dias que termina em `fim`."""
    if fim is None:
        return TRACO
    if dias == 1:
        return fim.strftime(fmt)
    return (fim - pd.Timedelta(days=dias - 1)).strftime(fmt) + ' a ' + fim.strftime(fmt)


def comum(c, ind, alt):
    """O que a linha e o cartão têm em comum: os textos do cadastro e os números do período."""
    r = c[ind['k']]
    d = IX.textos(ind)
    d.update({
        'valor': num(r['v'], ind['dec']), 'cor': cor(r, ind),
        'situacao': IX.cor_de(r['v'], r['rmin'], r['rmax'], ind['tipo'], *IX.SITUACAO),
        'barra': M.barra('%.0f' % IX.largura(r['v'], ind), cor(r, ind), IX.marcadores(ind), alt),
        'pct': TRACO if r['at'] is None else '%.0f%%' % (r['at'] * 100),
        'periodo': faixa(r['fim'], c['dias'])})
    return d


def linhas(c, itens):
    return ''.join(M.linha_ind(comum(c, ind, 24), i, len(itens)) for i, ind in enumerate(itens))


def cartoes(c, itens):
    out = ''
    for i, ind in enumerate(itens):
        r = c[ind['k']]
        v = r['var']
        boa = (v is not None) and ((v < 0) if ind['tipo'] == 'menor' else (v > 0))
        d = comum(c, ind, 20)
        d.update({
            'seta': '' if v is None else (SETA_CIMA if v >= 0 else SETA_BAIXO),
            'var': TRACO if v is None else pct(v, 1, '%' if ind['tipo_var'] == '%' else ' p.p.'),
            'cor_var': CINZA if v is None else (VERDE if boa else VERMELHO),
            'ant': num(r['ant'], ind['dec']),
            'ant_periodo': faixa(r['fim'] and r['fim'] - pd.Timedelta(days=c['dias']), c['dias'])})
        out += M.cartao_ind(d, i, len(itens))
    return out


def status(a):
    """O indicador de atualização, a partir de dados_op.atualizacao()."""
    palavra, cor_nome = IX.NIVEIS[a['nivel']]
    if a['atraso'] is None:
        rotulo, dados = 'Sem leitura na planilha', TRACO
    else:
        ha = ('hoje' if a['atraso'] <= 0 else 'ontem' if a['atraso'] == 1
              else 'há %d dias' % a['atraso'])
        rotulo = 'Dados até ' + a['dados'].strftime('%d/%m') + ' &#183; ' + ha
        dados = a['dados'].strftime('%d/%m/%Y')
    return M.status({'cor': COR[cor_nome], 'palavra': palavra, 'rotulo': rotulo, 'dados': dados,
                     'plan': a['plan'].strftime('%d/%m %H:%M'),
                     'bi': a['bi'].strftime('%d/%m %H:%M'), 'falta': IX.FALTA[a['falta']]})


def periodo(c):
    """As datas do período exibido. Com um tamanho fixo, o período vai até a última
    leitura da planilha (o de cada indicador, até a última leitura dele, fica na aba
    do indicador). Com datas exatas: o intervalo escolhido, igual para todos."""
    n, exatas = c['dias'], c['exatas']
    geral = c['ate'] if exatas else c['ult']
    return M.periodo({'rotulo': '%s &#183; %d %s' % (IX.ROTULO_PERIODO[exatas], n, 'dia' if n == 1 else 'dias'),
                      'valor': faixa(geral, n), 'completo': faixa(geral, n, '%d/%m/%Y'),
                      'nota': IX.NOTA_PERIODO[exatas]})


def paineis(c):
    out = {}
    for p in IX.PAINEIS:
        d = {'titulo': p['titulo'], 'sub': p['sub'], 'icones': p['icones'],
             'grad': GRAD[p['grad']], 'sub_dir': p.get('sub_dir', True)}
        if p['forma'] == 'linhas':
            out[p['k']] = M.painel_linhas(d, linhas(c, p['itens']))
        else:
            out[p['k']] = M.painel_cartoes(d, cartoes(c, p['itens']))
    out['rodape'] = M.rodape()
    out['status'] = status(dados_op.atualizacao(c))
    out['periodo'] = periodo(c)
    return out
