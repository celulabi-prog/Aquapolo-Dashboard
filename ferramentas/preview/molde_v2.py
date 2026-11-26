# -*- coding: utf-8 -*-
"""
Molde ÚNICO do HTML da página Visão Geral v2.

Como no molde_op: toda função recebe TEXTO pronto e devolve HTML, sem conta nenhuma.
  - preview .......: os textos são valores reais já formatados (prep_v2)
  - gerador de DAX : os textos são pedaços de DAX (gerar_v2)

A diferença para o molde_op é que aqui a FORMA depende do dado (a linha fora da
meta é maior que a linha dentro). Por isso as funções recebem a forma como
argumento: o preview chama uma vez, com a forma real; o gerador chama uma vez
por forma e deixa o DAX escolher com SWITCH.

Os moldes abaixo estão escritos com aspas duplas, para ler melhor, e passam por
q(), que troca por aspas simples: no DAX o HTML vira literal de string, e uma
aspa dupla quebraria a medida. Os lugares que recebem texto são marcados §assim§.
"""
import re
import indicadores_op as IX
from molde_op import RESET, ICONE
from estilo_v2 import *


def q(molde):
    return molde.replace('"', "'").replace('\n', '')


def sub(molde, **t):
    """Põe cada texto no seu lugar. Passada única: o texto que entra não é relido."""
    return re.sub(u'§(\\w+)§', lambda m: str(t[m.group(1)]), molde)


DICA_CSS = ("<style>.dc{display:none}.ind{cursor:help}"
            ".ind:hover{box-shadow:inset 0 0 0 1px #2f79ad}.ind:hover>.dc{display:block}</style>")
RAIZ = "<div style='" + FONTE + "height:100vh;width:100%;overflow:hidden;"


def r1(v):
    """Coordenada com uma casa e ponto decimal, igual ao FORMAT ( x, "0.0", "en-US" ) do DAX."""
    return '%.1f' % v


# ------------------------------------------------------------------- medidor
# kind: max = meta "<=" | min = meta ">=" | faixa. A zona da meta e os limites são
# geometria fixa; só o ponteiro (x), o triângulo (xt) e o trecho entre a meta e o
# ponteiro (a, w) vêm do dado. Trilho de x=4 a x=156, esticado quando W > 160.
ZONAS = {'max': (4, 99), 'min': (99, 156), 'faixa': (57.2, 102.8)}
LIMS = {'max': [99], 'min': [99], 'faixa': [57.2, 102.8]}
ANEL = q('<span style="width:14px;height:14px;flex:none;border-radius:50%;border:2px solid #a8bfd6"></span>'
         '<span style="font-size:16px;color:#a8bfd6">§txt§</span>')


def escala(W):
    return lambda v: 4 + (v - 4) * (W - 8) / 152.0


def medidor(kind, forma, t, W=160):
    """forma: 's' sem meta/sem leitura (t: txt) | 'd' dentro (t: x, xt) | 'a' atenção e
    'f' fora (t: x, xt, a, w) | 'dir' e 'esq' além da escala (t: cor, corte)."""
    if forma == 's':
        return sub(q('<div style="width:%dpx;height:32px;flex:none;display:flex;align-items:center;gap:8px">' % W)
                   + ANEL + '</div>', **t)
    X = escala(W)
    z0, z1 = ZONAS[kind]
    lims = LIMS[kind]
    zona = lambda y, h: '<rect x="%s" y="%d" width="%s" height="%d" fill="%s"/>' % (r1(X(z0)), y, r1(X(z1) - X(z0)), h, ZONA)
    abre = lambda h: ('<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block;flex:none;overflow:visible">'
                      % (W, h, W, h))
    tic = lambda d: '<path d="%s" stroke="#f3f8fd" stroke-width="1.5"/>' % ''.join('M%s %s' % (r1(X(l)), d) for l in lims)
    if forma == 'd':
        m = (abre(32) + '<rect x="4" y="16" width="%d" height="6" fill="%s"/>' % (W - 8, TRILHO) + zona(16, 6) + tic('12v14')
             + '<path d="M§xt§ 3h10l-5 8z" fill="#f3f8fd"/><path d="M§x§ 10v16" stroke="#f3f8fd" stroke-width="2.5"/></svg>')
    elif forma == 'dir':
        L = X(lims[-1])
        m = (abre(32) + '<rect x="4" y="13" width="%s" height="10" fill="%s"/>' % (r1(X(144) - 4), TRILHO) + zona(13, 10)
             + '<rect x="%s" y="10" width="%s" height="16" fill="§cor§"/>' % (r1(L), r1(X(145) - L))
             + '<path d="M%s 29l5-22M%s 29l5-22" stroke="§corte§" stroke-width="3.5"/>' % (r1(L + 14), r1(L + 23))
             + tic('8v20') + '<path d="M%s 4l14 14-14 14z" fill="§cor§"/></svg>' % r1(X(144)))
    elif forma == 'esq':
        L = X(lims[0])
        m = (abre(32) + '<rect x="16" y="13" width="%s" height="10" fill="%s"/>' % (r1(X(156) - 16), TRILHO) + zona(13, 10)
             + '<rect x="15" y="10" width="%s" height="16" fill="§cor§"/>' % r1(L - 15)
             + '<path d="M%s 29l-5-22M%s 29l-5-22" stroke="§corte§" stroke-width="3.5"/>' % (r1(L - 14), r1(L - 23))
             + tic('8v20') + '<path d="M16 4l-14 14 14 14z" fill="§cor§"/></svg>')
    elif forma == 'a':
        m = (abre(26) + '<rect x="4" y="11" width="%d" height="8" fill="%s"/>' % (W - 8, TRILHO) + zona(11, 8)
             + '<rect x="§a§" y="11" width="§w§" height="8" fill="%s"/>' % ATENCAO + tic('7v16')
             + '<path d="M§xt§ 0h12l-6 9z" fill="%s"/><path d="M§x§ 7v16" stroke="%s" stroke-width="3"/></svg>' % (ATENCAO, ATENCAO))
    else:
        m = (abre(32) + '<rect x="4" y="13" width="%d" height="10" fill="%s"/>' % (W - 8, TRILHO) + zona(13, 10)
             + '<rect x="§a§" y="13" width="§w§" height="10" fill="%s"/>' % FORA + tic('8v20')
             + '<path d="M§xt§ 0h14l-7 11z" fill="%s"/><path d="M§x§ 9v19" stroke="%s" stroke-width="3.5"/></svg>' % (FORA, FORA))
    return sub(q(m), **t)


