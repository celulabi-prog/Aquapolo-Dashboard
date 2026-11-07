# -*- coding: utf-8 -*-
"""Gera 'Medidas Volumes.tmdl' a partir do MESMO molde usado no preview."""
import io, uuid
import molde
from estilo import *

# reaproveita as medidas de apoio e os utilitários já validados de g2.py
from apoio import MEDIDAS, LIMPA, vol


def m(nome, doc, dax, pasta='Página Volumes', fmt=None):
    MEDIDAS.append({'nome': nome, 'doc': doc, 'dax': dax.strip(), 'pasta': pasta, 'fmt': fmt})


def F(expr):
    """Um valor que, no DAX, vem de uma expressão."""
    return '" & ' + expr + ' & "'


def texto(html):
    """Fecha o HTML montado pelo molde como um literal DAX."""
    return '"' + html + '"'


def rotulo(mes):
    return ('CALCULATE ( MAX ( dCalendario[Mês/Ano] ), REMOVEFILTERS ( dCalendario ), '
            'dCalendario[MesIdx] = ' + mes + ' )')


SEMDADOS = ('"<style>html,body{margin:0;padding:0;height:100%}</style>'
            '<div style=\'' + molde.FONTE + CARD + ';align-items:center;justify-content:center;'
            'color:' + SEC + ';font-size:12px\'>Sem dados para o período selecionado</div>"')

FMT_N = 'FORMAT ( %s, "#,##0" )'
FMT_P = 'FORMAT ( %s, "+0.0%%;-0.0%%" )'
SETA = 'IF ( %s >= 0, "&#9650;", "&#9660;" )'
COR_V = 'IF ( NOT ( %s ), "' + CINZA + '", IF ( %s >= 0, "' + VERDE + '", "' + VERMELHO + '" ) )'
COR_META = ('SWITCH ( TRUE (), ISBLANK ( %s ), "' + CINZA + '", %s >= 1, "' + VERDE + '", '
            '%s >= 0.85, "' + AMARELO + '", "' + VERMELHO + '" )')

# ------------------------------------------------------------------ cabeçalho
m('HTML Vol Cabeçalho', 'Faixa do topo: identificação, legenda de cores e data da última medição da base.', """
VAR _ult = CALCULATE ( MAX ( fato_indicadores[Data] ), ALL ( fato_indicadores ), """ + LIMPA + """ )
VAR _html = """ + texto(molde.cabecalho({'ult': F('FORMAT ( _ult, "dd/mm/yyyy" )')})) + """
RETURN IF ( ISBLANK ( _ult ), """ + SEMDADOS + """, _html )
""")

# -------------------------------------------------------------- cartão cliente
m('HTML Vol Cartão Cliente', 'Moldura e rótulo do filtro de cliente. A lista suspensa é um visual de segmentação por cima.',
  texto(molde.card_cliente({})))

# --------------------------------------------------------------- cartão volume
m('HTML Vol Cartão Volume', 'Volume do mês de referência, vazão equivalente e variação contra o mês anterior.', """
VAR _m = [Vol Mês Idx]
VAR _vol = [Vol do Mês]
VAR _ant = [Vol Mês Anterior]
VAR _rot = """ + rotulo('_m') + """
VAR _rotAnt = """ + rotulo('_m - 1') + """
VAR _tem = NOT ISBLANK ( _ant ) && _ant <> 0
VAR _var = DIVIDE ( _vol - _ant, _ant )
VAR _corVar = """ + (COR_V % ('_tem', '_var')) + """
VAR _setaVar = IF ( _tem, """ + (SETA % '_var') + """, "" )
VAR _html = """ + texto(molde.card_volume({
    'rot': F('_rot'), 'rot_ant': F('_rotAnt'),
    'vol': F(FMT_N % '_vol'), 'ls': F(FMT_N % 'DIVIDE ( _vol, 86.4 )'),
    'ant': F('IF ( _tem, ' + (FMT_N % '_ant') + ', "&#8212;" )'),
    'var_mes': F('IF ( _tem, ' + (FMT_P % '_var') + ', "&#8212;" )'),
    'cor_var': F('_corVar'), 'seta_var': F('_setaVar')})) + """
RETURN IF ( ISBLANK ( _m ) || ISBLANK ( _vol ), """ + SEMDADOS + """, _html )
""")

