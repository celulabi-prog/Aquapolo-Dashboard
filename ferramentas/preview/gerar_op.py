# -*- coding: utf-8 -*-
"""Gera 'Medidas HTML.tmdl' a partir do MESMO molde usado no preview_op.

Saem dois grupos de medidas, todos lendo a tabela 'Dados BI' (a planilha):

  '<indicador> Período' e '<indicador> Período Anterior' — o número de cada
      indicador, já tratado: só dias até hoje, zero como "sem leitura", média
      simples, ponderada pelo volume de clientes ou mediana, e a unidade do
      painel. O tamanho do período vem do seletor Período (tabela 'Período Painel').
  'HTML Painel ...' e 'HTML Rodapé' — o HTML de cada visual da página. Cada
      painel vira UMA medida, que só busca os números acima e desenha.
  'HTML Status' — a caixa do cabeçalho que diz se os dados estão em dia.
  'HTML Período' — a caixa do cabeçalho com as datas do período exibido.
"""
import io, pathlib, uuid
import molde_op as M
import indicadores_op as IX
from estilo_op import *

REPO = pathlib.Path(__file__).resolve().parents[2]
DESTINO = REPO / 'Dashboard - Aquapolo.SemanticModel' / 'definition' / 'tables' / 'Medidas HTML.tmdl'

GRAD = {'CAB_AZUL': CAB_AZUL, 'CAB_TEAL': CAB_TEAL}
FMT = {0: '"#,##0"', 1: '"#,##0.0"', 2: '"#,##0.00"'}
FMT_MODELO = {0: '#,0', 1: '#,0.0', 2: '#,0.00'}
TRACO = '"&#8212;"'
PASTA = 'Painel Operacional'
T = "'Dados BI'"
PER = "'Período Painel'"
DAT = "'Datas Painel'"


def F(expr):
    """Um valor que, no DAX, vem de uma expressão."""
    return '" & ' + expr + ' & "'


def texto(html):
    """Fecha o HTML montado pelo molde como um literal DAX."""
    return '"' + html + '"'


def numero(v):
    return 'BLANK ()' if v is None else repr(round(float(v), 10))


def nuM(expr, dec):
    return 'IF ( ISBLANK ( %s ), %s, FORMAT ( %s, %s ) )' % (expr, TRACO, expr, FMT[dec])


# --------------------------------------------------- medidas dos indicadores
def nome_medida(ind, anterior=False):
    return ind['nome'] + (' Período Anterior' if anterior else ' Período')


def leituras(ind):
    """Os filtros que separam, na planilha, os dias que valem como leitura do indicador."""
    f = ['%s[Indicador] = "%s"' % (T, ind['coluna'])]
    if ind['conta'] == 'mediana':
        f.append('%s[Valor] > 0' % T)
    elif not ind['zero_vale']:
        f.append('%s[Valor] <> 0' % T)
    return f


# O começo de toda medida de período: o tamanho (_tamanho) e, com Datas exatas
# marcado (Dias = 0 na tabela Período Painel), o dia em que ele termina (_ate).
VARS_PERIODO = [
    'VAR _opcao = SELECTEDVALUE ( %s[Dias], %d )' % (PER, IX.JANELA),
    'VAR _exatas = ( _opcao = 0 )',
    'VAR _ate = MAX ( %s[Data] )' % DAT,
    'VAR _tamanho = IF ( _exatas, INT ( _ate - MIN ( %s[Data] ) ) + 1, _opcao )' % DAT,
]


def dax_fim(ind):
    """O dia em que termina o período do indicador: a última leitura dele ou, com
    Datas exatas, o fim do intervalo."""
    return ('IF ( _exatas, _ate, CALCULATE ( MAX ( %s[Data] ), %s, KEEPFILTERS ( %s[Data] <= TODAY () ) ) )'
            % (T, ', '.join(leituras(ind)), T))