def medidor_escala(t, W=160):
    """Indicador sem meta, mas com escala própria (o Blend, de 0 a 100%): barra azul. t: x, xt, w."""
    return sub(q('<svg width="%d" height="32" viewBox="0 0 %d 32" style="display:block;flex:none">' % (W, W)
                 + '<rect x="4" y="16" width="%d" height="6" fill="%s"/>' % (W - 8, TRILHO)
                 + '<rect x="4" y="16" width="§w§" height="6" fill="%s"/>' % AZUL
                 + '<path d="M4 12v14M%s 13v12M%d 12v14" stroke="#6f93b5" stroke-width="1.5"/>' % (r1(W / 2.0), W - 4)
                 + '<path d="M§xt§ 3h10l-5 8z" fill="#f3f8fd"/><path d="M§x§ 10v16" stroke="#f3f8fd" stroke-width="2.5"/></svg>'), **t)


# --------------------------------------------------------------- minigráfico
# A série do período com a zona da meta ao fundo. geo = (largura, altura, margem x,
# margem y): a mesma conta serve à linha (esticável), ao cartão e à entrega.
GEO_LINHA, GEO_CARTAO, GEO_HEROI = (160, 60, 4, 4), (64, 26, 3, 3), (308, 160, 6, 10)


def mini(sit, t, geo=GEO_LINHA):
    """t: zy, zh (zona da meta), lim (os tracejados), pts, x0, xn, yl (o limite rompido)."""
    W, H = geo[0], geo[1]
    if geo == GEO_LINHA:
        abre = ('<svg viewBox="0 0 160 60" preserveAspectRatio="none" style="display:block;flex:1 1 0;'
                'min-height:0;max-height:56px;width:160px">')
        traco, risco, ve = '5 4', '2.5', ' vector-effect="non-scaling-stroke"'
    else:
        abre = '<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block;flex:none">' % (W, H, W, H)
        traco, risco, ve = '4 3', '2', ''
    return sub(q(abre + '<rect x="0" y="§zy§" width="%d" height="§zh§" fill="rgba(87,214,141,0.20)"/>' % W
                 + '<polygon points="§x0§,§yl§ §pts§ §xn§,§yl§" fill="rgba(%s,0.28)"/>' % RGB[sit]
                 + '<path d="§lim§" stroke="%s" stroke-width="1.5" stroke-dasharray="%s"%s/>' % (DENTRO, traco, ve)
                 + '<polyline points="§pts§" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" '
                   'stroke-linecap="round"%s/></svg>' % (COR[sit], risco, ve)), **t)


def mini_heroi(t):
    """A série da entrega, com área até a base. t: pts, x0, xn, xf, yf (último ponto), ym (meta), cor."""
    return sub(q('<svg viewBox="0 0 308 160" preserveAspectRatio="none" style="display:block;flex:1 1 0;min-height:0;'
                 'width:308px;margin-top:10px"><defs><linearGradient id="v2-area" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#3aa7f2" stop-opacity="0.50"/><stop offset="1" stop-color="#3aa7f2" '
                 'stop-opacity="0.08"/></linearGradient></defs>'
                 '<polygon points="§x0§,160 §pts§ §xn§,160" fill="url(#v2-area)"/>'
                 '<path d="M0 §ym§H308" stroke="#57d68d" stroke-width="1.5" stroke-dasharray="7 6" '
                 'vector-effect="non-scaling-stroke"/>'
                 '<polyline points="§pts§" fill="none" stroke="§cor§" stroke-width="3" stroke-linejoin="round" '
                 'stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
                 '<path d="M§xn§ §yf§h0.01" stroke="#f3f8fd" stroke-width="11" stroke-linecap="round" '
                 'vector-effect="non-scaling-stroke"/></svg>'), **t)