# -------------------------------------------------------------- cartão situação
m('HTML Vol Cartão Situação', 'Compara o volume do mês com a faixa esperada: média dos 12 meses anteriores mais ou menos um desvio padrão.', """
VAR _m = [Vol Mês Idx]
VAR _vol = [Vol do Mês]
VAR _med = [Vol Média 12m]
VAR _dp = [Vol Desvio 12m]
VAR _tem = NOT ISBLANK ( _vol ) && NOT ISBLANK ( _med )
VAR _dist = ABS ( _vol - _med )
VAR _verde = _tem && _dist <= _dp
VAR _cor = SWITCH ( TRUE (), NOT _tem, \"""" + CINZA + """\", _verde, \"""" + VERDE + """\", _dist <= 2 * _dp, \"""" + AMARELO + """\", \"""" + VERMELHO + """\" )
VAR _txt = SWITCH ( TRUE (), NOT _tem, "Sem referência", _verde, "Consumo estável", _vol > _med, "Consumo acima do esperado", "Consumo abaixo do esperado" )
VAR _html = """ + texto(molde.card_situacao({
    'cor': F('_cor'), 'icone': F('IF ( _verde, "&#10003;", "&#33;" )'), 'texto': F('_txt'),
    'faixa_min': F(FMT_N % '_med - _dp'), 'faixa_max': F(FMT_N % '_med + _dp')})) + """
RETURN IF ( ISBLANK ( _m ), """ + SEMDADOS + """, _html )
""")
print('medidas até aqui:', len(MEDIDAS))

# ---------------------------------------------------------- resumo por cliente
LINHA_RESUMO = molde.linha_resumo({
    'nome': F('_nome'), 'vol': F(FMT_N % '_v'), 'cor': F('_cor'),
    'cor_nome': F('IF ( _todos, "' + BRANCO + '", "' + CLARO + '" )'),
    'peso': F('IF ( _todos, "700", "400" )'),
    'larg': F('FORMAT ( _larg, "0" )'),
    'pct': F('IF ( ISBLANK ( _at ), "&#8212;", FORMAT ( _at, "0%" ) )')})

m('HTML Vol Resumo Clientes', 'Volume do mês de referência e atingimento da meta de cada cliente. A barra é colorida pelo atingimento e traz um tracejado na marca de 100%.', """
VAR _m = [Vol Mês Idx]
VAR _rot = """ + rotulo('_m') + """
VAR _lista = FILTER ( ALL ( Clientes[ID_Indicador], Clientes[Cliente], Clientes[Meta], Clientes[Ordem] ), NOT ISBLANK ( Clientes[ID_Indicador] ) )
VAR _tab =
    ADDCOLUMNS ( _lista, "@Vol", VAR _i = Clientes[ID_Indicador] RETURN """ + vol('_m', '_i') + """ )
VAR _linhas =
    CONCATENATEX (
        _tab,
        VAR _nome = SUBSTITUTE ( SUBSTITUTE ( Clientes[Cliente], "&", "&amp;" ), "<", "&lt;" )
        VAR _v = [@Vol]
        VAR _at = DIVIDE ( _v, Clientes[Meta] )
        VAR _cor = """ + (COR_META % ('_at', '_at', '_at')) + """
        VAR _larg = MIN ( MAX ( DIVIDE ( _at, 1.3 ) * 100, 0 ), 100 )
        VAR _todos = Clientes[Cliente] = "Todos Clientes"
        RETURN """ + texto(LINHA_RESUMO) + """,
        "",
        Clientes[Ordem], ASC
    )
VAR _html = """ + texto(molde.resumo({'rot': F('_rot')}, F('_linhas'))) + """
RETURN IF ( ISBLANK ( _m ), """ + SEMDADOS + """, _html )
""")

# ------------------------------------------------------------ histórico mensal
LINHA_HIST = molde.linha_historico({
    'rot': F('[@Rot]'), 'vol': F(FMT_N % '_v'), 'ls': F(FMT_N % 'DIVIDE ( _v, 86.4 )'),
    'dias': F('FORMAT ( [@D] + 0, "0" )'), 'larg': F('FORMAT ( _larg, "0" )'),
    'fundo': F('IF ( _foco, "#16304f", "transparent" )'),
    'cor_rot': F('IF ( _foco, "' + BRANCO + '", "' + SEC + '" )'),
    'cor_dias': F('IF ( [@D] < 25, "' + AMARELO + '", "' + SEC + '" )'),
    'cor_var': F(COR_V % ('_tem', '_d')),
    'var': F('IF ( _tem, ' + (SETA % '_d') + ' & " " & ' + (FMT_P % '_d') + ', "&#8212;" )')})

