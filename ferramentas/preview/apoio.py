# -*- coding: utf-8 -*-
"""Medidas de apoio: mês em foco, cliente, volumes, média e desvio de referência."""
import uuid

LOCAL = "'LocalDateTable_26878ded-8d73-4b03-b037-00303befc16a'"
# Bloco repetido: tira todo filtro que possa atingir fato_indicadores por outro caminho.
LIMPA = ("REMOVEFILTERS ( dim_indicadores ), REMOVEFILTERS ( Clientes ),\n"
         "        REMOVEFILTERS ( dCalendario ), REMOVEFILTERS ( " + LOCAL + " )")

MEDIDAS = []
RESET_TXT_DAX = ('"<style>html,body{margin:0;padding:0;height:100%;overflow:hidden}'
                 '*{box-sizing:border-box}</style>" &')


def m(nome, doc, dax, pasta='Base', fmt=None):
    corpo = dax.strip()
    if pasta != 'Base':
        # o iframe do visual traz margem padrao de 8px no body; sem zerar,
        # todo cartao de altura 100% estoura o retangulo e corta embaixo
        marca = 'VAR _html ='
        if marca in corpo:
            corpo = corpo.replace(marca, marca + ' ' + RESET_TXT_DAX, 1)
        else:
            corpo = RESET_TXT_DAX + ' ' + corpo
    MEDIDAS.append({'nome': nome, 'doc': doc, 'dax': corpo, 'pasta': pasta, 'fmt': fmt})


def vol(mes, ident, agg='[Valor Indicador]'):
    """CALCULATE de volume para um mes e um indicador."""
    return ("CALCULATE (\n"
            "        %s,\n"
            "        %s,\n"
            "        dCalendario[MesIdx] = %s,\n"
            "        fato_indicadores[ID_Indicador] = %s\n"
            "    )" % (agg, LIMPA, mes, ident))


# ---------------------------------------------------------------- apoio
m('Vol Mês Idx', 'Mês em foco. Sem filtro de período, usa o último mês COMPLETO da base (um mês pela metade distorceria a comparação com a meta e com os meses cheios).', """
VAR _escolhido = ISFILTERED ( dCalendario[Ano] ) || ISFILTERED ( dCalendario[Mês] ) || ISFILTERED ( dCalendario[Mês/Ano] ) || ISFILTERED ( dCalendario[Data] )
VAR _sel = MAX ( dCalendario[MesIdx] )
VAR _ult = CALCULATE ( MAX ( fato_indicadores[Data] ), ALL ( fato_indicadores ), %s )
VAR _idx = YEAR ( _ult ) * 12 + MONTH ( _ult )
VAR _fechado = _ult = EOMONTH ( _ult, 0 )
RETURN
    IF ( _escolhido, _sel, IF ( _fechado, _idx, _idx - 1 ) )
""" % LIMPA, fmt='0')

m('Vol ID Cliente', 'ID_Indicador do cliente escolhido. Sem escolha — ou com mais de um escolhido — usa Todos Clientes.', """
VAR _qtd = COUNTROWS ( VALUES ( Clientes[ID_Indicador] ) )
RETURN
    IF ( _qtd = 1, SELECTEDVALUE ( Clientes[ID_Indicador] ), "Volumes | Todos Clientes" )
""")

m('Vol Cliente', 'Nome do cliente escolhido.', """
VAR _qtd = COUNTROWS ( VALUES ( Clientes[Cliente] ) )
RETURN
    IF ( _qtd = 1, SELECTEDVALUE ( Clientes[Cliente] ), "Todos Clientes" )
""")

m('Vol do Mês', 'Volume médio diário (m³/d) do cliente no mês em foco.',
  "VAR _id = [Vol ID Cliente]\nVAR _i = [Vol Mês Idx]\nRETURN\n    " + vol('_i', '_id'), fmt='#,0')

m('Vol Mês Anterior', 'Volume médio diário (m³/d) no mês anterior ao mês em foco.',
  "VAR _id = [Vol ID Cliente]\nVAR _i = [Vol Mês Idx] - 1\nRETURN\n    " + vol('_i', '_id'), fmt='#,0')

m('Vol Mesmo Mês Ano Anterior', 'Volume médio diário (m³/d) no mesmo mês do ano anterior.',
  "VAR _id = [Vol ID Cliente]\nVAR _i = [Vol Mês Idx] - 12\nRETURN\n    " + vol('_i', '_id'), fmt='#,0')

m('Vol Dias do Mês', 'Dias com medição do cliente no mês em foco.',
  "VAR _id = [Vol ID Cliente]\nVAR _i = [Vol Mês Idx]\nRETURN\n    " + vol('_i', '_id', 'DISTINCTCOUNT ( fato_indicadores[Data] )'), fmt='0')

m('Vol Meta', 'Meta contratual (m³/d) do cliente, vinda de Target_Min na dim_indicadores.', """
VAR _id = [Vol ID Cliente]
RETURN
    CALCULATE ( MAX ( Clientes[Meta] ), REMOVEFILTERS ( Clientes ), Clientes[ID_Indicador] = _id )
""", fmt='#,0')

JANELA12 = "FILTER ( ALL ( dCalendario[MesIdx] ), dCalendario[MesIdx] >= _m - 12 && dCalendario[MesIdx] < _m )"
SERIE12 = ("VAR _id = [Vol ID Cliente]\n"
           "VAR _m = [Vol Mês Idx]\n"
           "VAR _meses = " + JANELA12 + "\n"
           "RETURN\n"
           "    %s (\n"
           "        _meses,\n"
           "        VAR _k = dCalendario[MesIdx]\n"
           "        RETURN\n"
           "            " + vol('_k', '_id').replace('\n', '\n        ') + "\n"
           "    )")

m('Vol Média 12m', 'Média dos volumes mensais dos 12 meses ANTERIORES ao mês em foco. Serve de referência; não inclui o próprio mês avaliado.',
  SERIE12 % 'AVERAGEX', fmt='#,0')

m('Vol Desvio 12m', 'Desvio padrão dos 12 meses anteriores. A faixa esperada é a média ± 1 desvio.',
  SERIE12 % 'STDEVX.P', fmt='#,0')

m('Vol Última Data', 'Última data com medição do cliente dentro do mês em foco.',
  "VAR _id = [Vol ID Cliente]\nVAR _i = [Vol Mês Idx]\nRETURN\n    " + vol('_i', '_id', 'MAX ( fato_indicadores[Data] )'), fmt='Short Date')

for dias in (7, 30):
    m('Vol Média %dd' % dias, 'Volume médio dos últimos %d dias com medição, até a última data do mês em foco.' % dias, """
VAR _id = [Vol ID Cliente]
VAR _fim = [Vol Última Data]
RETURN
    CALCULATE (
        [Valor Indicador],
        %s,
        fato_indicadores[Data] > _fim - %d,
        fato_indicadores[Data] <= _fim,
        fato_indicadores[ID_Indicador] = _id
    )
""" % (LIMPA, dias), fmt='#,0')

print('medidas de apoio:', len(MEDIDAS))