# ------------------------------------------------------- aba do indicador
def _celula(rotulo, valor, abaixo=''):
    """Uma informação da aba: rótulo pequeno, o dado em destaque e, embaixo, um complemento."""
    return ("<div><div style='font-size:16px;color:" + SEC + "'>" + rotulo + "</div>"
            "<div style='font-size:25px;font-weight:700;color:" + TEXTO + "'>" + valor + "</div>"
            + ("<div style='font-size:21px;font-weight:600;color:" + CLARO + "'>" + abaixo + "</div>"
               if abaixo else '') + "</div>")


def dica(D, onde, em_coluna=False):
    """A aba que abre ao passar o mouse: com o que o número é comparado. Pouco texto,
    letra grande. `onde` é a posição dentro do visual (a aba não sai do retângulo dele).
    D: nome, unidade, meta (None = sem meta), cor, situacao, periodo, pct e, quando
    há período anterior, valor, ant e ant_periodo. Não recebe o mouse."""
    if 'ant' in D:
        celulas = (_celula('Período exibido', D['periodo'], D['valor'])
                   + _celula('Período anterior', D['ant_periodo'], D['ant']))
    else:
        celulas = _celula('Período exibido', D['periodo'])
    celulas += (_celula('Meta', D['meta'], D['pct'] + ' da meta') if D['meta']
                else _celula('Meta', 'sem meta'))
    return ("<div class='dc' style='position:absolute;" + onde + ";z-index:9;pointer-events:none;"
            "padding:11px 18px 13px 18px;background:#04182a;border:1px solid " + BOTAO_B
            + ";border-radius:6px;box-shadow:0 8px 22px rgba(0,0,0,0.6);font-weight:400;"
            "line-height:1.3;text-align:left;white-space:nowrap'>"
            + "<div style='display:flex;align-items:baseline;gap:9px'>"
            + "<b style='font-size:22px;color:" + TEXTO + "'>" + D['nome'] + "</b>"
            + "<span style='font-size:18px;color:" + SEC + "'>" + D['unidade'] + "</span>"
            + ("<b style='margin-left:auto;padding-left:28px;font-size:20px;color:" + D['cor'] + "'>"
               + D['situacao'] + "</b>" if D['meta'] else '') + "</div>"
            + "<div style='display:flex;" + ('flex-direction:column;gap:8px' if em_coluna else 'gap:36px')
            + ";margin-top:7px'>" + celulas + "</div></div>")


# ------------------------------------------------------- linha de indicador
COMUM = ('position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto 160px;column-gap:14px;'
         'align-items:center;padding:0 14px 0 12px;border-top:1px solid ' + DIV + ';')
TXT = 'display:flex;flex-direction:column;align-items:flex-start;white-space:nowrap'
ETIQUETA = 'margin:0 -6px;padding:0 6px;background:' + FORA + ';border-radius:2px;color:#1c0508'
UM = '<div style="font-size:16px;line-height:20px;color:#a8bfd6">§um§</div>'


def estilo_frase(sit, extremo):
    """Desvio extremo e fora da meta: a frase vira etiqueta cheia."""
    return ETIQUETA if (extremo and sit == 'f') else 'color:' + COR[sit]


def linha(d, sit, estreito):
    """sit: 'd' (dentro, sem meta ou sem leitura), 'a' ou 'f'. d: nome, um, valor,
    medidor, dica e, em destaque, mini (pode vir vazio), q e ref (a frase do desvio)
    e frase_css. `estreito`: os blocos EEBC e OR, em que o nome fica em cima."""
    if sit == 'd':
        return sub(q('<div class="ind" style="flex:1 1 0;min-height:50px;' + COMUM + 'border-left:6px solid transparent">'
                     '<div style="white-space:nowrap"><div style="font-size:19px;font-weight:600;line-height:24px">§nome§</div>'
                     + UM + '</div><div style="font-size:34px;font-weight:700;line-height:38px;text-align:right">§valor§</div>'
                     '§medidor§§dica§</div>'), **d)
    f = sit == 'f'
    c = COR[sit]
    col3 = ('<div style="%salign-self:stretch;min-height:0;display:flex;flex-direction:column;justify-content:center;'
            'gap:%dpx;padding:5px 0">§mini§§medidor§</div>' % ('grid-row:1 / 3;grid-column:3;' if estreito else '', 4 if f else 3))
    fundo = 'border-left:6px solid %s;background:rgba(%s,%s)' % (c, RGB[sit], TINTA[sit])
    if not estreito:      # bloco largo (TMBR): texto e valor lado a lado, frase em uma linha
        val = 'font-size:%dpx;font-weight:700;line-height:%dpx;%stext-align:right;color:%s' % (
            ((56, 60, 'letter-spacing:-1px;') if f else (44, 48, '')) + (c,))
        return sub(q('<div class="ind" style="flex:%s 1 0;min-height:%dpx;%s%s">' % ('2' if f else '1.5', 72 if f else 70, COMUM, fundo)
                     + '<div style="%s"><div style="font-size:%dpx;font-weight:700;line-height:%dpx">§nome§</div>' % (
                         TXT, 22 if f else 20, 26 if f else 24)
                     + UM + '<div style="font-size:%dpx;font-weight:700;line-height:%dpx;§frase_css§">§q§ §ref§</div></div>' % (
                         (20, 24) if f else (17, 20))
                     + '<div style="%s">§valor§</div>' % val + col3 + '§dica§</div>'), **d)
    val = 'font-size:%dpx;font-weight:700;line-height:%dpx;%stext-align:right;color:%s' % (
        ((52, 56, 'letter-spacing:-1px;') if f else (44, 48, '')) + (c,))
    return sub(q('<div class="ind" style="flex:%s 1 0;min-height:%dpx;%sgrid-template-rows:auto auto;align-content:center;%s">' % (
                     '2' if f else '1.5', 88 if f else 86, COMUM, fundo)
                 + '<div style="grid-row:1;grid-column:1 / 3;font-size:%dpx;font-weight:700;line-height:24px;white-space:nowrap">'
                   '§nome§</div>' % (22 if f else 20)
                 + col3 + '<div style="grid-row:2;grid-column:1;%s">' % TXT + UM
                 + '<div style="font-size:%dpx;font-weight:700;line-height:%dpx;§frase_css§"><div>§q§</div><div>§ref§</div></div></div>' % (
                     (18, 20) if f else (16, 18))
                 + '<div style="grid-row:2;grid-column:2;%s">§valor§</div>§dica§</div>' % val), **d)