m('HTML Vol Histórico', 'Os 13 meses até o mês de referência. A barra é escalada a partir de 94% do menor valor, não do zero, para as diferenças ficarem legíveis. Média, mínimo e máximo do rodapé só contam meses com 25 dias ou mais.', """
VAR _m = [Vol Mês Idx]
VAR _id = [Vol ID Cliente]
VAR _cli = UPPER ( SUBSTITUTE ( SUBSTITUTE ( [Vol Cliente], "&", "&amp;" ), "<", "&lt;" ) )
VAR _meses = FILTER ( ALL ( dCalendario[MesIdx] ), dCalendario[MesIdx] >= _m - 12 && dCalendario[MesIdx] <= _m )
VAR _hist =
    ADDCOLUMNS (
        _meses,
        "@Rot", VAR _k = dCalendario[MesIdx] RETURN """ + rotulo('_k') + """,
        "@V", VAR _k = dCalendario[MesIdx] RETURN """ + vol('_k', '_id') + """,
        "@A", VAR _k = dCalendario[MesIdx] - 1 RETURN """ + vol('_k', '_id') + """,
        "@D", VAR _k = dCalendario[MesIdx] RETURN """ + vol('_k', '_id', 'DISTINCTCOUNT ( fato_indicadores[Data] )') + """
    )
VAR _piso = MINX ( _hist, [@V] ) * 0.94
VAR _faixa = MAX ( MAXX ( _hist, [@V] ) - _piso, 0.0001 )
VAR _cheios = FILTER ( _hist, [@D] >= 25 )
VAR _media = AVERAGEX ( _cheios, [@V] )
VAR _min = MINX ( _cheios, [@V] )
VAR _max = MAXX ( _cheios, [@V] )
VAR _mMin = MAXX ( TOPN ( 1, FILTER ( _cheios, [@V] = _min ), dCalendario[MesIdx], DESC ), [@Rot] )
VAR _mMax = MAXX ( TOPN ( 1, FILTER ( _cheios, [@V] = _max ), dCalendario[MesIdx], DESC ), [@Rot] )
VAR _linhas =
    CONCATENATEX (
        _hist,
        VAR _v = [@V]
        VAR _tem = NOT ISBLANK ( [@A] ) && [@A] <> 0 && NOT ISBLANK ( _v )
        VAR _d = DIVIDE ( _v - [@A], [@A] )
        VAR _larg = 55 + DIVIDE ( _v - _piso, _faixa ) * 45
        VAR _foco = dCalendario[MesIdx] = _m
        RETURN """ + texto(LINHA_HIST) + """,
        "",
        dCalendario[MesIdx], DESC
    )
VAR _html = """ + texto(molde.historico({
    'cliente': F('_cli'), 'media13': F(FMT_N % '_media'),
    'media13_ls': F(FMT_N % 'DIVIDE ( _media, 86.4 )'),
    'min13': F(FMT_N % '_min'), 'min13_mes': F('_mMin'),
    'max13': F(FMT_N % '_max'), 'max13_mes': F('_mMax')}, F('_linhas'))) + """
RETURN IF ( ISBLANK ( _m ), """ + SEMDADOS + """, _html )
""")
print('medidas até aqui:', len(MEDIDAS))

# ----------------------------------------------------------------- diagnóstico
def _ld(rotulo_, valor, lado='', sub=None, cor=None, unidade=True):
    d = {'rotulo': rotulo_, 'valor': valor, 'lado': lado, 'unidade': unidade}
    if sub: d['sub'] = sub
    if cor: d['cor'] = cor
    return molde.linha_diagnostico(d)


LINHAS_DIAG = (
    _ld('Meta contratual', F(FMT_N % '_meta'), F(FMT_N % 'DIVIDE ( _meta, 86.4 )') + ' L/s')
    + _ld('Média 12 meses anteriores', F(FMT_N % '_med'), F(FMT_N % 'DIVIDE ( _med, 86.4 )') + ' L/s')
    + _ld('Desvio vs. média 12 meses',
          F('IF ( _temRef, ' + (SETA % '_dMed') + ' & " " & ' + (FMT_P % '_dMed') + ', "&#8212;" )'),
          cor=F(COR_V % ('_temRef', '_dMed')), unidade=False)
    + _ld('Desvio vs. mesmo mês do ano anterior',
          F('IF ( _temAno, ' + (SETA % '_dAno') + ' & " " & ' + (FMT_P % '_dAno') + ', "&#8212;" )'),
          sub=F('_rotAno'), cor=F(COR_V % ('_temAno', '_dAno')), unidade=False)
    + _ld('Pico histórico', F(FMT_N % '_pico'), F(FMT_N % 'DIVIDE ( _pico, 86.4 )') + ' L/s', sub=F('_mPico'))
    + _ld('Menor consumo histórico', F(FMT_N % '_vale'), F(FMT_N % 'DIVIDE ( _vale, 86.4 )') + ' L/s', sub=F('_mVale')))

