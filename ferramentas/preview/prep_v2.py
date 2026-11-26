# -*- coding: utf-8 -*-
"""Lado do preview da Visão Geral v2: as regras em Python e o HTML com números reais.

O gerar_v2.py escreve as MESMAS regras em DAX. O que está aqui é o espelho que o
preview usa e contra o qual a medida é conferida:
  sit()      a situação do indicador ('d' dentro, 'a' atenção, 'f' fora, 's' sem meta, 'n' sem leitura)
  frase()    o desvio em palavras ("22% acima" + "do teto")
  ponteiro() a posição do ponteiro no medidor
  serie()    os pontos do minigráfico, em baldes

    python prep_v2.py      # roda as conferências das regras (não lê a planilha)
"""
import math
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import molde_v2 as M
import indicadores_op as IX
import dados_op
from dados_op import num, pct
from prep_op import faixa
from estilo_v2 import *

TRACO = '&#8212;'
PONTO = ' &#183; '
KIND = {'menor': 'max', 'maior': 'min', 'faixa': 'faixa'}
IND = {i['k']: i for i in IX.TODOS}

# ---- o que vai em cada visual (cadastro; o gerar_v2 usa o mesmo) ------------
COLUNAS = [('eebc', IX.EEBC, True), ('tmbr', IX.TMBR, False), ('or', IX.OR, True)]     # (etapa, linhas, estreito)
GRUPOS = [('PLANTA' + PONTO + 'TOTAL', False, ['quimicos', 'energia']),
          ('TMBR' + PONTO + 'UTILIDADES', True, ['coagulante', 'biologico']),
          ('OR' + PONTO + 'UTILIDADE E BLEND', True, ['energia_or', 'blend']),
          ('PLANTA' + PONTO + 'BALAN&#199;O', False, ['perdas'])]
W_MEDIDOR = {'perdas': 308}        # o cartão de Perdas ocupa a coluna inteira
HEROI = 'clientes'
BLEND = 'blend'
NIVEL = {0: ('SEM DADOS', PAINEL, LINHA, SEC), 1: ('DADOS EM DIA', PAINEL, LINHA, TEXTO),
         2: ('DADOS PENDENTES', ATENCAO, ATENCAO, '#1c1500'), 3: ('DADOS ATRASADOS', FORA, FORA, '#1c0508')}
SEM = {'s': 'sem meta', 'n': 'sem leitura'}


def um(ind):
    """A linha pequena sob o nome: unidade e meta."""
    meta = IX.meta_txt(ind)
    if meta is None:
        if ind['escala']:
            return 'sem meta' + PONTO + '0 a %s%s' % (IX.br(ind['escala']), ind['unidade'])
        return ind['unidade']
    return (ind['unidade'] + PONTO + meta) if ind['unidade'] else meta


def sufixo(ind):
    return '%' if ind['unidade'] == '%' else ''


# ------------------------------------------------------------------- regras
def arred(v, casas=0):
    """Arredonda como o ROUND do DAX: meio para longe do zero, sobre os 15 dígitos
    significativos do número (3,42 / 0,40 é 8,55, e não 8,549999999999999)."""
    return float(Decimal('%.15g' % float(v)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP))


def sit(v, ind):
    if v is None:
        return 'n'
    return IX.cor_de(v, ind['meta_min'], ind['meta_max'], ind['tipo'], 'd', 'a', 'f', 's')


def limite(v, ind):
    """O limite que o valor rompeu: o teto, se passou dele; o piso, se ficou abaixo."""
    if ind['meta_max'] is not None and v > ind['meta_max']:
        return ind['meta_max']
    if ind['meta_min'] is not None and v < ind['meta_min']:
        return ind['meta_min']
    return None