# ------------------------------------------------------------ bloco de etapa
def ver_ok(n, total):
    return sub(q('<div style="display:flex;align-items:baseline;gap:10px;white-space:nowrap;line-height:36px">'
                 '<span style="font-size:28px;font-weight:700">§n§ de §total§</span>'
                 '<span style="font-size:24px;color:#d3e1ef">dentro da meta</span></div>'), n=n, total=total)


def ver_fora(n):
    return sub(q('<span style="font-size:28px;font-weight:700;color:%s">§n§ fora da meta</span>' % FORA), n=n)


def ver_atencao(n, so):
    """so: não há indicador fora na etapa, e a atenção ganha o tamanho principal."""
    return sub(q('<span style="font-size:%dpx;font-weight:700;color:%s">§n§ em atenção</span>' % (28 if so else 24, ATENCAO)), n=n)


def ver_alerta(conteudo):
    return q('<div style="display:flex;align-items:baseline;gap:14px;white-space:nowrap;line-height:36px">') + conteudo + '</div>'


SEG = {'d': ('6px', ZONA), 'a': ('10px', ATENCAO), 'f': ('14px', FORA), 's': ('6px', TRAC)}


def segmento(sit):
    return q('<span style="flex:1;height:%s;background:%s"></span>' % SEG[sit])


def bloco(t):
    """t: borda, fundo (do cabeçalho), veredito, fita, linhas."""
    return sub(q('<div style="flex:1;min-height:0;display:flex;flex-direction:column;background:%s;border:2px solid §borda§;'
                 'border-radius:3px">' % PAINEL
                 + '<div style="height:78px;flex:none;display:flex;flex-direction:column;justify-content:space-between;'
                   'padding:8px 14px 12px;background:§fundo§">§veredito§'
                   '<div style="height:14px;display:flex;align-items:flex-end;gap:4px">§fita§</div></div>'
                   '<div style="flex:1;min-height:0;display:flex;flex-direction:column">§linhas§</div></div>'), **t)


# ------------------------------------------------------------- nó do trem
NOS = {
    'eebc': ('gota', 'EEBC', 'Alimentação'),
    'tmbr': ('colunas', 'TMBR', 'Biológico e membranas'),
    'or': ('funil', 'OR', 'Osmose reversa'),
    'clientes': ('tubos', 'CLIENTES', 'Entrega'),
}
TUBO = '<div style="flex:1;height:6px;background:%s"></div>' % AZUL
SETA_T = ('<svg width="14" height="20" viewBox="0 0 14 20" style="flex:none"><path d="M0 0l14 10-14 10z" fill="%s"/></svg>' % AZUL)


def _caixa_no(k, estica=False):
    ic, sigla, nome = NOS[k]
    return ('<div style="height:52px;flex:%s;display:flex;align-items:center;gap:12px;padding:0 18px 0 12px;'
            'border:2px solid §cor§;border-radius:3px;background:§fundo§;white-space:nowrap">' % ('1' if estica else 'none')
            + '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="§cor§" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round" style="flex:none">' + ICONE[ic].replace("'", '"') + '</svg>'
            + '<span style="font-size:26px;font-weight:700;letter-spacing:1px">%s</span>' % sigla
            + '<span style="font-size:17px;color:#a8bfd6">%s</span></div>' % nome)


