# -*- coding: utf-8 -*-
"""
Os 23 indicadores do Painel Operacional, em UMA lista só.

É daqui que saem tanto os números do preview quanto as medidas DAX. Mudou a
unidade, o ícone, a casa decimal, a meta ou o nome da coluna na planilha?
Muda aqui e roda de novo.

coluna: o título da coluna na linha 2 da planilha 'Dados BI.xlsx', letra por
        letra (com os erros de digitação de lá). Se alguém renomear a coluna
        na planilha, o indicador fica com '—' até o nome ser acertado aqui.
tipo:
  'menor' — quanto menor melhor; a referência é meta_max
  'maior' — quanto maior melhor; a referência é meta_min
  'faixa' — bom é ficar entre meta_min e meta_max
meta_min / meta_max: a referência, já na unidade que aparece no painel.
conta: como os valores diários viram o número dos 30 dias
  'media'     — média simples (leituras diretas)
  'ponderada' — média ponderada pelo volume de clientes do dia. É igual a
                somar o consumo e dividir pelo volume somado, que é a conta
                que a base antiga fazia
  'mediana'   — mediana dos valores positivos. Para as razões em que a planilha
                não traz o divisor: um dia com divisor perto de zero estoura a
                média (o Coagulante tem dias milhares de vezes acima do normal)
zero_vale: na planilha o PROCV devolve 0 quando a célula de origem está vazia,
           então 0 conta como "sem leitura". True só onde zero é leitura de verdade.
fator: multiplica o valor da planilha (fração -> %).
escala: para indicador SEM meta, o valor que enche a barra (o Blend é uma
        parcela de 0 a 100). Sem meta e sem escala, o indicador fica sem barra.
"""

TOLERANCIA = 0.10      # margem de "Atenção" em volta da referência
ESCALA = 1.6           # barra cheia = 160% da referência (traço da meta a 62,5%)
MARCADOR = 100.0 / ESCALA
JANELA = 30            # dias do período quando nada está marcado no seletor Período

# ---- período exibido (caixa do cabeçalho) ----------------------------------
# False = uma das opções de tamanho fixo; True = a opção Datas exatas.
ROTULO_PERIODO = {False: 'Período exibido', True: 'Datas escolhidas'}
NOTA_PERIODO = {False: 'Cada indicador vai até a sua última leitura.',
                True: 'Mesmo período para todos os indicadores.'}

# ---- indicador de atualização (caixa do cabeçalho) --------------------------
# O que decide o status é o atraso: dias entre a última leitura da planilha e hoje.
ATRASO_EM_DIA = 1      # até aqui, "Em dia" (a leitura de ontem é o normal)
ATRASO_PENDENTE = 3    # até aqui, "Pendente"; acima disso, "Atrasado"
NIVEIS = {0: ('Sem dados', 'cinza'), 1: ('Em dia', 'verde'),
          2: ('Pendente', 'amarelo'), 3: ('Atrasado', 'vermelho')}
# O que falta fazer, na ordem em que o painel consegue descobrir.
FALTA = {
    'nada': 'Nada pendente.',
    'bi': 'Falta atualizar o Power BI.',
    'planilha': 'Falta abrir e salvar a planilha no Excel e depois atualizar o Power BI.',
    'origem': 'Falta lançar os dados nas planilhas de origem.',
}

PESO = 'Clientes (L/s)'      # coluna que pondera as contas 'ponderada'

# ---- aba do indicador (abre ao passar o mouse) ------------------------------
# Na ordem de cor_de(): dentro, até TOLERANCIA fora, além disso, sem valor.
SITUACAO = ('Dentro da meta', 'Atenção', 'Fora da meta', 'Sem leitura')
SEM_META = 'Sem meta definida'


def I(**kw):
    kw.setdefault('fator', 1.0)
    kw.setdefault('dec_ref', kw['dec'])
    kw.setdefault('escala', None)
    kw.setdefault('tipo_var', '%')
    kw.setdefault('conta', 'media')
    kw.setdefault('zero_vale', False)
    kw.setdefault('meta_min', None)
    kw.setdefault('meta_max', None)
    return kw


