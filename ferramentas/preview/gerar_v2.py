# -*- coding: utf-8 -*-
"""Gera 'Medidas HTML v2.tmdl': as medidas da página Visão Geral v2.

Uma medida por visual, todas com o prefixo 'HTML v2' (nome de medida é único no
modelo). Elas não refazem os números: buscam as medidas '<indicador> Período' e
'<indicador> Período Anterior' da tabela 'Medidas HTML' (gerar_op.py) e só
desenham. O que é novo aqui, em DAX, espelha prep_v2.py:
  situação   _s  'd' dentro, 'a' atenção, 'f' fora, 's' sem meta, 'n' sem leitura
  frase      _q, _rt  o desvio em palavras; _fc  o estilo (etiqueta no extremo)
  medidor    _md  o SVG, com o ponteiro em _x
  minigráfico _mg  a série diária do período, em até BALDES pontos
A forma de cada linha (calma, atenção, fora) é escolhida com SWITCH sobre _s.

Este arquivo NÃO toca em 'Medidas HTML.tmdl' nem na página Visão Geral atual.
"""
import io, pathlib, uuid
import molde_v2 as M
import indicadores_op as IX
import gerar_op as G
import prep_v2 as P
import estilo_op as EO
from estilo_v2 import *

F, texto, numero, nuM, TRACO, T = G.F, G.texto, G.numero, G.nuM, G.TRACO, G.T
REPO = pathlib.Path(__file__).resolve().parents[2]
TABELA = 'Medidas HTML v2'
DESTINO = REPO / 'Dashboard - Aquapolo.SemanticModel' / 'definition' / 'tables' / (TABELA + '.tmdl')
PASTA = 'Visão Geral v2'


def fx(expr):
    """Coordenada de SVG: uma casa e ponto decimal, seja qual for o idioma do relatório."""
    return 'FORMAT ( %s, "0.0", "en-US" )' % expr


def lit(txt):
    return '"' + txt + '"'


def soma(n, letra):
    return '0 + ' + ' + '.join('IF ( _s%d = "%s", 1 )' % (i, letra) for i in range(1, n + 1))


PCT = 'IF ( ISBLANK ( _rf{n} ) || ISBLANK ( _v{n} ), {t}, FORMAT ( DIVIDE ( _v{n}, _rf{n} ), "0%" ) )'


# ----------------------------------------------------- os VAR de um indicador
def vars_base(ind, n, com_ant):
    """Valor, metas, período anterior (gerar_op.bloco_valores) e a situação em letra."""
    L = G.bloco_valores(ind, n, com_ant)
    L.append('VAR _s{n} = SWITCH ( TRUE (), ISBLANK ( _v{n} ), "n", _co{n} = "{vd}", "d", _co{n} = "{am}", "a", '
             '_co{n} = "{vm}", "f", "s" )'.format(n=n, vd=EO.VERDE, am=EO.AMARELO, vm=EO.VERMELHO))
    L.append('VAR _cr{n} = SWITCH ( _s{n}, "f", "{f}", "a", "{a}", "d", "{d}", "{s}" )'
             .format(n=n, f=FORA, a=ATENCAO, d=DENTRO, s=SEC))
    return L