m('HTML Vol Diagnóstico', 'Meta, média de referência, desvios e extremos históricos do cliente em foco. Pico e menor consumo só consideram meses com 25 dias ou mais.', """
VAR _m = [Vol Mês Idx]
VAR _id = [Vol ID Cliente]
VAR _cli = UPPER ( SUBSTITUTE ( SUBSTITUTE ( [Vol Cliente], "&", "&amp;" ), "<", "&lt;" ) )
VAR _vol = [Vol do Mês]
VAR _meta = [Vol Meta]
VAR _med = [Vol Média 12m]
VAR _dp = [Vol Desvio 12m]
VAR _ano = [Vol Mesmo Mês Ano Anterior]
VAR _rotAno = """ + rotulo('_m - 12') + """
VAR _temRef = NOT ISBLANK ( _med ) && NOT ISBLANK ( _vol )
VAR _temAno = NOT ISBLANK ( _ano ) && _ano <> 0
VAR _dMed = DIVIDE ( _vol - _med, _med )
VAR _dAno = DIVIDE ( _vol - _ano, _ano )
VAR _dentro = _temRef && ABS ( _vol - _med ) <= _dp
VAR _todos =
    FILTER (
        ADDCOLUMNS (
            ALL ( dCalendario[MesIdx] ),
            "@Rot", VAR _k = dCalendario[MesIdx] RETURN """ + rotulo('_k') + """,
            "@V", VAR _k = dCalendario[MesIdx] RETURN """ + vol('_k', '_id') + """,
            "@D", VAR _k = dCalendario[MesIdx] RETURN """ + vol('_k', '_id', 'DISTINCTCOUNT ( fato_indicadores[Data] )') + """
        ),
        [@D] >= 25
    )
VAR _pico = MAXX ( _todos, [@V] )
VAR _vale = MINX ( _todos, [@V] )
VAR _mPico = MAXX ( TOPN ( 1, FILTER ( _todos, [@V] = _pico ), dCalendario[MesIdx], DESC ), [@Rot] )
VAR _mVale = MAXX ( TOPN ( 1, FILTER ( _todos, [@V] = _vale ), dCalendario[MesIdx], DESC ), [@Rot] )
VAR _linhas = """ + texto(LINHAS_DIAG) + """
VAR _html = """ + texto(molde.diagnostico({
    'cliente': F('_cli'), 'cor_desvio': F(COR_V % ('_temRef', '_dMed')),
    'desvio_txt': F('IF ( _temRef, FORMAT ( ABS ( _dMed ), "0.0%" ) & IF ( _dMed >= 0, " acima", " abaixo" ), "sem referência" )'),
    'cor_faixa': F('IF ( _dentro, "' + VERDE + '", "' + AMARELO + '" )'),
    'faixa_txt': F('IF ( _dentro, "dentro", "fora" )')}, F('_linhas'))) + """
RETURN IF ( ISBLANK ( _m ), """ + SEMDADOS + """, _html )
""")

# ------------------------------------------- variação vs. mesmo mês ano ant.
BARRA = molde.barra_variacao({
    'x': F('FORMAT ( _cx - _bw / 2, "0" )'), 'y': F('FORMAT ( _y, "0" )'),
    'w': F('FORMAT ( _bw, "0" )'), 'h': F('FORMAT ( _h, "0" )'),
    'cx': F('FORMAT ( _cx, "0" )'), 'yr': F('FORMAT ( _yr, "0" )'),
    'cor': F('_cor'), 'pct': F(FMT_P % '_vv'), 'nome': F('_nome')})