def faixa(v, fmt='dd/mm', recuo=''):
    """As datas do período de _tamanho dias que termina em v. Com recuo ' - _tamanho',
    as do período anterior."""
    return ('IF ( ISBLANK ( {v} ), {t}, IF ( _tamanho = 1, FORMAT ( {v}{r}, "{f}" ), '
            'FORMAT ( {v}{r} - _tamanho + 1, "{f}" ) & " a " & FORMAT ( {v}{r}, "{f}" ) ) )'
            .format(v=v, r=recuo, t=TRACO, f=fmt))


def dax_indicador(ind, anterior=False):
    """O período que termina na última leitura do indicador — ou o período antes desse.
    Com Datas exatas, o período é o intervalo do controle de datas, igual para todos."""
    lei = leituras(ind)
    periodo = (['%s[Data] > _fim - 2 * _tamanho' % T, '%s[Data] <= _fim - _tamanho' % T] if anterior
               else ['%s[Data] > _fim - _tamanho' % T, '%s[Data] <= _fim' % T])

    def calculate(cabeca, filtros, recuo):
        e = ' ' * recuo
        return (cabeca + ' (\n' + ',\n'.join(e + '    ' + x for x in filtros) + '\n' + e + ')')

    L = VARS_PERIODO + [
        'VAR _ultima =',
        '    ' + calculate('CALCULATE', ['MAX ( %s[Data] )' % T] + lei
                           + ['KEEPFILTERS ( %s[Data] <= TODAY () )' % T], 4),
        'VAR _fim = IF ( _exatas, _ate, _ultima )']
    vezes = '' if ind['fator'] == 1.0 else ('%s * ' % numero(ind['fator']))
    if ind['conta'] == 'ponderada':
        L += ['VAR _dias =',
              '    ' + calculate('CALCULATETABLE', ['VALUES ( %s[Data] )' % T] + lei + periodo, 4),
              'VAR _t =',
              '    ADDCOLUMNS (',
              '        _dias,',
              '        "@v", CALCULATE ( AVERAGE ( %s[Valor] ), %s[Indicador] = "%s" ),' % (T, T, ind['coluna']),
              '        "@p", CALCULATE ( AVERAGE ( %s[Valor] ), %s[Indicador] = "%s" )' % (T, T, IX.PESO),
              '    )',
              'RETURN',
              '    %sDIVIDE ( SUMX ( _t, [@v] * [@p] ), SUMX ( _t, [@p] ) )' % vezes]
    else:
        conta = 'MEDIAN' if ind['conta'] == 'mediana' else 'AVERAGE'
        L += ['RETURN',
              '    ' + vezes + calculate('CALCULATE', ['%s ( %s[Valor] )' % (conta, T)] + lei + periodo, 4)]
    return '\n'.join(L)


def doc_indicador(ind, anterior=False):
    conta = {'media': 'média simples',
             'ponderada': 'média ponderada pelo volume de clientes do dia (soma do consumo dividida '
                          'pelo volume somado)',
             'mediana': 'mediana dos valores positivos (a planilha não traz o divisor, e um dia com '
                        'divisor perto de zero estouraria a média)'}[ind['conta']]
    quando = ('do período anterior ao de [%s], com o mesmo tamanho' % nome_medida(ind) if anterior
              else 'do período marcado no seletor Período (%d dias se nada estiver marcado), '
                   'contado até a última leitura do indicador; com Datas exatas, do intervalo '
                   'do controle de datas' % IX.JANELA)
    zero = ('Zero conta como leitura.' if ind['zero_vale'] else
            'Zero e datas futuras ficam de fora: na planilha, zero é célula vazia na origem.')
    vezes = '' if ind['fator'] == 1.0 else ' Sai multiplicado por %g (fração para %%).' % ind['fator']
    return ("%s: %s %s, coluna '%s' da planilha Dados BI. %s%s"
            % (ind['nome'], conta, quando, ind['coluna'], zero, vezes))