def vars_frase(ind, n):
    """O desvio em palavras. Espelha prep_v2.frase()."""
    L = ['VAR _L{n} = SWITCH ( TRUE (), NOT ISBLANK ( _ma{n} ) && _v{n} > _ma{n}, _ma{n}, '
         'NOT ISBLANK ( _mi{n} ) && _v{n} < _mi{n}, _mi{n} )'.format(n=n),
         'VAR _ac{n} = _v{n} > _L{n}'.format(n=n),
         'VAR _r{n} = DIVIDE ( _v{n}, _L{n} )'.format(n=n),
         'VAR _ex{n} = ( _ac{n} && _r{n} >= 2 ) || ( NOT _ac{n} && _r{n} <= 0.5 )'.format(n=n)]
    lado = 'IF ( _ac{n}, " acima", " abaixo" )'.format(n=n)
    if ind['k'] in ABSOLUTOS:
        um_, varios = ABSOLUTOS[ind['k']]
        L += ['VAR _d{n} = ROUND ( ABS ( _v{n} - _L{n} ), {dec} )'.format(n=n, dec=ind['dec']),
              'VAR _q{n} = IF ( _d{n} = 0, "menos de 1 {um}", FORMAT ( _d{n}, {fmt} ) & IF ( _d{n} = 1, " {um}", " {varios}" ) ) & {lado}'
              .format(n=n, um=um_, varios=varios, fmt=G.FMT[ind['dec']], lado=lado),
              'VAR _rt{n} = "da faixa"'.format(n=n)]
    else:
        L += ['VAR _pc{n} = ROUND ( ABS ( _r{n} - 1 ) * 100, 0 )'.format(n=n),
              'VAR _q{n} = IF ( _ac{n} && _r{n} >= 2, FORMAT ( ROUND ( _r{n}, 1 ), "#,##0.0" ) & " vezes", '
              'IF ( _pc{n} < 1, "menos de 1%", FORMAT ( _pc{n}, "0" ) & "%" ) & {lado} )'.format(n=n, lado=lado),
              'VAR _rt{n} = SWITCH ( TRUE (), _ac{n} && _r{n} >= 2, "o teto", _ac{n}, "do teto", "do piso" )'.format(n=n)]
    L.append('VAR _fc{n} = IF ( _ex{n} && _s{n} = "f", "{et}", "color:" & _cr{n} )'.format(n=n, et=M.ETIQUETA))
    return L


def vars_medidor(ind, n, W=160):
    """O medidor, na forma que a situação pede. Espelha prep_v2.medidor()."""
    kind = P.KIND[ind['tipo']]
    X = M.escala(W)
    k = repr((W - 8) / 152.0)
    if kind == 'faixa':
        bruto = '57.2 + 45.6 * DIVIDE ( _v{n} - _mi{n}, _ma{n} - _mi{n} )'
    else:
        bruto = '4 + 0.95 * DIVIDE ( _v{n}, _rf{n} ) * 100'
    L = [('VAR _br{n} = ' + bruto).format(n=n),
         'VAR _x{n} = 4 + ( MIN ( MAX ( _br{n}, 4 ), 156 ) - 4 ) * {k}'.format(n=n, k=k)]
    x = '_x%d' % n
    if kind == 'max':
        a, w = M.r1(X(99)), fx('%s - %s' % (x, repr(X(99))))
    elif kind == 'min':
        a, w = F(fx(x)), fx('%s - %s' % (repr(X(99)), x))
    else:
        a = F('IF ( _br%d > 102.8, "%s", %s )' % (n, M.r1(X(102.8)), fx(x)))
        w = fx('IF ( _br%d > 102.8, %s - %s, %s - %s )' % (n, x, repr(X(102.8)), repr(X(57.2)), x))
    w = F(w)
    alem = {'cor': F('_cr%d' % n), 'corte': F('IF ( _s%d = "a", "%s", "%s" )' % (n, CORTE['a'], CORTE['f']))}
    casos = ['_s{n} = "s" || _s{n} = "n", '.format(n=n)
             + texto(M.medidor(kind, 's', {'txt': F('IF ( _s%d = "n", "%s", "%s" )' % (n, P.SEM['n'], P.SEM['s']))}, W)),
             '_s%d = "d", ' % n + texto(M.medidor(kind, 'd', {'x': F(fx(x)), 'xt': F(fx(x + ' - 5'))}, W)),
             '_br%d > 156, ' % n + texto(M.medidor(kind, 'dir', alem, W)),
             '_br%d < 4, ' % n + texto(M.medidor(kind, 'esq', alem, W)),
             '_s%d = "a", ' % n + texto(M.medidor(kind, 'a', {'x': F(fx(x)), 'xt': F(fx(x + ' - 6')), 'a': a, 'w': w}, W))]
    L.append('VAR _md%d = SWITCH ( TRUE (), %s, %s )' % (
        n, ', '.join(casos), texto(M.medidor(kind, 'f', {'x': F(fx(x)), 'xt': F(fx(x + ' - 7')), 'a': a, 'w': w}, W))))
    return L


