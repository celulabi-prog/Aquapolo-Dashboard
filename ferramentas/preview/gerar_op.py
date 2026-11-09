# -*- coding: utf-8 -*-
"""Gera 'Medidas HTML.tmdl' a partir do MESMO molde usado no preview_op.

Cada painel da página vira UMA medida: o DAX monta as linhas (ou os cartões)
um atrás do outro e devolve o HTML inteiro. Antes eram 23 medidas, uma por
indicador; agora são 5 painéis + o rodapé, que é o que a página tem de visual.
"""
import io, pathlib, uuid
import molde_op as M
import indicadores_op as IX
from estilo_op import *

DESTINO = (pathlib.Path(r'C:\Users\Iza\Documents\dashboard aquapolo claude')
           / 'Dashboard - Aquapolo.SemanticModel' / 'definition' / 'tables' / 'Medidas HTML.tmdl')

GRAD = {'CAB_AZUL': CAB_AZUL, 'CAB_TEAL': CAB_TEAL}
FMT = {0: '"#,##0"', 1: '"#,##0.0"', 2: '"#,##0.00"'}
TRACO = '"&#8212;"'


def F(expr):
    """Um valor que, no DAX, vem de uma expressão."""
    return '" & ' + expr + ' & "'


def texto(html):
    """Fecha o HTML montado pelo molde como um literal DAX."""
    return '"' + html + '"'


def lista(ids):
    return '{ ' + ', '.join('"' + i + '"' for i in ids) + ' }'


def nuM(expr, dec):
    return 'IF ( ISBLANK ( %s ), %s, FORMAT ( %s, %s ) )' % (expr, TRACO, expr, FMT[dec])


def calc(medida, ids_var, tabela, fator):
    d = ('CALCULATE ( %s, REMOVEFILTERS ( dim_indicadores ), TREATAS ( %s, %s ) )'
         % (medida, ids_var, tabela))
    return d if fator == 1.0 else ('%s * %s' % (repr(round(fator, 10)), d))


def bloco_valores(ind, n, com_anterior):
    """Os VAR de um indicador: valor, referências, cor e largura da barra."""
    iv, fa = '_ids%d' % n, ind['fator']
    L = ['VAR %s = %s' % (iv, lista(ind['ids'])),
         'VAR _v%d = %s' % (n, calc('[Valor 30d]', iv, 'fato_indicadores[ID_Indicador]', fa)),
         'VAR _mi%d = %s' % (n, calc('MAX ( dim_indicadores[Target_Min] )', iv,
                                     'dim_indicadores[ID_Indicador]', fa)),
         'VAR _ma%d = %s' % (n, calc('MAX ( dim_indicadores[Target_Max] )', iv,
                                     'dim_indicadores[ID_Indicador]', fa))]
    L.append('VAR _rf%d = %s' % (n, '_ma%d' % n if ind['tipo'] in ('menor', 'faixa') else '_mi%d' % n))
    sem = 'ISBLANK ( _v{n} )'.format(n=n)
    if ind['tipo'] == 'faixa':
        cor = ('SWITCH ( TRUE (), {sem} || ISBLANK ( _mi{n} ) || ISBLANK ( _ma{n} ), "{ci}", '
               '_v{n} >= _mi{n} && _v{n} <= _ma{n}, "{vd}", '
               '_v{n} >= _mi{n} * {lo} && _v{n} <= _ma{n} * {hi}, "{am}", "{vm}" )')
    elif ind['tipo'] == 'menor':
        cor = ('SWITCH ( TRUE (), {sem} || ISBLANK ( _rf{n} ), "{ci}", '
               '_v{n} <= _rf{n}, "{vd}", _v{n} <= _rf{n} * {hi}, "{am}", "{vm}" )')
    else:
        cor = ('SWITCH ( TRUE (), {sem} || ISBLANK ( _rf{n} ), "{ci}", '
               '_v{n} >= _rf{n}, "{vd}", _v{n} >= _rf{n} * {lo}, "{am}", "{vm}" )')
    L.append('VAR _co%d = %s' % (n, cor.format(
        n=n, sem=sem, ci=CINZA, vd=VERDE, am=AMARELO, vm=VERMELHO,
        lo=1 - IX.TOLERANCIA, hi=1 + IX.TOLERANCIA)))
    L.append('VAR _lg{n} = MIN ( MAX ( DIVIDE ( _v{n}, _rf{n} ), 0 ), {e} ) / {e} * 100'
             .format(n=n, e=IX.ESCALA))
    if com_anterior:
        L.append('VAR _an%d = %s' % (n, calc('[Valor 30d Anterior]', iv,
                                             'fato_indicadores[ID_Indicador]', fa)))
        L.append('VAR _te{n} = NOT ISBLANK ( _v{n} ) && NOT ISBLANK ( _an{n} ) && _an{n} <> 0'.format(n=n))
        L.append('VAR _dl%d = %s' % (n, ('DIVIDE ( _v{n} - _an{n}, _an{n} )' if ind['tipo_var'] == '%'
                                         else '_v{n} - _an{n}').format(n=n)))
    return L