# ---------------------------------------------------------------- linhas
EEBC = [
    # zero_vale: aqui há dias com zero retrolavagem de verdade. O preço é que um
    # dia ainda não preenchido na origem também entra como zero.
    I(k='retrolavagem', nome='Retrolavagens', unidade='ciclos', icone='retro',
      coluna='Nº retrolayagens disco ( ciclos/d)', tipo='menor', dec=0, meta_max=12,
      zero_vale=True),
    I(k='dqo', nome='DQO', unidade='mg/L', icone='frasco',
      coluna='DQO (mg/L)', tipo='menor', dec=0, meta_max=100),
    I(k='nh3', nome='NH3', unidade='mg/L', icone='molecula',
      coluna='NH3 (mg/L)', tipo='menor', dec=1, meta_max=20),
    I(k='condutividade', nome='Condutividade', unidade='µS/cm', icone='ondas',
      coluna='Condutividade', tipo='menor', dec=0, meta_max=650),
    I(k='dureza', nome='Dureza', unidade='mg/L', icone='diamante',
      coluna='Dureza (mg/L)', tipo='menor', dec=0, meta_max=100),
]

TMBR = [
    I(k='idade_lodo', nome='Idade do Lodo', unidade='dias', icone='lodo',
      coluna='Idade do lodo (dias)', tipo='faixa', dec=0, meta_min=18, meta_max=22),
    I(k='fm', nome='Alimento/Microorg.', unidade='g/g.d<sup>-1</sup>', icone='microorg',
      coluna='Alimento/ Microorg (g/g.d-¹)', tipo='faixa', dec=2, meta_min=0.08, meta_max=0.16),
    # Na planilha estes três já vêm resumidos entre os 8 trens: o pior do dia
    # (maior TMP, menor permeabilidade, maior turbidez).
    I(k='ptm', nome='TMP', unidade='bar', icone='manometro',
      coluna='Pressão transmembrana (Bar)', tipo='menor', dec=2, meta_max=0.6),
    I(k='permeabilidade', nome='Permeabilidade', unidade='LMH/bar', icone='colunas',
      coluna='Permeabilidade (LMH/bar)', tipo='maior', dec=0, meta_min=100),
    I(k='turbidez', nome='Turbidez', unidade='NTU', icone='turbidez',
      coluna='Turbidez (NTU)', tipo='menor', dec=2, meta_max=0.4),
    I(k='fluxo', nome='Fluxo', unidade='LMH', icone='ondas',
      coluna='Fluxo (LMH)', tipo='faixa', dec=1, dec_ref=0, meta_min=17, meta_max=24),
]

OR = [
    I(k='sdi', nome='SDI', unidade='', icone='sdi',
      coluna='SDI', tipo='menor', dec=1, meta_max=3),
    I(k='dp_skid_1', nome='dP Skid 1', unidade='bar', icone='manometro',
      coluna='dP Skid 1 (bar)', tipo='menor', dec=1, meta_max=3.5),
    I(k='dp_skid_2', nome='dP Skid 2', unidade='bar', icone='manometro',
      coluna='dP Skid-02 (bar)', tipo='menor', dec=1, meta_max=3.5),
    I(k='dp_skid_3', nome='dP Skid 3', unidade='bar', icone='manometro',
      coluna='dP Skid-03 (bar)', tipo='menor', dec=1, meta_max=3.5),
]

# ---------------------------------------------------------------- cartões
CONSUMO = [
    I(k='quimicos', nome='Químicos', unidade='kg/m³', icone='frasco',
      coluna='Químicos (Kg/m³)', tipo='menor', dec=2, meta_max=0.12, conta='ponderada'),
    I(k='energia', nome='Energia', unidade='kWh/m³', icone='raio',
      coluna='Energia (KWh/m³)', tipo='menor', dec=2, meta_max=0.98, conta='ponderada'),
    # Na planilha é a energia da OR por m³ entregue aos clientes. Na base antiga
    # era por m³ de permeado da OR, e a meta de 0,50 foi definida para aquela conta.
    I(k='energia_or', nome='Energia OR', unidade='kWh/m³', icone='engrenagem',
      coluna='Energia OR KW/m³', tipo='menor', dec=2, meta_max=0.50, conta='ponderada'),
    I(k='biologico', nome='Energia - Biológico', unidade='kWh/kg NH3 rem', icone='ventilador',
      coluna='Energia - Biológico (KWh/kg NH3 rem)', tipo='menor', dec=1, conta='mediana'),
    I(k='coagulante', nome='Coagulante', unidade='gPAC/gP rem', icone='molecula',
      coluna='Coagulante (gPAC/gP rem)', tipo='menor', dec=1, meta_max=17, conta='mediana'),
]

VOLUMES = [
    I(k='clientes', nome='Clientes', unidade='L/s', icone='tubos',
      coluna=PESO, tipo='maior', dec=1, meta_min=26950 / 86.4),      # 26.950 m³/d
    I(k='blend', nome='Blend', unidade='%', icone='frasco',
      coluna='Blend %', tipo='menor', dec=1, fator=100.0, tipo_var='p.p.',
      conta='ponderada', escala=100),
    I(k='perdas', nome='Perdas', unidade='%', icone='gota',
      coluna='Perdas %', tipo='menor', dec=1, fator=100.0, tipo_var='p.p.',
      meta_max=18, conta='ponderada'),
]