def vars_serie(ind, n, geo):
    """A série diária do período, em baldes, e a escala do minigráfico. Espelha
    prep_v2.serie() e prep_v2.geometria()."""
    lims = [l for l in (ind['meta_min'], ind['meta_max']) if l is not None]
    vezes = '' if ind['fator'] == 1.0 else ' * %s' % numero(ind['fator'])
    return [
        'VAR _d0{n} = _f{n} - _tamanho + 1'.format(n=n),
        ('VAR _t{n} = CALCULATETABLE ( SELECTCOLUMNS ( {T}, "@b", INT ( DIVIDE ( INT ( {T}[Data] - _d0{n} ), _passo ) ), '
         '"@v", {T}[Valor]{vezes} ), {lei}, {T}[Data] >= _d0{n}, {T}[Data] <= _f{n} )')
        .format(n=n, T=T, vezes=vezes, lei=', '.join(G.leituras(ind))),
        'VAR _g{n} = GROUPBY ( _t{n}, [@b], "@m", AVERAGEX ( CURRENTGROUP (), [@v] ) )'.format(n=n),
        'VAR _hi{n} = MIN ( MAX ( MAXX ( _g{n}, [@m] ), {sup} ), {esc} * MAX ( _v{n}, {sup} ) )'
        .format(n=n, sup=numero(max(lims)), esc=ESCALA_MINI),
        'VAR _lo{n} = MIN ( MINX ( _g{n}, [@m] ), {inf} )'.format(n=n, inf=numero(min(lims))),
        'VAR _am{n} = IF ( _hi{n} > _lo{n}, _hi{n} - _lo{n}, 1 )'.format(n=n),
    ]


def xy(n, geo):
    W, H, mx, my = geo
    x = lambda b: '%d + %d * DIVIDE ( %s, _nb )' % (mx, W - 2 * mx, b)
    y = lambda val: '%d - %d * DIVIDE ( MIN ( %s, _hi%d ) - _lo%d, _am%d )' % (H - my, H - 2 * my, val, n, n, n)
    return x, y


def vars_mini(ind, n, geo=M.GEO_LINHA, corte=False):
    """O minigráfico da linha ou do cartão em destaque. Espelha prep_v2.mini()."""
    W, H = geo[0], geo[1]
    x, y = xy(n, geo)
    mi, ma = ind['meta_min'], ind['meta_max']
    if mi is not None and ma is not None:
        zy, zh = fx(y('_ma%d' % n)), fx('( %s ) - ( %s )' % (y('_mi%d' % n), y('_ma%d' % n)))
    elif ma is not None:
        zy, zh = fx(y('_ma%d' % n)), fx('%d - ( %s )' % (H, y('_ma%d' % n)))
    else:
        zy, zh = '"0.0"', fx(y('_mi%d' % n))
    lim = ' & '.join('"M0 " & %s & "H%d"' % (fx(y('_%s%d' % (l, n))), W)
                     for l, v in (('ma', ma), ('mi', mi)) if v is not None)
    L = vars_serie(ind, n, geo) + [
        'VAR _pts{n} = CONCATENATEX ( _g{n}, {x} & "," & {y}, " ", [@b], ASC )'
        .format(n=n, x=fx(x('[@b]')), y=fx(y('[@m]'))),
    ]
    t = {'zy': F(zy), 'zh': F(zh), 'lim': F(lim), 'pts': F('_pts%d' % n),
         'x0': F(fx(x('MINX ( _g%d, [@b] )' % n))), 'xn': F(fx(x('MAXX ( _g%d, [@b] )' % n))),
         'yl': F(fx(y('COALESCE ( _L%d, _rf%d )' % (n, n))))}
    some = 'COUNTROWS ( _g%d ) < 2' % n + (' || _semmini' if corte else '')
    L.append('VAR _mg%d = IF ( %s, "", IF ( _s%d = "a", %s, %s ) )'
             % (n, some, n, texto(M.mini('a', t, geo)), texto(M.mini('f', t, geo))))
    return L