def html_linha(ind, n):
    if ind['tipo'] == 'faixa':
        rot = '"Faixa"'
        val = ('IF ( ISBLANK ( _mi{n} ) || ISBLANK ( _ma{n} ), {t}, FORMAT ( _mi{n}, {f} ) '
               '& " &#8211; " & FORMAT ( _ma{n}, {f} ) )').format(n=n, t=TRACO, f=FMT[ind['dec_ref']])
    else:
        rot, val = '"Ref."', nuM('_rf%d' % n, ind['dec_ref'])
    return M.linha_ind({
        'icone': ind['icone'], 'nome': ind['nome'], 'unidade': ind['unidade'],
        'valor': F(nuM('_v%d' % n, ind['dec'])), 'cor': F('_co%d' % n),
        'larg': F('FORMAT ( _lg%d, "0" )' % n), 'marcador': '%.1f' % IX.MARCADOR,
        'rot_ref': F(rot), 'ref': F(val)})


def html_cartao(ind, n):
    if not ind['ids']:
        return M.cartao_vazio({'icone': ind['icone'], 'nome': ind['nome'],
                               'unidade': ind['unidade'], 'aviso': ind.get('aviso', '')})
    pp = ind['tipo_var'] != '%'
    fvar = ('FORMAT ( _dl{n}, "+0.0%;-0.0%" )' if not pp
            else 'FORMAT ( _dl{n}, "+0.0;-0.0" ) & " p.p."').format(n=n)
    boa = ('_dl{n} < 0' if ind['tipo'] == 'menor' else '_dl{n} > 0').format(n=n)
    return M.cartao_ind({
        'icone': ind['icone'], 'nome': ind['nome'], 'unidade': ind['unidade'],
        'valor': F(nuM('_v%d' % n, ind['dec'])), 'cor': F('_co%d' % n),
        'larg': F('FORMAT ( _lg%d, "0" )' % n), 'marcador': '%.1f' % IX.MARCADOR,
        'seta': F('IF ( _te{n}, IF ( _dl{n} >= 0, "&#9650;", "&#9660;" ), "" )'.format(n=n)),
        'var': F('IF ( _te%d, %s, %s )' % (n, fvar, TRACO)),
        'cor_var': F('IF ( NOT _te{n}, "{ci}", IF ( {boa}, "{vd}", "{vm}" ) )'
                     .format(n=n, boa=boa, ci=CINZA, vd=VERDE, vm=VERMELHO)),
        'ref': F('IF ( ISBLANK ( _rf%d ), "Ref. &#8212;", "Ref. " & FORMAT ( _rf%d, %s ) & "%s" )'
                 % (n, n, FMT[ind['dec_ref']], ind['uni_ref'])),
        'pct': F('IF ( ISBLANK ( _rf{n} ) || ISBLANK ( _v{n} ), {t}, '
                 'FORMAT ( DIVIDE ( _v{n}, _rf{n} ), "0%" ) )'.format(n=n, t=TRACO))})