m('HTML Vol Variação Ano', 'Variação de cada cliente contra o mesmo mês do ano anterior, em ordem decrescente. Verde sobe, vermelho cai. Em percentual, e não em volume, senão os clientes pequenos somem ao lado do Q3 ABC.', """
VAR _m = [Vol Mês Idx]
VAR _rot = """ + rotulo('_m') + """
VAR _rotAno = """ + rotulo('_m - 12') + """
VAR _lista = FILTER ( ALL ( Clientes[ID_Indicador], Clientes[Cliente] ), Clientes[Cliente] <> "Todos Clientes" && NOT ISBLANK ( Clientes[ID_Indicador] ) )
VAR _base =
    ADDCOLUMNS (
        _lista,
        "@At", VAR _i = Clientes[ID_Indicador] RETURN """ + vol('_m', '_i') + """,
        "@An", VAR _i = Clientes[ID_Indicador] RETURN """ + vol('_m - 12', '_i') + """
    )
VAR _tab = ADDCOLUMNS ( FILTER ( _base, NOT ISBLANK ( [@At] ) && NOT ISBLANK ( [@An] ) && [@An] <> 0 ), "@Var", DIVIDE ( [@At] - [@An], [@An] ) )
VAR _n = COUNTROWS ( _tab )
VAR _maxP = MAX ( MAXX ( _tab, [@Var] ), 0 )
VAR _maxN = MAX ( - MINX ( _tab, [@Var] ), 0 )
VAR _tot = MAX ( _maxP + _maxN, 0.01 )
VAR _y0 = """ + str(molde.TOPO_R) + """ + """ + str(molde.ALTO_PLOT) + """ * DIVIDE ( _maxP, _tot )
VAR _gw = DIVIDE ( """ + str(molde.LARG_SVG - 16) + """, _n )
VAR _bw = MIN ( _gw * 0.46, 80 )
VAR _barras =
    CONCATENATEX (
        _tab,
        VAR _vv = [@Var]
        VAR _pos = COUNTROWS ( FILTER ( _tab, [@Var] > _vv ) ) + 1
        VAR _cx = 8 + ( _pos - 0.5 ) * _gw
        VAR _h = MAX ( ABS ( _vv ) / _tot * """ + str(molde.ALTO_PLOT) + """, 1 )
        VAR _sobe = _vv >= 0
        VAR _y = IF ( _sobe, _y0 - _h, _y0 )
        VAR _yr = IF ( _sobe, _y0 - _h - 9, _y0 + _h + 17 )
        VAR _cor = IF ( _sobe, \"""" + VERDE + """\", \"""" + VERMELHO + """\" )
        VAR _nome = SUBSTITUTE ( SUBSTITUTE ( Clientes[Cliente], "&", "&amp;" ), "<", "&lt;" )
        RETURN """ + texto(BARRA) + """,
        "",
        [@Var], DESC
    )
VAR _html = """ + texto(molde.variacao({
    'contexto': F('_rot & " vs. " & _rotAno & " &#183; todos os clientes, ordenado"'),
    'y0': F('FORMAT ( _y0, "0" )')}, F('_barras'))) + """
RETURN IF ( ISBLANK ( _m ) || _n = 0, """ + SEMDADOS + """, _html )
""")
print('medidas totais:', len(MEDIDAS))

# --------------------------------------------------------------- escreve TMDL
TAB = '\t'
out = ["table 'Medidas Volumes'", TAB + 'lineageTag: 2d58c591-b413-4b63-948a-6661d2370c83', '']
for d in MEDIDAS:
    corpo = d['dax']
    out.append(TAB + '/// ' + d['doc'])
    if '\n' in corpo:
        out.append(TAB + "measure '" + d['nome'] + "' = ```")
        for l in corpo.split('\n'):
            out.append((TAB * 3 + l) if l.strip() else '')
        out.append(TAB * 3 + '```')
    else:
        out.append(TAB + "measure '" + d['nome'] + "' = " + corpo)
    if d['fmt']:
        out.append(TAB * 2 + 'formatString: ' + d['fmt'])
    out.append(TAB * 2 + 'displayFolder: ' + d['pasta'])
    out.append(TAB * 2 + 'lineageTag: ' + str(uuid.uuid5(uuid.NAMESPACE_DNS, 'aquapolo.vol.' + d['nome'])))
    out.append('')
out += [
    TAB + 'column Aux', TAB * 2 + 'dataType: string', TAB * 2 + 'isHidden',
    TAB * 2 + 'lineageTag: 83f4ec86-7ab9-4661-9ae3-d24350d1afa6',
    TAB * 2 + 'summarizeBy: none', TAB * 2 + 'isNameInferred', TAB * 2 + 'sourceColumn: [Aux]', '',
    TAB * 2 + 'annotation SummarizationSetBy = Automatic', '',
    TAB + "partition 'Medidas Volumes' = calculated", TAB * 2 + 'mode: import',
    TAB * 2 + 'source = ROW("Aux", BLANK())', '',
    TAB + 'annotation PBI_Id = MedidasVolumes', '',
]
destino = (r'C:\Users\Iza\Documents\dashboard aquapolo claude'
           r'\Dashboard - Aquapolo.SemanticModel\definition\tables\Medidas Volumes.tmdl')
io.open(destino, 'w', encoding='utf-8').write('\n'.join(out))
print('ESCRITO:', len(MEDIDAS), 'medidas,', len(out), 'linhas')