def vars_dica(ind, n, onde, com_ant, em_coluna=False):
    """A aba que abre ao passar o mouse. Espelha prep_v2.dica_dados()."""
    d = {'nome': ind['nome'], 'unidade': ind['unidade'], 'meta': IX.meta_txt(ind), 'cor': F('_cr%d' % n),
         'situacao': F('_si%d' % n), 'periodo': F(G.faixa('_f%d' % n)), 'pct': F(PCT.format(n=n, t=TRACO))}
    if com_ant:
        d.update({'valor': F(nuM('_v%d' % n, ind['dec'])), 'ant': F(nuM('_an%d' % n, ind['dec'])),
                  'ant_periodo': F(G.faixa('_f%d' % n, recuo=' - _tamanho'))})
    return ['VAR _dc%d = %s' % (n, texto(M.dica(d, onde, em_coluna)))]


def vars_variacao(ind, n, grande=False):
    """Seta, número e palavra da variação sobre o período anterior. Espelha prep_v2.variacao()."""
    fvar = ('FORMAT ( _dl{n}, "+0.0%;-0.0%" )' if ind['tipo_var'] == '%'
            else 'FORMAT ( _dl{n}, "+0.0;-0.0" ) & " p.p."').format(n=n)
    boa = ('_dl{n} < 0' if ind['tipo'] == 'menor' else '_dl{n} > 0').format(n=n)
    rot = '""' if ind['escala'] else 'IF ( NOT _te{n} || _dl{n} = 0, "", IF ( {boa}, "melhorou", "piorou" ) )'.format(n=n, boa=boa)
    t = {'seta': F('IF ( NOT _te{n}, "M3 8h10", IF ( _dl{n} >= 0, "{s}", "{d}" ) )'.format(n=n, s=M.SETA['+'], d=M.SETA['-'])),
         'var': F('IF ( _te%d, %s, %s )' % (n, fvar, TRACO)), 'rot': F(rot)}
    return ['VAR _vr%d = %s' % (n, texto(M.variacao(t, grande)))]


