# -*- coding: utf-8 -*-
"""
Os 23 indicadores do Painel Operacional, em UMA lista só.

É daqui que saem tanto os números do preview quanto as medidas DAX. Mudou a
unidade, o ícone, a casa decimal ou o ID na base? Muda aqui e roda de novo.

tipo:
  'menor' — quanto menor melhor; a referência é Target_Max
  'maior' — quanto maior melhor; a referência é Target_Min
  'faixa' — bom é ficar entre Target_Min e Target_Max
fator: multiplica o valor e a referência (fração -> %, m³/d -> L/s).
"""

TOLERANCIA = 0.10      # margem de "Atenção" em volta da referência
ESCALA = 1.6           # barra cheia = 160% da referência (traço da meta a 62,5%)
MARCADOR = 100.0 / ESCALA


def _trens(molde, n=8, sep=''):
    return [molde % (sep + str(i)) for i in range(1, n + 1)]


TMP = _trens("Membranas de Ultrafiltração | Pressão Transmembrana (TMP) - TM%s")
PERM = _trens("Membranas de Ultrafiltração | Permeablidade - TM %s")
TURB = _trens("Membranas de Ultrafiltração | Turbidez online - TM%s")


def I(**kw):
    kw.setdefault('fator', 1.0)
    kw.setdefault('dec_ref', kw['dec'])
    kw.setdefault('uni_ref', '')
    kw.setdefault('tipo_var', '%')
    return kw


# ---------------------------------------------------------------- linhas
EEBC = [
    I(k='retrolavagem', nome='Retrolavagens', unidade='ciclos', icone='retro',
      ids=["Filtro Disco | Número de Retrolavagens (AV)"], tipo='menor', dec=0),
    I(k='dqo', nome='DQO', unidade='mg/L', icone='frasco',
      ids=["Água Bruta | DQO"], tipo='menor', dec=0),
    I(k='nh3', nome='NH3', unidade='mg/L', icone='molecula',
      ids=["Água Bruta | Amônia"], tipo='menor', dec=1),
    I(k='condutividade', nome='Condutividade', unidade='µS/cm', icone='ondas',
      ids=["Água Bruta | Condutividade online"], tipo='menor', dec=0),
    I(k='dureza', nome='Dureza', unidade='mg/L', icone='diamante',
      ids=["Água Bruta | Dureza"], tipo='menor', dec=0),
]

TMBR = [
    I(k='idade_lodo', nome='Idade do Lodo', unidade='dias', icone='lodo',
      ids=["Reator Biológico | Idade do lodo (IL)"], tipo='faixa', dec=0),
    I(k='fm', nome='Alimento/Microorg.', unidade='g/g.d<sup>-1</sup>', icone='microorg',
      ids=["Reator Biológico | Alimento/ Microoganismo (F/M)"], tipo='faixa', dec=2),
    I(k='ptm', nome='TMP', unidade='bar', icone='manometro',
      ids=TMP, tipo='menor', dec=2),
    I(k='permeabilidade', nome='Permeabilidade', unidade='LMH/bar', icone='colunas',
      ids=PERM, tipo='maior', dec=0),
    I(k='turbidez', nome='Turbidez', unidade='NTU', icone='turbidez',
      ids=TURB, tipo='menor', dec=2),
    I(k='fluxo', nome='Fluxo', unidade='LMH', icone='ondas',
      ids=["Membranas de Ultrafiltração | Fluxo TM's"], tipo='faixa', dec=1),
]

OR = [
    I(k='sdi', nome='SDI', unidade='', icone='sdi',
      ids=["Osmose Reversa | SDI"], tipo='menor', dec=1),
    I(k='dp_skid_1', nome='dP Skid 1', unidade='bar', icone='manometro',
      ids=["Osmose Reversa | Diferencial de Pressão - Skid 1"], tipo='menor', dec=1),
    I(k='dp_skid_2', nome='dP Skid 2', unidade='bar', icone='manometro',
      ids=["Osmose Reversa | Diferencial de Pressão - Skid 2"], tipo='menor', dec=1),
    I(k='dp_skid_3', nome='dP Skid 3', unidade='bar', icone='manometro',
      ids=["Osmose Reversa | Diferencial de Pressão - Skid 3"], tipo='menor', dec=1),
]

# ---------------------------------------------------------------- cartões
CONSUMO = [
    I(k='quimicos', nome='Químicos', unidade='kg/m³', icone='frasco',
      ids=["Químicos | Consumo Unitário - Químicos"], tipo='menor', dec=2, uni_ref=' kg/m³'),
    I(k='energia', nome='Energia', unidade='kWh/m³', icone='raio',
      ids=["Energia | Consumo Unitário - Energia"], tipo='menor', dec=2, uni_ref=' kWh/m³'),
    I(k='energia_or', nome='Energia OR', unidade='kWh/m³', icone='engrenagem',
      ids=["Energia | Consumo OR"], tipo='menor', dec=2, uni_ref=' kWh/m³'),
    I(k='biologico', nome='Energia - Biológico', unidade='kWh/kg NH3 rem', icone='ventilador',
      ids=["Energia | Consumo SOP Biológico/ Amônia Removida"], tipo='menor', dec=1,
      uni_ref=' kWh/kg'),
    I(k='coagulante', nome='Coagulante', unidade='gPAC/gP rem', icone='molecula',
      ids=["Químicos | PAC/ P rem"], tipo='menor', dec=1, uni_ref=' gPAC/gP'),
]

VOLUMES = [
    I(k='clientes', nome='Clientes', unidade='L/s', icone='tubos',
      ids=["Volumes | Todos Clientes"], tipo='maior', dec=1, fator=1 / 86.4, uni_ref=' L/s'),
    I(k='blend', nome='Blend', unidade='%', icone='frasco', ids=[], tipo='menor', dec=1,
      uni_ref=' %', tipo_var='p.p.',
      aviso='A base ainda não traz o indicador de Blend.'),
    I(k='perdas', nome='Perdas', unidade='%', icone='gota',
      ids=["Perdas | Perda Total"], tipo='menor', dec=1, fator=100.0, uni_ref=' %',
      tipo_var='p.p.'),
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


def largura(v, ref):
    if v is None or ref in (None, 0):
        return 0.0
    return max(0.0, min(v / ref, ESCALA)) / ESCALA * 100