# ----------------------------------------------------------- medidas de HTML
def bloco_valores(ind, n, com_anterior):
    """Os VAR de um indicador: valor, referências, cor, largura da barra e, para a aba
    que abre ao passar o mouse, a situação e o dia em que termina o período."""
    L = ['VAR _v%d = [%s]' % (n, nome_medida(ind)),
         'VAR _mi%d = %s' % (n, numero(ind['meta_min'])),
         'VAR _ma%d = %s' % (n, numero(ind['meta_max']))]
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
    # A barra enche contra a meta ou, sem meta, contra a escala do indicador (IX.largura).
    base, cheia = (('_rf%d' % n, IX.ESCALA) if IX.referencia(ind) is not None
                   else (numero(ind['escala']), 1.0))
    L.append('VAR _lg{n} = MIN ( MAX ( DIVIDE ( _v{n}, {b} ), 0 ), {e} ) / {e} * 100'
             .format(n=n, b=base, e=cheia))
    L.append('VAR _si%d = SWITCH ( _co%d, "%s", "%s", "%s", "%s", "%s", "%s", "%s" )'
             % (n, n, VERDE, IX.SITUACAO[0], AMARELO, IX.SITUACAO[1], VERMELHO, IX.SITUACAO[2],
                IX.SITUACAO[3]))
    L.append('VAR _f%d = %s' % (n, dax_fim(ind)))
    if com_anterior:
        L.append('VAR _an%d = [%s]' % (n, nome_medida(ind, True)))
        L.append('VAR _te{n} = NOT ISBLANK ( _v{n} ) && NOT ISBLANK ( _an{n} ) && _an{n} <> 0'.format(n=n))
        L.append('VAR _dl%d = %s' % (n, ('DIVIDE ( _v{n} - _an{n}, _an{n} )' if ind['tipo_var'] == '%'
                                         else '_v{n} - _an{n}').format(n=n)))
    return L


def comum(ind, n, alt):
    """O que a linha e o cartão têm em comum. Espelha prep_op.comum()."""
    d = IX.textos(ind)
    d.update({
        'valor': F(nuM('_v%d' % n, ind['dec'])), 'cor': F('_co%d' % n), 'situacao': F('_si%d' % n),
        'barra': M.barra(F('FORMAT ( _lg%d, "0" )' % n), F('_co%d' % n), IX.marcadores(ind), alt),
        'pct': F('IF ( ISBLANK ( _rf{n} ) || ISBLANK ( _v{n} ), {t}, '
                 'FORMAT ( DIVIDE ( _v{n}, _rf{n} ), "0%" ) )'.format(n=n, t=TRACO)),
        'periodo': F(faixa('_f%d' % n))})
    return d


def html_linha(ind, n, total):
    return M.linha_ind(comum(ind, n, 24), n - 1, total)


def html_cartao(ind, n, total):
    pp = ind['tipo_var'] != '%'
    fvar = ('FORMAT ( _dl{n}, "+0.0%;-0.0%" )' if not pp
            else 'FORMAT ( _dl{n}, "+0.0;-0.0" ) & " p.p."').format(n=n)
    boa = ('_dl{n} < 0' if ind['tipo'] == 'menor' else '_dl{n} > 0').format(n=n)
    d = comum(ind, n, 20)
    d.update({
        'seta': F('IF ( _te{n}, IF ( _dl{n} >= 0, "&#9650;", "&#9660;" ), "" )'.format(n=n)),
        'var': F('IF ( _te%d, %s, %s )' % (n, fvar, TRACO)),
        'cor_var': F('IF ( NOT _te{n}, "{ci}", IF ( {boa}, "{vd}", "{vm}" ) )'
                     .format(n=n, boa=boa, ci=CINZA, vd=VERDE, vm=VERMELHO)),
        'ant': F(nuM('_an%d' % n, ind['dec'])),
        'ant_periodo': F(faixa('_f%d' % n, recuo=' - _tamanho'))})
    return M.cartao_ind(d, n - 1, total)