# -------------------------------------------------------- colunas das etapas
def medida_coluna(etapa, itens, estreito):
    n_it = len(itens)
    corte = n_it >= CORTE_MINI[0]
    L = list(G.VARS_PERIODO) + ['VAR _passo = ROUNDUP ( DIVIDE ( _tamanho, %d ), 0 )' % BALDES,
                                'VAR _nb = MAX ( INT ( DIVIDE ( _tamanho - 1, _passo ) ), 1 )']
    for n, ind in enumerate(itens, start=1):
        L += vars_base(ind, n, False)
    L += ['VAR _nf = ' + soma(n_it, 'f'), 'VAR _na = ' + soma(n_it, 'a'), 'VAR _nd = ' + soma(n_it, 'd')]
    if corte:
        L.append('VAR _semmini = _nf + _na >= %d' % CORTE_MINI[1])
    for n, ind in enumerate(itens, start=1):
        i = n - 1
        onde = 'left:12px;margin:3px 0;' + ('top:100%' if i < (n_it + 1) // 2 else 'bottom:100%')
        L += vars_frase(ind, n) + vars_medidor(ind, n) + vars_mini(ind, n, M.GEO_LINHA, corte) + vars_dica(ind, n, onde, False)
        d = {'nome': ind['nome'], 'um': P.um(ind), 'valor': F(nuM('_v%d' % n, ind['dec'])), 'medidor': F('_md%d' % n),
             'dica': F('_dc%d' % n), 'q': F('_q%d' % n), 'ref': F('_rt%d' % n), 'frase_css': F('_fc%d' % n),
             'mini': F('_mg%d' % n)}
        L.append('VAR _h%d = SWITCH ( _s%d, "f", %s, "a", %s, %s )'
                 % (n, n, texto(M.linha(d, 'f', estreito)), texto(M.linha(d, 'a', estreito)), texto(M.linha(d, 'd', estreito))))
    com_meta = sum(1 for i in itens if IX.referencia(i) is not None)
    L += ['VAR _vc = IF ( _nf > 0, %s, "" ) & IF ( _na > 0, IF ( _nf > 0, %s, %s ), "" )'
          % (texto(M.ver_fora(F('_nf'))), texto(M.ver_atencao(F('_na'), False)), texto(M.ver_atencao(F('_na'), True))),
          'VAR _ver = IF ( _nf + _na = 0, %s, %s )' % (texto(M.ver_ok(F('_nd'), com_meta)), texto(M.ver_alerta(F('_vc')))),
          'VAR _ft = ' + ' & '.join('SWITCH ( _s%d, "f", %s, "a", %s, "d", %s, %s )' % (
              n, lit(M.segmento('f')), lit(M.segmento('a')), lit(M.segmento('d')), lit(M.segmento('s')))
              for n in range(1, n_it + 1))]
    t = {'cor': F('IF ( _nf > 0, "%s", "%s" )' % (FORA, AZUL)), 'fundo': F('IF ( _nf > 0, "%s", "%s" )' % (NO_FORA, PAINEL)),
         'lig': F('IF ( _nf > 0, "%s", "%s" )' % (FORA, LIG))}
    if etapa == 'or':
        L.append('VAR _bl = [%s]' % G.nome_medida(P.IND[P.BLEND]))
        t['blend'] = F(nuM('_bl', P.IND[P.BLEND]['dec'])) + '%'
    corpo = M.bloco({
        'borda': F('IF ( _nf > 0, "%s", IF ( _na > 0, "%s", "%s" ) )' % (FORA, ATENCAO, LINHA)),
        'fundo': F('IF ( _nf > 0, "%s", "%s" )' % (CAB_FORA, CAB_CALMO)), 'veredito': F('_ver'), 'fita': F('_ft'),
        'linhas': F(' & '.join('_h%d' % n for n in range(1, n_it + 1)))})
    L.append('RETURN\n    ' + texto(M.coluna(M.no(etapa, t), corpo)))
    return '\n'.join(L)


# ------------------------------------------------------ entrega aos clientes
def medida_clientes():
    ind, n = P.IND[P.HEROI], 1
    geo = M.GEO_HEROI
    x, y = xy(n, geo)
    dest = '( _s1 = "a" || _s1 = "f" )'
    L = list(G.VARS_PERIODO) + ['VAR _passo = ROUNDUP ( DIVIDE ( _tamanho, %d ), 0 )' % BALDES,
                                'VAR _nb = MAX ( INT ( DIVIDE ( _tamanho - 1, _passo ) ), 1 )']
    L += vars_base(ind, n, True) + vars_serie(ind, n, geo)
    L += ['VAR _pts1 = CONCATENATEX ( _g1, %s & "," & %s, " ", [@b], ASC )' % (fx(x('[@b]')), fx(y('[@m]'))),
          'VAR _mg1 = IF ( ISBLANK ( _v1 ) || COUNTROWS ( _g1 ) < 2, "", %s )' % texto(M.mini_heroi({
              'pts': F('_pts1'), 'x0': F(fx(x('MINX ( _g1, [@b] )'))), 'xn': F(fx(x('MAXX ( _g1, [@b] )'))),
              'yf': F(fx('MAXX ( TOPN ( 1, _g1, [@b], DESC ), %s )' % y('[@m]'))), 'ym': F(fx(y('_rf1'))),
              'cor': F('IF ( %s, _cr1, "#5cc0ff" )' % dest)})),
          'VAR _xh = 4 + 300 * MIN ( MAX ( DIVIDE ( _v1, _rf1 ) * 100, 0 ), 160 ) / 160',
          'VAR _ch = IF ( %s, _cr1, "%s" )' % (dest, TEXTO)]
    falta = {'x': F(fx('MIN ( _xh, 191.5 )')), 'w': F(fx('ABS ( 191.5 - _xh )'))}
    L += ['VAR _fa = IF ( %s, IF ( _s1 = "a", %s, %s ), "" )'
          % (dest, texto(M.falta_heroi('a', falta)), texto(M.falta_heroi('f', falta))),
          'VAR _md1 = IF ( ISBLANK ( _v1 ), %s, %s )' % (
              texto(M.medidor_heroi({'x': '4.0', 'xt': '-3.0', 'cor': TEXTO, 'falta': ''})),
              texto(M.medidor_heroi({'x': F(fx('_xh')), 'xt': F(fx('_xh - 7')), 'cor': F('_ch'), 'falta': F('_fa')})))]
    L += vars_variacao(ind, n, True) + vars_dica(ind, n, 'left:10px;top:118px', True, True)
    data = lambda e: 'IF ( ISBLANK ( _f1 ), %s, FORMAT ( %s, "dd/mm" ) )' % (TRACO, e)
    corpo = M.heroi({
        'borda': F('IF ( %s, _cr1, "%s" )' % (dest, AZUL)), 'cor_valor': F('IF ( %s, ";color:" & _cr1, "" )' % dest),
        'valor': F(nuM('_v1', ind['dec'])), 'unidade': ind['unidade'],
        'marca': F('SWITCH ( _s1, "d", %s, "a", %s, "f", %s, %s )' % tuple(lit(M.MARCA[k]) for k in 'dafs')),
        'cor_pct': F('_cr1'), 'pct': F(PCT.format(n=n, t=TRACO)), 'meta': IX.meta_txt(ind), 'medidor': F('_md1'),
        'mini': F('_mg1'), 'de': F(data('_f1 - _tamanho + 1')), 'ate': F(data('_f1')), 'variacao': F('_vr1'), 'dica': F('_dc1')})
    fora = '_s1 = "f"'
    no = M.no(P.HEROI, {'cor': F('IF ( %s, "%s", "%s" )' % (fora, FORA, AZUL)),
                        'fundo': F('IF ( %s, "%s", "#0a2a47" )' % (fora, NO_FORA)),
                        'lig': F('IF ( %s, "%s", "%s" )' % (fora, FORA, AZUL))})
    L.append('RETURN\n    ' + texto(M.coluna(no, corpo)))
    return '\n'.join(L)


# ----------------------------------------------------------------- utilidades
def html_cartao(ind, n, lado):
    """Os VAR de um cartão e a expressão que escolhe a forma dele. Espelha prep_v2.cartao()."""
    W = P.W_MEDIDOR.get(ind['k'], 160)
    L = vars_base(ind, n, True) + vars_variacao(ind, n) + vars_dica(ind, n, 'top:0;' + lado, True)
    d = {'nome': ind['nome'], 'um': P.um(ind), 'valor': F(nuM('_v%d' % n, ind['dec'])), 'sufixo': M.sufixo(P.sufixo(ind)),
         'variacao': F('_vr%d' % n), 'dica': F('_dc%d' % n)}
    if IX.referencia(ind) is None:
        if ind['escala']:
            L.append('VAR _x{n} = 4 + {w} * MIN ( MAX ( DIVIDE ( _v{n}, {e} ), 0 ), 1 )'.format(n=n, w=W - 8, e=numero(ind['escala'])))
            x = '_x%d' % n
            com = dict(d, medidor=M.medidor_escala({'x': F(fx(x)), 'xt': F(fx(x + ' - 5')), 'w': F(fx(x + ' - 4'))}, W))
            sem = dict(d, medidor=M.medidor('max', 's', {'txt': P.SEM['n']}, W))
            L.append('VAR _h%d = IF ( ISBLANK ( _v%d ), %s, %s )' % (n, n, texto(M.cartao(sem, 's')), texto(M.cartao(com, 'e'))))
        else:
            d['medidor'] = M.medidor('max', 's', {'txt': F('IF ( ISBLANK ( _v%d ), "%s", "%s" )' % (n, P.SEM['n'], P.SEM['s']))}, W)
            L.append('VAR _h%d = %s' % (n, texto(M.cartao(d, 's'))))
        return L
    L += vars_frase(ind, n) + vars_medidor(ind, n, W) + vars_mini(ind, n, M.GEO_CARTAO)
    d.update({'medidor': F('_md%d' % n), 'pct': F(PCT.format(n=n, t=TRACO)), 'q': F('_q%d' % n), 'ref': F('_rt%d' % n),
              'frase_css': F('_fc%d' % n), 'mini': F('_mg%d' % n)})
    L.append('VAR _h%d = SWITCH ( _s%d, "f", %s, "a", %s, %s )'
             % (n, n, texto(M.cartao(d, 'f')), texto(M.cartao(d, 'a')), texto(M.cartao(d, 'd'))))
    return L


def medida_utilidades():
    L = list(G.VARS_PERIODO) + ['VAR _passo = ROUNDUP ( DIVIDE ( _tamanho, %d ), 0 )' % BALDES,
                                'VAR _nb = MAX ( INT ( DIVIDE ( _tamanho - 1, _passo ) ), 1 )']
    grupos, n = [], 0
    for g, (titulo, ligado, ks) in enumerate(P.GRUPOS):
        lado = 'left:0' if g < 2 else 'right:0'
        nomes = []
        for k in ks:
            n += 1
            L += html_cartao(P.IND[k], n, lado)
            nomes.append('_h%d' % n)
        grupos.append(M.grupo(titulo, ligado, F(' & '.join(nomes))))
    L.append('RETURN\n    ' + texto(M.utilidades(grupos)))
    return '\n'.join(L)


# ------------------------------------------------------------ faixa de situação
def medida_situacao():
    L = list(G.VARS_PERIODO)
    for n, ind in enumerate(IX.TODOS, start=1):
        L += vars_base(ind, n, False)
    N = len(IX.TODOS)
    L += ['VAR _nf = ' + soma(N, 'f'), 'VAR _na = ' + soma(N, 'a'), 'VAR _nd = ' + soma(N, 'd'),
          'VAR _ns = %s + %s' % (soma(N, 's'), soma(N, 'n'))]

    def um(forma, var, rotulo, cor):
        apag = forma == 's'
        zero = 'FALSE ()' if apag else '%s = 0' % var
        cn = cor if forma in 'af' else (SEC if apag else TEXTO)
        marca = F('IF ( %s, %s, %s )' % (zero, lit(M.marca_cont(forma, TRAC)), lit(M.marca_cont(forma, cor))))
        return M.contador(marca, {'n': F(var), 'cor_n': F('IF ( %s, "%s", "%s" )' % (zero, TRAC, cn)), 'rotulo': rotulo,
                                  'cor_r': F('IF ( %s, "%s", "%s" )' % (zero, SEC, SEC if apag else TEXTO)),
                                  'peso': '400' if apag else '600'})
    L.append('RETURN\n    ' + texto(M.situacao(N, um('f', '_nf', 'fora da meta', FORA) + um('a', '_na', 'em atenção', ATENCAO)
                                                + um('d', '_nd', 'dentro da meta', DENTRO) + um('s', '_ns', 'sem meta', SEC))))
    return '\n'.join(L)


def medida_dados():
    """O estado dos dados. Os VAR são os de gerar_op.medida_status(); espelha prep_v2.dados()."""
    base = G.medida_status().rsplit('RETURN', 1)[0].rstrip()
    assert '_nivel' in base and '_falta' in base and '_ha' in base
    col = lambda i: 'SWITCH ( _nivel, 1, "%s", 2, "%s", 3, "%s", "%s" )' % tuple(P.NIVEL[k][i] for k in (1, 2, 3, 0))
    data_hora = lambda v: 'IF ( ISBLANK ( %s ), %s, FORMAT ( %s, "dd/mm hh:nn" ) )' % (v, TRACO, v)
    data = lambda fmt: 'IF ( ISBLANK ( _dados ), %s, FORMAT ( _dados, "%s" ) )' % (TRACO, fmt)
    return base + '\nRETURN\n    ' + texto(M.dados({
        'fundo': F(col(1)), 'borda': F(col(2)), 'tinta': F(col(3)), 'titulo': F(col(0)),
        'ha': F('IF ( ISBLANK ( _dados ), %s, _ha )' % TRACO), 'ate': F(data('dd/mm')), 'dados': F(data('dd/mm/yyyy')),
        'plan': F(data_hora('_plan')), 'bi': F(data_hora('_bi')), 'falta': F('_falta')}))


def medida_periodo():
    base = G.medida_periodo().rsplit('RETURN', 1)[0].rstrip()
    assert '_rotulo' in base and '_nota' in base
    return base + '\nRETURN\n    ' + texto(M.periodo({
        'rotulo': F('_rotulo'), 'valor': F(G.faixa('_fim')), 'completo': F(G.faixa('_fim', 'dd/mm/yyyy')), 'nota': F('_nota')}))


# ------------------------------------------------------------------ medidas
COMO = ("Valor = as medidas '... Período' da tabela Medidas HTML (planilha Dados BI); meta = a de "
        'ferramentas/preview/indicadores_op.py. A linha fora da meta ou em atenção cresce no próprio lugar, com o '
        'desvio em palavras e a tendência do período; a ordem nunca muda. Ao passar o mouse, abre a aba com o período e a meta.')
MEDIDAS = []
for etapa, itens, estreito in P.COLUNAS:
    MEDIDAS.append({'chave': etapa, 'nome': 'HTML v2 ' + M.NOS[etapa][1],
                    'doc': 'Coluna %s da Visão Geral v2: o nó do trem e o bloco com %s. %s'
                           % (M.NOS[etapa][1], ', '.join(i['nome'] for i in itens), COMO),
                    'dax': medida_coluna(etapa, itens, estreito)})
MEDIDAS += [
    {'chave': 'clientes', 'nome': 'HTML v2 Clientes',
     'doc': 'Coluna Clientes da Visão Geral v2: a entrega aos clientes em destaque, com a meta, a tendência do '
            'período e a variação sobre o período anterior.',
     'dax': medida_clientes()},
    {'chave': 'utilidades', 'nome': 'HTML v2 Utilidades',
     'doc': 'Faixa de utilidades da Visão Geral v2: os consumos sob a etapa a que pertencem, o Blend e as Perdas. ' + COMO,
     'dax': medida_utilidades()},
    {'chave': 'situacao', 'nome': 'HTML v2 Situação',
     'doc': 'Faixa de situação da Visão Geral v2: quantos dos %d indicadores estão fora da meta, em atenção '
            '(até %d%% fora), dentro da meta e sem meta ou sem leitura.' % (len(IX.TODOS), IX.TOLERANCIA * 100),
     'dax': medida_situacao()},
    {'chave': 'dados', 'nome': 'HTML v2 Dados',
     'doc': 'Estado dos dados na Visão Geral v2: em dia (última leitura há até %d dia), pendentes (até %d dias) ou '
            'atrasados. Ao passar o mouse, mostra a data dos dados, quando a planilha foi salva, quando o Power BI '
            'foi atualizado e o que falta fazer.' % (IX.ATRASO_EM_DIA, IX.ATRASO_PENDENTE),
     'dax': medida_dados()},
    {'chave': 'periodo', 'nome': 'HTML v2 Período',
     'doc': 'Caixa do cabeçalho da Visão Geral v2 com as datas do período exibido. Ao passar o mouse, as datas com o ano.',
     'dax': medida_periodo()},
    {'chave': 'legenda', 'nome': 'HTML v2 Legenda',
     'doc': 'Legenda da Visão Geral v2: as marcas de situação, o destaque da linha, o medidor e a variação.',
     'dax': texto(M.legenda())},
]
NOME = {d['chave']: d['nome'] for d in MEDIDAS}


def tag(nome):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, 'aquapolo.v2.' + nome))