def no(k, t):
    """A célula do trem em cima da coluna: tubo, seta, a caixa da etapa e a ligação até
    o bloco. t: cor e fundo (da caixa), lig (da ligação) e, na OR, blend."""
    lig = ('<div style="height:14px;flex:none;display:flex;justify-content:center">'
           '<div style="width:2px;background:§lig§"></div></div>')
    vao = '<div style="height:22px;flex:none"></div>'
    if k == 'or':         # o desvio: a parcela que não passa pela osmose, com o Blend em cima
        m = ('<div style="position:relative;height:88px;flex:none;display:flex;flex-direction:column">'
             '<div style="position:absolute;left:22px;right:22px;top:7px;height:44px;border:4px solid %s;border-bottom:0;'
             'border-radius:8px 8px 0 0"></div>' % AZUL
             + '<div style="position:absolute;left:50%;top:0;transform:translateX(-50%);height:20px;display:flex;'
               'align-items:center;gap:7px;padding:0 12px;background:' + PAG + ';white-space:nowrap;line-height:20px">'
               '<span style="font-size:17px;color:#a8bfd6">Blend</span>'
               '<span style="font-size:20px;font-weight:700">§blend§</span></div>'
             + vao + '<div style="position:relative;height:52px;flex:none;display:flex;align-items:center">'
             + '<div style="width:28px;flex:none;height:6px;background:%s"></div>' % AZUL
             + '<div style="flex:1;height:4px;background:%s"></div>' % AZUL
             + '<svg width="10" height="14" viewBox="0 0 10 14" style="flex:none"><path d="M0 0l10 7-10 7z" fill="%s"/></svg>' % AZUL
             + _caixa_no(k) + '<div style="flex:1;height:4px;background:%s"></div>' % AZUL
             + '<div style="width:28px;flex:none;height:6px;background:%s"></div></div>' % AZUL + lig + '</div>')
    elif k == 'clientes':
        m = ('<div style="height:88px;flex:none;display:flex;flex-direction:column">' + vao
             + '<div style="height:52px;flex:none;display:flex;align-items:center">'
             + '<div style="width:10px;flex:none;height:6px;background:%s"></div>' % AZUL + SETA_T + _caixa_no(k, True)
             + '</div>' + lig + '</div>')
    else:
        m = ('<div style="height:88px;flex:none;display:flex;flex-direction:column">' + vao
             + '<div style="height:52px;flex:none;display:flex;align-items:center">' + TUBO + SETA_T + _caixa_no(k) + TUBO
             + '</div>' + lig + '</div>')
    return sub(q(m), **t)


def coluna(no_html, corpo):
    """Um visual: a célula do trem em cima e o bloco da etapa embaixo."""
    return RESET + DICA_CSS + RAIZ + "display:flex;flex-direction:column'>" + no_html + corpo + "</div>"


# ---------------------------------------------------- entrega aos clientes
MARCA = {'d': q('<span style="width:16px;height:16px;flex:none;border-radius:50%;background:' + DENTRO + '"></span>'),
         'a': q('<span style="width:0;height:0;flex:none;border-left:10px solid transparent;border-right:10px solid '
                'transparent;border-bottom:17px solid ' + ATENCAO + '"></span>'),
         'f': q('<span style="width:14px;height:14px;flex:none;background:' + FORA + ';transform:rotate(45deg);margin:0 3px"></span>'),
         's': q('<span style="width:16px;height:16px;flex:none;border-radius:50%;border:2px solid ' + SEC + '"></span>')}
SETA = {'+': 'M8 13.5V2.5M3 7.5l5-5 5 5', '-': 'M8 2.5v11M3 8.5l5 5 5-5'}


def variacao(t, grande=False):
    """A variação sobre o período anterior: seta, número e, quando há sentido bom ou
    ruim, a palavra. Sem cor de situação. t: seta (o caminho), var, rot."""
    a, b, c = (20, 26, 17) if grande else (16, 18, 16)
    alt = 32 if grande else 24
    return sub(q('<div style="display:flex;align-items:center;gap:%dpx;white-space:nowrap">' % (8 if grande else 6)
                 + '<svg width="%d" height="%d" viewBox="0 0 16 16" fill="none" stroke="#f3f8fd" stroke-width="2.4" '
                   'stroke-linecap="round" stroke-linejoin="round" style="flex:none"><path d="§seta§"/></svg>' % (a, a)
                 + '<span style="font-size:%dpx;font-weight:700;line-height:%dpx">§var§</span>' % (b, alt)
                 + '<span style="font-size:%dpx;line-height:%dpx;color:#a8bfd6;margin-left:2px">§rot§</span></div>' % (c, alt)), **t)


def medidor_heroi(t):
    """t: x, xt, cor (do ponteiro), falta (o trecho entre o valor e a meta, ou vazio)."""
    return sub(q('<svg width="308" height="32" viewBox="0 0 308 32" style="display:block;flex:none;margin-top:6px">'
                 '<rect x="4" y="15" width="300" height="8" fill="%s"/><rect x="191.5" y="15" width="112.5" height="8" fill="%s"/>'
                 % (TRILHO, ZONA)
                 + '§falta§<path d="M191.5 10v18" stroke="#f3f8fd" stroke-width="1.5"/>'
                   '<path d="M§xt§ 1h14l-7 10z" fill="§cor§"/><path d="M§x§ 9v19" stroke="§cor§" stroke-width="3"/></svg>'), **t)