def medida_painel(p):
    cartoes = p['forma'] == 'cartoes'
    linhas, pedacos = [], []
    for n, ind in enumerate(p['itens'], start=1):
        if ind['ids']:
            linhas += bloco_valores(ind, n, cartoes)
        pedacos.append(texto(html_cartao(ind, n) if cartoes else html_linha(ind, n)))
    corpo = M.painel_cartoes if cartoes else M.painel_linhas
    d = {'titulo': p['titulo'], 'sub': p['sub'], 'icones': p['icones'],
         'grad': GRAD[p['grad']], 'sub_dir': p.get('sub_dir', True)}
    linhas.append('VAR _itens =\n    ' + '\n        & '.join(pedacos))
    linhas.append('RETURN\n    ' + texto(corpo(d, F('_itens'))))
    return '\n'.join(linhas)


# ------------------------------------------------------------------ medidas
MEDIDAS = []
for p in IX.PAINEIS:
    quais = ', '.join(i['nome'] for i in p['itens'])
    MEDIDAS.append({
        'nome': p['medida'],
        'doc': ('Painel %s da Visão Geral: %s. Valor = média dos últimos 30 dias com dado '
                '([Valor 30d]); referência = Target_Min/Target_Max da dim_indicadores. '
                'Verde dentro da meta, amarelo até %d%% fora, vermelho além disso. '
                'A barra enche até %d%% da referência e o tracejado marca os 100%%.'
                % (p['titulo'], quais, IX.TOLERANCIA * 100, IX.ESCALA * 100)),
        'dax': medida_painel(p)})

MEDIDAS.append({
    'nome': 'HTML Rodapé',
    'doc': 'Faixa do rodapé: data da última medição da base e a legenda das cores e dos termos.',
    'dax': ('VAR _ult = CALCULATE ( MAX ( fato_indicadores[Data] ), ALL ( fato_indicadores ) )\n'
            'RETURN\n    '
            + texto(M.rodape({'ult': F('IF ( ISBLANK ( _ult ), "&#8212;", '
                                       'FORMAT ( _ult, "dd/mm/yyyy" ) )')})))})

# ------------------------------------------------------------- escreve TMDL
TAB = '\t'
out = ["table 'Medidas HTML'", TAB + 'lineageTag: af935ac6-adea-4710-8879-f9f7682c9e9d', '']
for d in MEDIDAS:
    out.append(TAB + '/// ' + d['doc'])
    out.append(TAB + "measure '" + d['nome'] + "' = ```")
    for l in d['dax'].split('\n'):
        out.append((TAB * 3 + l) if l.strip() else '')
    out.append(TAB * 3 + '```')
    out.append(TAB * 2 + 'displayFolder: Painel Operacional')
    out.append(TAB * 2 + 'lineageTag: ' + str(uuid.uuid5(uuid.NAMESPACE_DNS, 'aquapolo.op.' + d['nome'])))
    out.append('')
out += [
    TAB + 'column Aux', TAB * 2 + 'dataType: string', TAB * 2 + 'isHidden',
    TAB * 2 + 'lineageTag: 674cf386-1713-4851-b817-217b7cf73e83',
    TAB * 2 + 'summarizeBy: none', TAB * 2 + 'isNameInferred', TAB * 2 + 'sourceColumn: [Aux]', '',
    TAB * 2 + 'annotation SummarizationSetBy = Automatic', '',
    TAB + "partition 'Medidas HTML' = calculated", TAB * 2 + 'mode: import',
    TAB * 2 + 'source = ROW("Aux", BLANK())', '',
]

if __name__ == '__main__':
    io.open(DESTINO, 'w', encoding='utf-8').write('\n'.join(out))
    print('ESCRITO:', DESTINO.name, '|', len(MEDIDAS), 'medidas,', len(out), 'linhas')
    for d in MEDIDAS:
        print('   %-24s %6d caracteres de DAX' % (d['nome'], len(d['dax'])))