def tmdl():
    TAB = '\t'
    out = ["table '%s'" % TABELA, TAB + 'lineageTag: ' + tag('tabela'), '']
    for d in MEDIDAS:
        out.append(TAB + '/// ' + d['doc'])
        out.append(TAB + "measure '" + d['nome'] + "' = ```")
        for l in d['dax'].split('\n'):
            out.append((TAB * 3 + l) if l.strip() else '')
        out.append(TAB * 3 + '```')
        out.append(TAB * 2 + 'displayFolder: ' + PASTA)
        out.append(TAB * 2 + 'lineageTag: ' + tag(d['nome']))
        out.append('')
    out += [
        TAB + 'column Aux', TAB * 2 + 'dataType: string', TAB * 2 + 'isHidden', TAB * 2 + 'lineageTag: ' + tag('Aux'),
        TAB * 2 + 'summarizeBy: none', TAB * 2 + 'isNameInferred', TAB * 2 + 'sourceColumn: [Aux]', '',
        TAB * 2 + 'annotation SummarizationSetBy = Automatic', '',
        TAB + "partition '%s' = calculated" % TABELA, TAB * 2 + 'mode: import',
        TAB * 2 + 'source = ROW("Aux", BLANK())', '',
    ]
    return '\n'.join(out)


if __name__ == '__main__':
    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(tmdl())
    print('ESCRITO:', DESTINO.name, '|', len(MEDIDAS), 'medidas')
    for d in MEDIDAS:
        print('   %-22s %6d caracteres de DAX' % (d['nome'], len(d['dax'])))