def falta_heroi(sit, t):
    return sub(q('<rect x="§x§" y="15" width="§w§" height="8" fill="%s"/>' % COR[sit]), **t)


def heroi(t):
    """t: borda, cor_valor (vazio = branco), valor, unidade, marca, cor_pct, pct, meta,
    medidor, mini, de, ate, variacao, dica."""
    return sub(q('<div class="ind" style="position:relative;flex:1;min-height:0;display:flex;flex-direction:column;'
                 'padding:6px 16px 10px;background:linear-gradient(180deg,#0b3157 0%,#061d33 58%);border:2px solid §borda§;'
                 'border-radius:3px">'
                 '<div style="display:flex;align-items:baseline;gap:6px;margin-left:-5px;white-space:nowrap">'
                 '<span style="font-size:108px;font-weight:700;line-height:108px;letter-spacing:-3px§cor_valor§">§valor§</span>'
                 '<span style="font-size:24px;font-weight:600;color:#7cc4f8">§unidade§</span></div>'
                 '<div style="display:flex;align-items:center;gap:10px;margin-top:2px;white-space:nowrap">§marca§'
                 '<span style="font-size:30px;font-weight:700;line-height:36px;color:§cor_pct§">§pct§ da meta</span>'
                 '<span style="flex:1"></span><span style="font-size:17px;color:#a8bfd6">§meta§</span></div>'
                 '§medidor§§mini§'
                 '<div style="display:flex;justify-content:space-between;font-size:16px;line-height:22px;color:#a8bfd6">'
                 '<span>§de§</span><span>tracejado = meta</span><span>§ate§</span></div>'
                 '<div style="margin-top:8px;border-top:1px solid ' + LINHA + ';padding-top:8px">§variacao§</div>§dica§</div>'), **t)


# -------------------------------------------------------- cartão de utilidade
CART = ('position:relative;flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between;'
        'padding:8px 12px;border-radius:3px;')
CART_CALMO = CART + 'background:%s;border:1px solid %s;border-left:6px solid %s' % (PAINEL, LINHA, LINHA)
UM_C = '<div style="font-size:16px;line-height:20px;color:#a8bfd6;white-space:nowrap">§um§</div>'
NOME_C = ('<div style="height:26px;display:flex;align-items:center;white-space:nowrap">'
          '<span style="font-size:19px;font-weight:600;line-height:24px">§nome§</span></div>')
VALOR_C = ('<div style="display:flex;align-items:baseline;gap:6px"><span style="font-size:38px;font-weight:700;'
           'line-height:48px">§valor§</span>§sufixo§</div>')


def sufixo(txt):
    return q('<span style="font-size:22px;color:#a8bfd6">%s</span>' % txt) if txt else ''


def cartao(d, sit):
    """sit: 'd' dentro (ou sem leitura) | 'a', 'f' em destaque | 's' sem meta | 'e' sem
    meta com escala própria. d: nome, um, valor, sufixo, medidor, variacao, dica e,
    conforme a forma, pct, mini, q, ref, frase_css."""
    if sit in ('s', 'e'):
        return sub(q('<div class="ind" style="' + CART_CALMO + '"><div>' + NOME_C + UM_C + '</div>'
                     '<div style="height:48px;display:flex;align-items:center;white-space:nowrap">' + VALOR_C + '</div>'
                     '§medidor§§variacao§§dica§</div>'), **d)
    if sit == 'd':
        return sub(q('<div class="ind" style="' + CART_CALMO + '"><div>' + NOME_C + UM_C + '</div>'
                     '<div style="height:48px;display:flex;align-items:center;justify-content:space-between;white-space:nowrap">'
                     + VALOR_C + '<div style="text-align:right"><div style="font-size:22px;font-weight:700;line-height:24px">§pct§</div>'
                     '<div style="font-size:16px;line-height:20px;color:#a8bfd6">da meta</div></div></div>'
                     '§medidor§§variacao§§dica§</div>'), **d)
    c = COR[sit]
    return sub(q('<div class="ind" style="' + CART + 'background:rgba(%s,%s);border:1px solid %s;border-left:6px solid %s">' % (
                     RGB[sit], TINTA[sit], c, c)
                 + '<div><div style="height:26px;display:flex;align-items:center;justify-content:space-between;gap:8px;'
                   'white-space:nowrap"><span style="font-size:19px;font-weight:700;line-height:24px">§nome§</span>§mini§</div>'
                 + UM_C + '</div>'
                 '<div style="height:48px;display:flex;align-items:center;justify-content:space-between;white-space:nowrap">'
                 '<div style="display:flex;align-items:baseline;gap:6px"><span style="font-size:40px;font-weight:700;'
                 'line-height:48px;color:%s">§valor§</span>§sufixo§</div>' % c
                 + '<div style="text-align:right"><div style="font-size:18px;font-weight:700;line-height:22px;§frase_css§">'
                   '<div>§q§</div><div>§ref§</div></div></div></div>§medidor§§variacao§§dica§</div>'), **d)