def frase(v, ind):
    """(quantidade, referência, extremo). Só faz sentido fora da zona da meta."""
    L = limite(v, ind)
    if L is None:
        return '', '', False
    acima = v > L
    r = v / L if L else 0.0
    lado = ' acima' if acima else ' abaixo'
    extremo = (acima and r >= 2) or ((not acima) and r <= 0.5)
    if ind['k'] in ABSOLUTOS:
        um_, varios = ABSOLUTOS[ind['k']]
        d = arred(abs(v - L), ind['dec'])
        if d == 0:
            return 'menos de 1 ' + um_ + lado, 'da faixa', extremo
        return IX.br(d, ind['dec']) + ' ' + (um_ if d == 1 else varios) + lado, 'da faixa', extremo
    if acima and r >= 2:
        return IX.br(arred(r, 1), 1) + ' vezes', 'o teto', extremo
    n = arred(abs(r - 1) * 100)
    return (('menos de 1%' if n < 1 else '%d%%' % n) + lado), ('do teto' if acima else 'do piso'), extremo


def ponteiro(v, ind):
    """(posição bruta, posição no trilho de 4 a 156) pela escala do medidor."""
    if KIND[ind['tipo']] == 'faixa':
        bruto = 57.2 + 45.6 * (v - ind['meta_min']) / (ind['meta_max'] - ind['meta_min'])
    else:
        bruto = 4 + 0.95 * (v / IX.referencia(ind) * 100)
    return bruto, max(4.0, min(156.0, bruto))


def medidor(v, ind, s, W=160):
    kind = KIND[ind['tipo']]
    if s in 'sn':
        return M.medidor(kind, 's', {'txt': SEM[s]}, W)
    X = M.escala(W)
    bruto, x = ponteiro(v, ind)
    x = X(x)
    if s == 'd':
        return M.medidor(kind, 'd', {'x': M.r1(x), 'xt': M.r1(x - 5)}, W)
    if bruto > 156:
        return M.medidor(kind, 'dir', {'cor': COR[s], 'corte': CORTE[s]}, W)
    if bruto < 4:
        return M.medidor(kind, 'esq', {'cor': COR[s], 'corte': CORTE[s]}, W)
    if kind == 'max':
        a, b = X(99), x
    elif kind == 'min':
        a, b = x, X(99)
    elif bruto > 102.8:
        a, b = X(102.8), x
    else:
        a, b = x, X(57.2)
    return M.medidor(kind, s, {'x': M.r1(x), 'xt': M.r1(x - (6 if s == 'a' else 7)), 'a': M.r1(a), 'w': M.r1(b - a)}, W)


def medidor_escala(v, ind, W=160):
    x = 4 + (W - 8) * max(0.0, min(1.0, v / ind['escala']))
    return M.medidor_escala({'x': M.r1(x), 'xt': M.r1(x - 5), 'w': M.r1(x - 4)}, W)


# --------------------------------------------------------------- minigráfico
def passo(dias):
    return int(math.ceil(dias / float(BALDES)))