def medida_painel(p):
    cartoes = p['forma'] == 'cartoes'
    linhas, pedacos = list(VARS_PERIODO), []
    for n, ind in enumerate(p['itens'], start=1):
        linhas += bloco_valores(ind, n, cartoes)
        pedacos.append(texto((html_cartao if cartoes else html_linha)(ind, n, len(p['itens']))))
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
        'nome': p['medida'], 'pasta': PASTA,
        'doc': ("Painel %s da Visão Geral: %s. Valor = as medidas '... Período' de cada indicador "
                '(planilha Dados BI); meta = a de ferramentas/preview/indicadores_op.py. '
                'Verde dentro da meta, amarelo até %d%% fora, vermelho além disso. '
                'A barra enche até %d%% da meta e o tracejado marca os 100%% (na faixa, os dois limites). '
                'Ao passar o mouse num indicador, abre a aba com as datas do período exibido, a meta '
                'e, nos cartões, o período anterior com o valor dele.'
                % (p['titulo'], quais, IX.TOLERANCIA * 100, IX.ESCALA * 100)),
        'dax': medida_painel(p)})

MEDIDAS.append({
    'nome': 'HTML Rodapé', 'pasta': PASTA,
    'doc': 'Faixa do rodapé: o aviso da aba de explicação e a legenda das cores, da meta, da barra e da variação.',
    'dax': texto(M.rodape())})


def medida_status():
    """A caixa do cabeçalho: os dados estão em dia? Espelha dados_op.atualizacao()."""
    cor = {n: COR[c] for n, (_, c) in IX.NIVEIS.items()}
    pal = {n: p for n, (p, _) in IX.NIVEIS.items()}
    data_hora = lambda v: 'IF ( ISBLANK ( %s ), %s, FORMAT ( %s, "dd/mm hh:nn" ) )' % (v, TRACO, v)
    L = [
        '-- Agora no horário de Brasília (UTC-3), para valer igual no Desktop e no serviço.',
        'VAR _agora = UTCNOW () - 3 / 24',
        'VAR _hoje = INT ( _agora )',
        'VAR _dados = CALCULATE ( MAX ( %s[Data] ), %s[Valor] <> 0, %s[Data] <= TODAY () )' % (T, T, T),
        'VAR _plan = CALCULATE ( MAX ( %s[Planilha salva em] ), REMOVEFILTERS ( %s ) )' % (T, T),
        'VAR _bi = CALCULATE ( MAX ( %s[Carregado em] ), REMOVEFILTERS ( %s ) )' % (T, T),
        '-- Atraso = dias entre a última leitura e hoje. É ele que decide o status.',
        'VAR _atraso = _hoje - INT ( _dados )',
        'VAR _nivel = SWITCH ( TRUE (), ISBLANK ( _dados ), 0, _atraso <= %d, 1, _atraso <= %d, 2, 3 )'
        % (IX.ATRASO_EM_DIA, IX.ATRASO_PENDENTE),
        'VAR _cor = SWITCH ( _nivel, 1, "%s", 2, "%s", 3, "%s", "%s" )' % (cor[1], cor[2], cor[3], cor[0]),
        'VAR _palavra = SWITCH ( _nivel, 1, "%s", 2, "%s", 3, "%s", "%s" )' % (pal[1], pal[2], pal[3], pal[0]),
        'VAR _ha = SWITCH ( TRUE (), _atraso <= 0, "hoje", _atraso = 1, "ontem", "há " & _atraso & " dias" )',
        'VAR _rotulo = IF ( ISBLANK ( _dados ), "Sem leitura na planilha", '
        '"Dados até " & FORMAT ( _dados, "dd/mm" ) & " &#183; " & _ha )',
        '-- O que falta, na ordem em que dá para saber: o Power BI só enxerga a planilha quando é atualizado.',
        'VAR _falta = SWITCH ( TRUE (), _nivel = 1, "%s", ISBLANK ( _bi ) || INT ( _bi ) < _hoje, "%s", '
        'ISBLANK ( _plan ) || INT ( _plan ) < _hoje, "%s", "%s" )'
        % (IX.FALTA['nada'], IX.FALTA['bi'], IX.FALTA['planilha'], IX.FALTA['origem']),
        'RETURN\n    ' + texto(M.status({
            'cor': F('_cor'), 'palavra': F('_palavra'), 'rotulo': F('_rotulo'),
            'dados': F('IF ( ISBLANK ( _dados ), %s, FORMAT ( _dados, "dd/mm/yyyy" ) )' % TRACO),
            'plan': F(data_hora('_plan')), 'bi': F(data_hora('_bi')), 'falta': F('_falta')})),
    ]
    return '\n'.join(L)