# ---------------------------------------------------------------- painéis
PAINEIS = [
    dict(k='eebc', medida='HTML Painel EEBC', titulo='QUALIDADE EEBC',
         sub='Qualidade da água de alimentação', icones=[('gota', '#5fb4f5')],
         grad='CAB_AZUL', itens=EEBC, forma='linhas'),
    dict(k='tmbr', medida='HTML Painel TMBR', titulo='PERFORMANCE TMBR',
         sub='Desempenho da etapa biológica', icones=[('engrenagem', '#7fc4ff')],
         grad='CAB_AZUL', itens=TMBR, forma='linhas'),
    dict(k='or', medida='HTML Painel OR', titulo='PERFORMANCE OR',
         sub='', icones=[('funil', '#4aa8f0')],
         grad='CAB_AZUL', itens=OR, forma='linhas'),
    dict(k='consumo', medida='HTML Painel Consumo', titulo='CONSUMO DE QUÍMICOS E ENERGIA',
         sub='Consumos específicos', icones=[('folha', '#3ddc84'), ('raio', '#4fe3dd')],
         grad='CAB_TEAL', itens=CONSUMO, forma='cartoes', sub_dir=False),
    dict(k='volumes', medida='HTML Painel Volumes', titulo='VOLUMES',
         sub='Distribuição e balanço hídrico', icones=[('gota', '#5fb4f5')],
         grad='CAB_AZUL', itens=VOLUMES, forma='cartoes'),
]

TODOS = EEBC + TMBR + OR + CONSUMO + VOLUMES


# ------------------------------------------------------- regras de cor/barra
def cor_de(v, rmin, rmax, tipo, verde, amarelo, vermelho, cinza):
    """Mesma regra do preview e do DAX, escrita uma vez."""
    if v is None:
        return cinza
    t = TOLERANCIA
    if tipo == 'faixa':
        if rmin is None or rmax is None:
            return cinza
        if rmin <= v <= rmax:
            return verde
        return amarelo if rmin * (1 - t) <= v <= rmax * (1 + t) else vermelho
    ref = rmax if tipo == 'menor' else rmin
    if ref is None:
        return cinza
    if tipo == 'menor':
        return verde if v <= ref else (amarelo if v <= ref * (1 + t) else vermelho)
    return verde if v >= ref else (amarelo if v >= ref * (1 - t) else vermelho)


def br(v, casas=0):
    """Número no formato pt-BR."""
    return '{:,.{}f}'.format(v, casas).replace(',', '§').replace('.', ',').replace('§', '.')


def referencia(ind):
    """A meta que a barra e a cor usam: o teto de 'menor' e de 'faixa', o piso de 'maior'."""
    return ind['meta_max'] if ind['tipo'] in ('menor', 'faixa') else ind['meta_min']


def meta_txt(ind):
    """A meta como aparece no painel: ≤ teto, ≥ piso ou a faixa. None = indicador sem meta."""
    ref = referencia(ind)
    if ref is None:
        return None
    if ind['tipo'] == 'faixa':
        return br(ind['meta_min'], ind['dec_ref']) + ' &#8211; ' + br(ref, ind['dec_ref'])
    return ('&#8804; ' if ind['tipo'] == 'menor' else '&#8805; ') + br(ref, ind['dec_ref'])


def textos(ind):
    """O que é igual no preview e no DAX: os textos que só dependem deste cadastro."""
    return {'icone': ind['icone'], 'nome': ind['nome'], 'unidade': ind['unidade'],
            'meta': meta_txt(ind),
            'obs': ('barra: 0 a %s%s' % (br(ind['escala']), ind['unidade'])) if ind['escala'] else ''}


def marcadores(ind):
    """Onde ficam os tracejados da barra, em % do trilho: um em cada limite da meta.
    [] = sem meta, mas com escala própria (barra sem tracejado); None = sem barra."""
    if referencia(ind) is None:
        return [] if ind['escala'] else None
    if ind['tipo'] == 'faixa':
        return [MARCADOR * ind['meta_min'] / ind['meta_max'], MARCADOR]
    return [MARCADOR]


def largura(v, ind):
    """Quanto da barra enche, em %: o valor sobre a meta (cheia em ESCALA vezes a meta)
    ou, para indicador sem meta, o valor sobre a escala dele."""
    base, cheia = referencia(ind), ESCALA
    if base is None:
        base, cheia = ind['escala'], 1.0
    if v is None or not base:
        return 0.0
    return max(0.0, min(v / base, cheia)) / cheia * 100