def grupo(titulo, ligado, cartoes):
    """Um grupo de utilidades sob a sua coluna. `ligado`: pertence a uma etapa (borda
    tracejada, com a seta de ligação em cima); senão, é total da planta."""
    borda = 'border-top:2px dashed %s;padding-top:4px' % TRAC if ligado else 'border-top:1px solid %s;padding-top:5px' % LINHA
    return (q('<div style="display:flex;flex-direction:column;%s">' % borda
              + '<div style="height:26px;flex:none;display:flex;align-items:center;font-size:16px;font-weight:700;'
                'letter-spacing:1px;color:#a8bfd6">%s</div><div style="flex:1;min-height:0;display:flex;gap:12px">' % titulo)
            + cartoes + '</div></div>')


LIGACAO = q('<div style="display:flex;flex-direction:column;align-items:center">'
            '<svg width="12" height="9" viewBox="0 0 12 9" style="flex:none;display:block"><path d="M6 0l6 9H0z" fill="%s"/></svg>'
            '<div style="flex:1;width:0;border-left:2px dashed %s"></div></div>' % (TRAC, TRAC))


def utilidades(g):
    """g: os quatro grupos, na ordem das colunas (EEBC, TMBR, OR, Clientes)."""
    v = '<div></div>'
    return (RESET + DICA_CSS + RAIZ + "display:grid;grid-template-columns:" + GRADE
            + ";grid-template-rows:%dpx %dpx'>" % (H_LIG, H_UTIL)
            + v + v + LIGACAO + v + LIGACAO + v + v
            + g[0] + v + g[1] + v + g[2] + v + g[3] + "</div>")


# ----------------------------------------------------------- faixa de situação
def contador(marca, t):
    """t: n, cor_n (do número), cor_r e peso (do rótulo), rotulo."""
    return sub(q('<div style="display:flex;align-items:center;gap:10px;white-space:nowrap">') + marca
               + q('<span style="font-size:40px;font-weight:700;line-height:44px;color:§cor_n§">§n§</span>'
                   '<span style="font-size:20px;font-weight:§peso§;color:§cor_r§">§rotulo§</span></div>'), **t)


def marca_cont(forma, cor):
    """A marca de cada contagem: losango (fora), triângulo (atenção), círculo (dentro), anel (sem meta)."""
    m = {'f': '<span style="width:14px;height:14px;flex:none;background:§cor§;transform:rotate(45deg);margin:0 3px"></span>',
         'a': '<span style="width:0;height:0;flex:none;border-left:10px solid transparent;border-right:10px solid '
              'transparent;border-bottom:17px solid §cor§"></span>',
         'd': '<span style="width:16px;height:16px;flex:none;border-radius:50%;background:§cor§"></span>',
         's': '<span style="width:16px;height:16px;flex:none;border-radius:50%;border:2px solid §cor§"></span>'}[forma]
    return sub(q(m), cor=cor)


def situacao(total, contadores):
    return (RESET + RAIZ + "display:flex;align-items:center;justify-content:space-between;padding:0 28px 0 20px;background:"
            + PAINEL + ";border:1px solid " + LINHA + ";border-radius:3px'>"
            + q('<div style="white-space:nowrap"><div style="font-size:16px;font-weight:700;letter-spacing:1.5px;'
                'line-height:20px;color:#a8bfd6">PLANTA</div><div style="font-size:20px;font-weight:600;line-height:26px">'
                '%d indicadores</div></div><div style="width:1px;flex:none;height:40px;background:%s"></div>' % (total, LINHA))
            + contadores + "</div>")


def _par(nome, valor):
    return ("<div style='display:flex;justify-content:space-between;gap:10px;line-height:1.5'>"
            "<span style='color:" + SEC + ";white-space:nowrap'>" + nome + "</span>"
            "<b style='color:" + CLARO + ";white-space:nowrap;font-weight:600'>" + valor + "</b></div>")


def dados(t):
    """O estado dos dados: em dia, pendentes ou atrasados. Ao passar o mouse, abre embaixo
    as três datas da cadeia e o que falta fazer. t: fundo, borda, tinta, titulo, ha, ate,
    dados, plan, bi, falta."""
    return sub(RESET + "<style>.cx:hover+.dt,.dt:hover{display:block!important}</style>" + RAIZ + "'>"
               + q('<div class="cx" style="height:%dpx;display:flex;align-items:center;gap:12px;padding:0 16px 0 14px;'
                   'background:§fundo§;border:1px solid §borda§;border-radius:3px;color:§tinta§;cursor:default">' % H_SIT
                   + '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="§tinta§" stroke-width="2" '
                     'stroke-linecap="round" stroke-linejoin="round" style="flex:none"><circle cx="12" cy="12" r="9"/>'
                     '<path d="M12 7v5.5l3.5 2"/></svg>'
                     '<div style="white-space:nowrap"><div style="font-size:16px;font-weight:700;letter-spacing:1px;'
                     'line-height:20px">§titulo§</div><div style="font-size:26px;font-weight:700;line-height:30px">§ha§</div></div>'
                     '<div style="flex:1"></div><div style="text-align:right;white-space:nowrap">'
                     '<div style="font-size:16px;font-weight:600;line-height:20px">dados até</div>'
                     '<div style="font-size:26px;font-weight:700;line-height:30px">§ate§</div></div></div>')
               + "<div class='dt' style='display:none;margin-top:6px;padding:9px 14px 11px 14px;background:#04182a;"
                 "border:1px solid " + BOTAO_B + ";border-radius:6px;font-size:17px;box-shadow:0 8px 22px rgba(0,0,0,0.6)'>"
               + _par('Dados até', u'§dados§') + _par('Planilha salva', u'§plan§') + _par('Power BI atualizado', u'§bi§')
               + "<div style='margin-top:6px;padding-top:6px;border-top:1px solid " + LINHA + ";color:" + CLARO
               + u";line-height:1.3'>§falta§</div></div></div>", **t)