MEDIDAS.append({
    'nome': 'HTML Status', 'pasta': PASTA,
    'doc': ('Caixa do cabeçalho com o status da atualização dos dados. Em dia = última leitura há até %d dia; '
            'Pendente = até %d dias; Atrasado = mais que isso. Ao passar o mouse, mostra a data dos dados, '
            'quando a planilha foi salva, quando o Power BI foi atualizado e o que falta fazer.'
            % (IX.ATRASO_EM_DIA, IX.ATRASO_PENDENTE)),
    'dax': medida_status()})

def medida_periodo():
    """A caixa do cabeçalho com as datas do período exibido. Espelha prep_op.periodo()."""
    L = VARS_PERIODO + [
        '-- Com um tamanho fixo, o período geral termina na última leitura da planilha (a data do rodapé).',
        'VAR _fim = IF ( _exatas, _ate, CALCULATE ( MAX ( %s[Data] ), %s[Valor] <> 0, %s[Data] <= TODAY () ) )' % (T, T, T),
        'VAR _rotulo = IF ( _exatas, "%s", "%s" ) & " &#183; " & _tamanho & IF ( _tamanho = 1, " dia", " dias" )'
        % (IX.ROTULO_PERIODO[True], IX.ROTULO_PERIODO[False]),
        'VAR _nota = IF ( _exatas, "%s", "%s" )' % (IX.NOTA_PERIODO[True], IX.NOTA_PERIODO[False])]
    L.append('RETURN\n    ' + texto(M.periodo({
        'rotulo': F('_rotulo'), 'valor': F(faixa('_fim')), 'completo': F(faixa('_fim', 'dd/mm/yyyy')),
        'nota': F('_nota')})))
    return '\n'.join(L)


MEDIDAS.append({
    'nome': 'HTML Período', 'pasta': PASTA,
    'doc': ('Caixa do cabeçalho com as datas do período exibido: o tamanho marcado no seletor Período, '
            'contado até a última leitura da planilha, ou o intervalo do controle de datas quando o seletor '
            'está em Datas exatas. Ao passar o mouse, mostra as datas com o ano. O período de cada indicador '
            'fica na aba dele, nos painéis.'),
    'dax': medida_periodo()})

for p in IX.PAINEIS:
    for ind in p['itens']:
        for anterior in ((False, True) if p['forma'] == 'cartoes' else (False,)):
            MEDIDAS.append({
                'nome': nome_medida(ind, anterior), 'pasta': PASTA + '\\Indicadores',
                'formato': FMT_MODELO[ind['dec']], 'doc': doc_indicador(ind, anterior),
                'dax': dax_indicador(ind, anterior)})

# ------------------------------------------------------------- escreve TMDL
TAB = '\t'
out = ["table 'Medidas HTML'", TAB + 'lineageTag: af935ac6-adea-4710-8879-f9f7682c9e9d', '']
for d in MEDIDAS:
    out.append(TAB + '/// ' + d['doc'])
    out.append(TAB + "measure '" + d['nome'] + "' = ```")
    for l in d['dax'].split('\n'):
        out.append((TAB * 3 + l) if l.strip() else '')
    out.append(TAB * 3 + '```')
    if d.get('formato'):
        out.append(TAB * 2 + 'formatString: ' + d['formato'])
    out.append(TAB * 2 + 'displayFolder: ' + d['pasta'])
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
        print('   %-30s %6d caracteres de DAX' % (d['nome'], len(d['dax'])))