def serie(longa, ind, fim, dias, hoje):
    """Os pontos do período (fim - dias, fim], em baldes de `passo` dias: [(balde, média)]."""
    if fim is None:
        return []
    s = dados_op._serie(longa, ind, hoje)
    s = s[(s.index > fim - pd.Timedelta(days=dias)) & (s.index <= fim)] * ind['fator']
    if not len(s):
        return []
    d0 = fim - pd.Timedelta(days=dias - 1)
    b = ((s.index - d0).days // passo(dias))
    g = s.groupby(b).mean()
    return [(int(k), float(m)) for k, m in g.items()]


def geometria(pontos, dias, v, ind, geo):
    """As coordenadas do minigráfico: escala que inclui a meta e corta em ESCALA_MINI vezes
    o maior entre o valor do período e a meta. Devolve (x, y, hi, lo) como funções e números."""
    W, H, mx, my = geo
    lims = [l for l in (ind['meta_min'], ind['meta_max']) if l is not None]
    vals = [m for _, m in pontos]
    teto = ESCALA_MINI * max([v] + lims)
    hi = min(max(vals + lims), teto)
    lo = min(vals + lims)
    am = (hi - lo) if hi > lo else 1.0
    nb = max((dias - 1) // passo(dias), 1)
    x = lambda b: mx + (W - 2 * mx) * b / float(nb)
    y = lambda val: (H - my) - (H - 2 * my) * (min(val, hi) - lo) / am
    return x, y


def mini(pontos, dias, v, ind, s, geo=M.GEO_LINHA):
    if len(pontos) < 2:
        return ''
    W, H = geo[0], geo[1]
    x, y = geometria(pontos, dias, v, ind, geo)
    mi, ma = ind['meta_min'], ind['meta_max']
    if mi is not None and ma is not None:
        zy, zh = y(ma), y(mi) - y(ma)
    elif ma is not None:
        zy, zh = y(ma), H - y(ma)
    else:
        zy, zh = 0.0, y(mi)
    lim = ''.join('M0 %sH%d' % (M.r1(y(l)), W) for l in (ma, mi) if l is not None)
    L = limite(v, ind)
    return M.mini(s, {'zy': M.r1(zy), 'zh': M.r1(zh), 'lim': lim,
                      'pts': ' '.join(M.r1(x(b)) + ',' + M.r1(y(m)) for b, m in pontos),
                      'x0': M.r1(x(pontos[0][0])), 'xn': M.r1(x(pontos[-1][0])),
                      'yl': M.r1(y(L if L is not None else IX.referencia(ind)))}, geo)


def mini_heroi(pontos, dias, v, ind, s):
    if len(pontos) < 2:
        return ''
    x, y = geometria(pontos, dias, v, ind, M.GEO_HEROI)
    return M.mini_heroi({'pts': ' '.join(M.r1(x(b)) + ',' + M.r1(y(m)) for b, m in pontos),
                         'x0': M.r1(x(pontos[0][0])), 'xn': M.r1(x(pontos[-1][0])),
                         'yf': M.r1(y(pontos[-1][1])), 'ym': M.r1(y(IX.referencia(ind))),
                         'cor': '#5cc0ff' if s not in 'af' else COR[s]})


# ----------------------------------------------------------------- textos
def cor_sit(s):
    return COR.get(s, SEC)


def dica_dados(c, ind, com_ant):
    r = c[ind['k']]
    s = sit(r['v'], ind)
    d = {'nome': ind['nome'], 'unidade': ind['unidade'], 'meta': IX.meta_txt(ind), 'cor': cor_sit(s),
         'situacao': IX.cor_de(r['v'], r['rmin'], r['rmax'], ind['tipo'], *IX.SITUACAO),
         'periodo': faixa(r['fim'], c['dias']),
         'pct': TRACO if r['at'] is None else '%.0f%%' % arred(r['at'] * 100)}
    if com_ant:
        d.update({'valor': num(r['v'], ind['dec']), 'ant': num(r['ant'], ind['dec']),
                  'ant_periodo': faixa(r['fim'] and r['fim'] - pd.Timedelta(days=c['dias']), c['dias'])})
    return d


def variacao(c, ind, grande=False):
    r = c[ind['k']]
    v = r['var']
    if v is None:
        return M.variacao({'seta': 'M3 8h10', 'var': TRACO, 'rot': ''}, grande)
    boa = (v < 0) if ind['tipo'] == 'menor' else (v > 0)
    rot = '' if (v == 0 or ind['escala']) else ('melhorou' if boa else 'piorou')
    return M.variacao({'seta': M.SETA['+' if v >= 0 else '-'],
                       'var': pct(v, 1, '%' if ind['tipo_var'] == '%' else ' p.p.'), 'rot': rot}, grande)


# ----------------------------------------------------------------- colunas
def linha(c, S, ind, i, n, estreito, sem_mini):
    r = c[ind['k']]
    v = r['v']
    s = sit(v, ind)
    onde = 'left:12px;margin:3px 0;' + ('top:100%' if i < (n + 1) // 2 else 'bottom:100%')
    d = {'nome': ind['nome'], 'um': um(ind), 'valor': num(v, ind['dec']), 'medidor': medidor(v, ind, s),
         'dica': M.dica(dica_dados(c, ind, False), onde)}
    if s not in 'af':
        return M.linha(d, 'd', estreito)
    qtd, ref, extremo = frase(v, ind)
    d.update({'q': qtd, 'ref': ref, 'frase_css': M.estilo_frase(s, extremo),
              'mini': '' if sem_mini else mini(S[ind['k']], c['dias'], v, ind, s)})
    return M.linha(d, s, estreito)


def coluna(c, S, etapa, itens, estreito):
    sits = [sit(c[i['k']]['v'], i) for i in itens]
    nf, na, nd = sits.count('f'), sits.count('a'), sits.count('d')
    com_meta = sum(1 for i in itens if IX.referencia(i) is not None)
    if nf or na:
        ver = M.ver_alerta((M.ver_fora(nf) if nf else '') + (M.ver_atencao(na, not nf) if na else ''))
    else:
        ver = M.ver_ok(nd, com_meta)
    sem_mini = len(itens) >= CORTE_MINI[0] and nf + na >= CORTE_MINI[1]
    corpo = M.bloco({
        'borda': FORA if nf else (ATENCAO if na else LINHA), 'fundo': CAB_FORA if nf else CAB_CALMO, 'veredito': ver,
        'fita': ''.join(M.segmento(s if s in 'af' else ('d' if s == 'd' else 's')) for s in sits),
        'linhas': ''.join(linha(c, S, ind, i, len(itens), estreito, sem_mini) for i, ind in enumerate(itens))})
    t = {'cor': FORA if nf else AZUL, 'fundo': NO_FORA if nf else PAINEL, 'lig': FORA if nf else LIG}
    if etapa == 'or':
        b = IND[BLEND]
        t['blend'] = num(c[BLEND]['v'], b['dec']) + '%'
    return M.coluna(M.no(etapa, t), corpo)


def clientes(c, S):
    ind = IND[HEROI]
    r = c[HEROI]
    v = r['v']
    s = sit(v, ind)
    fora = s == 'f'
    destaque = s in 'af'
    cor = COR[s] if destaque else TEXTO
    if v is None:
        med = M.medidor_heroi({'x': '4.0', 'xt': '-3.0', 'cor': TEXTO, 'falta': ''})
    else:
        x = 4 + 300 * max(0.0, min(160.0, v / r['ref'] * 100)) / 160.0
        falta = M.falta_heroi(s, {'x': M.r1(min(x, 191.5)), 'w': M.r1(abs(191.5 - x))}) if destaque else ''
        med = M.medidor_heroi({'x': M.r1(x), 'xt': M.r1(x - 7), 'cor': cor, 'falta': falta})
    corpo = M.heroi({
        'borda': COR[s] if destaque else AZUL, 'cor_valor': (';color:' + COR[s]) if destaque else '',
        'valor': num(v, ind['dec']), 'unidade': ind['unidade'], 'marca': M.MARCA[s if s in 'adf' else 's'],
        'cor_pct': cor_sit(s), 'pct': TRACO if r['at'] is None else '%.0f%%' % arred(r['at'] * 100),
        'meta': IX.meta_txt(ind), 'medidor': med,
        'mini': mini_heroi(S[HEROI], c['dias'], v, ind, s) if v is not None else '',
        'de': TRACO if r['fim'] is None else (r['fim'] - pd.Timedelta(days=c['dias'] - 1)).strftime('%d/%m'),
        'ate': TRACO if r['fim'] is None else r['fim'].strftime('%d/%m'),
        'variacao': variacao(c, ind, True),
        'dica': M.dica(dica_dados(c, ind, True), 'left:10px;top:118px', True)})
    return M.coluna(M.no(HEROI, {'cor': FORA if fora else AZUL, 'fundo': NO_FORA if fora else '#0a2a47',
                                 'lig': FORA if fora else AZUL}), corpo)


# -------------------------------------------------------------- utilidades
def cartao(c, S, ind, lado):
    r = c[ind['k']]
    v = r['v']
    s = sit(v, ind)
    W = W_MEDIDOR.get(ind['k'], 160)
    d = {'nome': ind['nome'], 'um': um(ind), 'valor': num(v, ind['dec']), 'sufixo': M.sufixo(sufixo(ind)),
         'variacao': variacao(c, ind), 'dica': M.dica(dica_dados(c, ind, True), 'top:0;' + lado)}
    if IX.referencia(ind) is None:       # sem meta: com escala própria (Blend) ou só o anel
        if ind['escala'] and v is not None:
            d['medidor'] = medidor_escala(v, ind, W)
            return M.cartao(d, 'e')
        d['medidor'] = M.medidor('max', 's', {'txt': SEM['s' if v is not None else 'n']}, W)
        return M.cartao(d, 's')
    d['medidor'] = medidor(v, ind, s, W)
    if s not in 'af':
        d['pct'] = TRACO if r['at'] is None else '%.0f%%' % arred(r['at'] * 100)
        return M.cartao(d, 'd')
    qtd, ref, extremo = frase(v, ind)
    d.update({'q': qtd, 'ref': ref, 'frase_css': M.estilo_frase(s, extremo),
              'mini': mini(S[ind['k']], c['dias'], v, ind, s, M.GEO_CARTAO)})
    return M.cartao(d, s)


def utilidades(c, S):
    grupos = []
    for g, (titulo, ligado, ks) in enumerate(GRUPOS):
        lado = 'left:0' if g < 2 else 'right:0'
        grupos.append(M.grupo(titulo, ligado, ''.join(cartao(c, S, IND[k], lado) for k in ks)))
    return M.utilidades(grupos)


# ---------------------------------------------------------- faixa de situação
def contagem(c):
    sits = [sit(c[i['k']]['v'], i) for i in IX.TODOS]
    return {'f': sits.count('f'), 'a': sits.count('a'), 'd': sits.count('d'), 's': sits.count('s') + sits.count('n')}


def situacao(c):
    n = contagem(c)
    def um_(forma, rotulo, cor):
        zero = n[forma] == 0 and forma != 's'
        apag = forma == 's'
        cn = TRAC if zero else (cor if forma in 'af' else (SEC if apag else TEXTO))
        return M.contador(M.marca_cont(forma, TRAC if zero else cor),
                          {'n': '%d' % n[forma], 'cor_n': cn, 'rotulo': rotulo,
                           'cor_r': SEC if (zero or apag) else TEXTO, 'peso': '400' if apag else '600'})
    return M.situacao(len(IX.TODOS), um_('f', 'fora da meta', FORA) + um_('a', 'em atenção', ATENCAO)
                      + um_('d', 'dentro da meta', DENTRO) + um_('s', 'sem meta', SEC))


def dados(a):
    """O estado dos dados, a partir de dados_op.atualizacao()."""
    titulo, fundo, borda, tinta = NIVEL[a['nivel']]
    if a['atraso'] is None:
        ha, ate, dia = TRACO, TRACO, TRACO
    else:
        ha = 'hoje' if a['atraso'] <= 0 else 'ontem' if a['atraso'] == 1 else 'há %d dias' % a['atraso']
        ate, dia = a['dados'].strftime('%d/%m'), a['dados'].strftime('%d/%m/%Y')
    return M.dados({'fundo': fundo, 'borda': borda, 'tinta': tinta, 'titulo': titulo, 'ha': ha, 'ate': ate,
                    'dados': dia, 'plan': a['plan'].strftime('%d/%m %H:%M'), 'bi': a['bi'].strftime('%d/%m %H:%M'),
                    'falta': IX.FALTA[a['falta']]})


def periodo(c):
    n, exatas = c['dias'], c['exatas']
    geral = c['ate'] if exatas else c['ult']
    return M.periodo({'rotulo': '%s%s%d %s' % (IX.ROTULO_PERIODO[exatas], PONTO, n, 'dia' if n == 1 else 'dias'),
                      'valor': faixa(geral, n), 'completo': faixa(geral, n, '%d/%m/%Y'),
                      'nota': IX.NOTA_PERIODO[exatas]})


def series(c, longa, hoje):
    return {i['k']: serie(longa, i, c[i['k']]['fim'], c['dias'], hoje) for i in IX.TODOS}


def paineis(c, S, a):
    """O HTML de cada visual da página: c = dados_op.calcular(), S = series(), a = dados_op.atualizacao()."""
    out = {etapa: coluna(c, S, etapa, itens, estreito) for etapa, itens, estreito in COLUNAS}
    out.update({'clientes': clientes(c, S), 'utilidades': utilidades(c, S), 'situacao': situacao(c),
                'dados': dados(a), 'periodo': periodo(c), 'legenda': M.legenda()})
    return out


# ------------------------------------------- casos de teste (valores fictícios)
# 'hoje' são os números do período 03/11 a 18/11/2026, do print que serviu de base ao
# desenho. Os outros forçam os extremos do destaque no lugar. Nenhum lê a planilha.
HOJE = dict(retrolavagem=10, dqo=40, nh3=4.1, condutividade=356, dureza=94, idade_lodo=23, fm=0.05, ptm=0.14,
            permeabilidade=114, turbidez=3.42, fluxo=21.3, sdi=1.8, dp_skid_1=1.9, dp_skid_2=1.6, dp_skid_3=2.5,
            quimicos=0.1272, energia=0.91, energia_or=0.125, biologico=4.5, coagulante=20.8, clientes=343.3,
            blend=25.5, perdas=14.0)
VAR_HOJE = dict(quimicos=-4.7, energia=-3.4, energia_or=4.1, biologico=12.5, coagulante=29.3, clientes=13.8,
                blend=-1.2, perdas=-0.1)
T6 = dict(idade_lodo=9, ptm=0.74, permeabilidade=48, turbidez=12.4, fluxo=12.4)
E5 = dict(retrolavagem=19, dqo=148, nh3=27.5, condutividade=1430, dureza=131)
O4 = dict(sdi=4.2, dp_skid_1=10.5, dp_skid_2=4.4, dp_skid_3=5.1)
UT = dict(quimicos=0.15, energia=1.21, energia_or=1.10, perdas=22.4)
CALMO = dict(idade_lodo=20, fm=0.12, permeabilidade=180, turbidez=0.21, quimicos=0.11, coagulante=15.2)
CASOS = {
    'hoje': {},
    't1': dict(T6, condutividade=1430, dp_skid_2=3.7),                       # TMBR com as 6 linhas fora
    't2': dict(E5, **dict(T6, **dict(O4, **dict(UT, nh3=21.6, idade_lodo=23, sdi=3.2, dp_skid_2=3.7, clientes=274.5)))),
    't3': dict(E5, **dict(T6, **dict(O4, **dict(UT, clientes=274.5)))),      # tudo fora
    't4': dict(CALMO),                                                       # nenhum desvio
    't5': dict(CALMO, turbidez=3.42, dureza=104, dp_skid_3=4.6, clientes=296.3),
    't6': dict(permeabilidade=48, turbidez=12.4),                            # TMBR com 4 destaques
    't7': dict(CALMO, turbidez=None, dqo=None),                              # indicadores sem leitura
}
ONDA = [0.02, -0.06, 0.09, 0.01, -0.08, 0.05, 0.12, -0.03, -0.10, 0.04, 0.08, -0.05, 0.03, 0.10, -0.02, 0.0]


def caso(nome):
    """(c, S, a) fictícios, no formato de dados_op.calcular(), series() e atualizacao()."""
    valores = dict(HOJE, **CASOS[nome])
    fim, dias = pd.Timestamp('2026-11-18'), 16
    c = {'ult': fim, 'dias': dias, 'exatas': True, 'ate': fim}
    S = {}
    for n, ind in enumerate(IX.TODOS):
        v = valores[ind['k']]
        r = {'v': v, 'ant': None, 'fim': fim, 'rmin': ind['meta_min'], 'rmax': ind['meta_max'],
             'ref': IX.referencia(ind), 'var': None}
        r['at'] = (v / r['ref']) if (v is not None and r['ref']) else None
        if v is not None and ind['k'] in VAR_HOJE:
            r['var'] = VAR_HOJE[ind['k']]
            r['ant'] = v / (1 + r['var'] / 100.0) if ind['tipo_var'] == '%' else v - r['var']
        c[ind['k']] = r
        S[ind['k']] = [] if v is None else [(i, v * (1 + ONDA[(i + 3 * n) % 16])) for i in range(dias)]
    a = {'nivel': 3, 'atraso': 7, 'dados': fim, 'plan': pd.Timestamp('2026-11-19 08:42'),
         'bi': pd.Timestamp('2026-11-25 09:10'), 'falta': 'origem'}
    return c, S, a


# ------------------------------------------------------------- conferências
def conferir():
    """As regras, em valores conhecidos. Para a tela e o DAX nunca saírem do combinado."""
    f = lambda k, v: frase(v, IND[k])[:2]
    assert f('fm', 0.05) == ('38% abaixo', 'do piso'), f('fm', 0.05)
    assert f('coagulante', 20.8) == ('22% acima', 'do teto')
    assert f('turbidez', 3.42) == ('8,6 vezes', 'o teto'), f('turbidez', 3.42)
    assert f('idade_lodo', 23) == ('1 dia acima', 'da faixa')
    assert f('idade_lodo', 9) == ('9 dias abaixo', 'da faixa')
    assert f('idade_lodo', 22.3) == ('menos de 1 dia acima', 'da faixa')
    assert f('quimicos', 0.1272) == ('6% acima', 'do teto')
    assert frase(3.42, IND['turbidez'])[2] and frase(48, IND['permeabilidade'])[2]
    assert not frase(20.8, IND['coagulante'])[2]
    assert frase(10, IND['retrolavagem']) == ('', '', False)
    assert [sit(v, IND['turbidez']) for v in (0.4, 0.44, 0.45, None)] == ['d', 'a', 'f', 'n']
    assert sit(25.5, IND['blend']) == 's' and sit(None, IND['blend']) == 'n'
    assert arred(0.5) == 1 and arred(2.5) == 3 and arred(8.55, 1) == 8.6
    assert ponteiro(0.4, IND['turbidez'])[1] == 99.0 and ponteiro(3.42, IND['turbidez'])[0] > 156
    assert abs(ponteiro(18, IND['idade_lodo'])[1] - 57.2) < 1e-9 and abs(ponteiro(22, IND['idade_lodo'])[1] - 102.8) < 1e-9
    # nenhuma faixa em "atenção" pode cair fora do trilho: aí o medidor de atenção não teria como desenhar
    for ind in IX.TODOS:
        if ind['tipo'] == 'faixa':
            for v in (ind['meta_min'] * (1 - IX.TOLERANCIA), ind['meta_max'] * (1 + IX.TOLERANCIA)):
                assert 4 <= ponteiro(v, ind)[0] <= 156, ind['k']
    for nome in CASOS:
        c, S, a = caso(nome)
        n = contagem(c)
        assert sum(n.values()) == len(IX.TODOS) == 23, nome
        for k, h in paineis(c, S, a).items():
            assert '"' not in h, (nome, k, h[max(0, h.index('"') - 60):h.index('"') + 20])
            assert u'§' not in h, (nome, k)
            assert len(h) < 32000, (nome, k, len(h))
    c, S, a = caso('hoje')
    assert contagem(c) == {'f': 3, 'a': 2, 'd': 16, 's': 2}, contagem(c)
    print('regras conferidas:', len(CASOS), 'casos, 23 indicadores')
    for k, h in paineis(c, S, a).items():
        print('   %-11s %6d caracteres de HTML' % (k, len(h)))


if __name__ == '__main__':
    conferir()