def periodo(t):
    """A caixa do cabeçalho com as datas do período exibido. Ao passar o mouse, as datas
    com o ano. t: rotulo, valor, completo, nota."""
    return sub(RESET + "<style>.cx:hover+.dt,.dt:hover{display:block!important}</style>" + RAIZ + "'>"
               + q('<div class="cx" style="height:%dpx;display:flex;align-items:center;justify-content:flex-end;gap:14px;'
                   'cursor:default">' % (H_CAB - 1)
                   + '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="1.7" '
                     'stroke-linecap="round" stroke-linejoin="round" style="flex:none">' % AZUL
                   + ICONE['calendario'].replace("'", '"') + '</svg>'
                     '<div style="white-space:nowrap"><div style="font-size:17px;line-height:22px;color:#a8bfd6">§rotulo§</div>'
                     '<div style="font-size:30px;font-weight:700;line-height:36px">§valor§</div></div></div>')
               + "<div class='dt' style='display:none;margin-left:auto;width:max-content;padding:8px 14px 9px 14px;"
                 "background:#04182a;border:1px solid " + BOTAO_B + ";border-radius:6px;box-shadow:0 8px 22px rgba(0,0,0,0.6)'>"
               + "<div style='font-size:18px;font-weight:700;white-space:nowrap'>" + u"§completo§</div>"
               + "<div style='margin-top:3px;font-size:16px;color:" + CLARO + u";white-space:nowrap'>§nota§</div></div></div>", **t)


# -------------------------------------------------------------------- legenda
def legenda():
    div = '<div style="width:1px;height:22px;background:%s"></div>' % LINHA
    item = lambda marca, txt, gap=8: ('<div style="display:flex;align-items:center;gap:%dpx;white-space:nowrap">%s<span>%s</span></div>'
                                      % (gap, marca, txt))
    seta = lambda d: ('<svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="#f3f8fd" stroke-width="2.4" '
                      'stroke-linecap="round" stroke-linejoin="round" style="flex:none"><path d="%s"/></svg>' % d)
    return (RESET + RAIZ + "display:flex;align-items:center;justify-content:space-between;padding:0 18px;border:1px solid "
            + LINHA + ";border-radius:3px;font-size:16px;color:" + CLARO + "'>"
            + q(item('<span style="width:14px;height:14px;flex:none;border-radius:50%%;background:%s"></span>' % DENTRO, 'Dentro da meta')
                + item('<span style="width:0;height:0;flex:none;border-left:8px solid transparent;border-right:8px solid transparent;'
                       'border-bottom:14px solid %s"></span>' % ATENCAO, 'Atenção: até %d%% fora' % (IX.TOLERANCIA * 100))
                + item('<span style="width:12px;height:12px;flex:none;background:%s;transform:rotate(45deg)"></span>' % FORA,
                       'Fora da meta', 10)
                + item('<span style="width:14px;height:14px;flex:none;border-radius:50%%;border:2px solid %s"></span>' % SEC, 'Sem meta')
                + div
                + item('<svg width="34" height="24" viewBox="0 0 34 24"><rect x="0" y="1" width="34" height="3" fill="%s"/>'
                       '<rect x="0" y="7" width="34" height="11" fill="%s"/><rect x="0" y="21" width="34" height="3" fill="%s"/></svg>'
                       % (TRAC, FORA, TRAC), 'Fora ou em atenção: a linha cresce &#183; a ordem não muda', 10)
                + div
                + item('<svg width="80" height="24" viewBox="0 0 107 32"><rect x="3" y="16" width="101" height="6" fill="%s"/>'
                       '<rect x="3" y="16" width="63" height="6" fill="%s"/><path d="M66 11v16" stroke="#f3f8fd" stroke-width="2"/>'
                       '<path d="M34 2h12l-6 9z" fill="#f3f8fd"/><path d="M40 10v17" stroke="#f3f8fd" stroke-width="3"/></svg>'
                       % (TRILHO, ZONA), 'Faixa verde e tracejado = meta &#183; ponteiro = valor', 10)
                + '<div style="display:flex;align-items:center;gap:4px;white-space:nowrap">' + seta(SETA['+']) + seta(SETA['-'])
                + '<span style="margin-left:4px">Variação sobre o período anterior</span></div>')
            + "</div>")
