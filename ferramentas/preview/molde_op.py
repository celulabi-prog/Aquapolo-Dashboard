# -*- coding: utf-8 -*-
"""
Molde ÚNICO do HTML do Painel Operacional.

Toda função recebe apenas TEXTO já pronto e devolve HTML. Nenhuma conta aqui.
O mesmo molde serve a dois usos:
  - preview .......: os valores são números já formatados -> vira a página que eu renderizo
  - gerador de DAX : os valores são pedaços de DAX        -> vira a medida do Power BI
Como o molde é o mesmo, o que aparece no preview é o que o Power BI desenha.

Regra dura: nada de aspas duplas no HTML. Ele vira literal de string DAX.
"""
import indicadores_op as IX
from estilo_op import *

RESET = ("<style>html,body{margin:0;padding:0;height:100%;overflow:hidden}"
         "*{box-sizing:border-box}</style>")
# Cada indicador (.ind) guarda a sua aba de explicação (.dc), que só aparece com o mouse em cima.
DICA_CSS = ("<style>.dc{display:none}.ind{cursor:help}"
            ".ind:hover{box-shadow:inset 0 0 0 1px #2f79ad}.ind:hover>.dc{display:block}</style>")


# ------------------------------------------------------------------- ícones
def _svg(corpo, tam=26, risco=1.7):
    return ("<svg viewBox='0 0 24 24' width='" + str(tam) + "' height='" + str(tam)
            + "' fill='none' stroke='currentColor' stroke-width='" + str(risco)
            + "' stroke-linecap='round' stroke-linejoin='round'>" + corpo + "</svg>")


def _pontos(pares, r=1.3):
    return ''.join("<circle cx='%s' cy='%s' r='%s' fill='currentColor' stroke='none'/>" % (a, b, r)
                   for a, b in pares)


ICONE = {
    'gota': "<path d='M12 3c3.4 4 5.5 6.6 5.5 9.3A5.5 5.5 0 0 1 6.5 12.3C6.5 9.6 8.6 7 12 3z'/>",
    'engrenagem': ("<circle cx='12' cy='12' r='3.1'/>"
                   "<path d='M12 2.6v2.1M12 19.3v2.1M21.4 12h-2.1M4.7 12H2.6"
                   "M18.6 5.4l-1.5 1.5M6.9 17.1l-1.5 1.5M18.6 18.6l-1.5-1.5M6.9 6.9L5.4 5.4'/>"),
    'funil': "<path d='M3.5 4.5h17l-6.6 7.8v6.4l-3.8 2v-8.4z'/>",
    'folha': ("<path d='M20 4c0 8.3-4.2 12.4-10.4 12.4A5.6 5.6 0 0 1 4 10.8C4 5.6 9.6 4 20 4z'/>"
              "<path d='M4.6 19.4C7 15 11 11.6 16.2 9.6'/>"),
    'raio': "<path d='M13.4 2.5L4.8 13.4h5.6l-.8 8.1 8.6-10.9h-5.6z' fill='currentColor' stroke='none'/>",
    'retro': ("<path d='M4.2 10.2a8 8 0 0 1 13.4-3.3l2.2 2.1'/>"
              "<path d='M19.8 13.8a8 8 0 0 1-13.4 3.3l-2.2-2.1'/>"
              "<path d='M20.3 4.4v4.6h-4.6M3.7 19.6V15h4.6'/>"),
    'frasco': ("<path d='M9.4 2.8h5.2M10.3 2.8v6.1L5 18.6a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5.3-9.7V2.8'/>"
               "<path d='M7.2 15.4h9.6'/>" + _pontos([(10, 18), (13.4, 18.6)], 0.9)),
    'molecula': ("<circle cx='12' cy='5.2' r='2.3'/><circle cx='5.2' cy='17' r='2.3'/>"
                 "<circle cx='18.8' cy='17' r='2.3'/><path d='M10.8 7.2L6.4 14.9M13.2 7.2l4.4 7.7M7.5 17h9'/>"),
    'ondas': ("<path d='M2.6 7.6c1.9-1.9 3.7-1.9 5.6 0s3.7 1.9 5.6 0 3.7-1.9 5.6 0'/>"
              "<path d='M2.6 12.4c1.9-1.9 3.7-1.9 5.6 0s3.7 1.9 5.6 0 3.7-1.9 5.6 0'/>"
              "<path d='M2.6 17.2c1.9-1.9 3.7-1.9 5.6 0s3.7 1.9 5.6 0 3.7-1.9 5.6 0'/>"),
    'diamante': ("<path d='M6.2 3.4h11.6l3.4 5.4L12 20.8 2.8 8.8z'/>"
                 "<path d='M2.8 8.8h18.4M8.7 3.4l-2.5 5.4L12 20.8l5.8-12-2.5-5.4'/>"),
    'lodo': "<circle cx='8.4' cy='8.6' r='3.5'/><circle cx='15.8' cy='8.6' r='3'/><circle cx='12' cy='16.2' r='3.8'/>",
    'microorg': ("<circle cx='12' cy='12' r='3'/>"
                 "<path d='M12 2.8v2.6M12 18.6v2.6M21.2 12h-2.6M5.4 12H2.8"
                 "M18.5 5.5l-1.8 1.8M7.3 16.7l-1.8 1.8M18.5 18.5l-1.8-1.8M7.3 7.3L5.5 5.5'/>"),
    # arco aberto embaixo + ponteiro: a mostrador fechado vira um círculo cortado
    'manometro': ("<path d='M3.6 17.4a9 9 0 1 1 16.8 0'/>"
                  "<path d='M12 17.4L16.6 9.6'/>" + _pontos([(12, 17.4)], 1.6)),
    'colunas': ("<path d='M4 4.6v14.8M8.7 4.6v14.8M12 4.6v14.8M15.3 4.6v14.8M20 4.6v14.8'/>"
                "<path d='M2.6 4.6h18.8M2.6 19.4h18.8'/>"),
    'turbidez': _pontos([(6, 6), (12, 4.6), (18, 6), (4.6, 12), (12, 9.8), (19.4, 12),
                         (6, 18), (12, 15.2), (18, 18), (9, 12.4), (15, 12.4)], 1.25),
    'sdi': (_pontos([(12, 12)], 2.4) + _pontos(
            [(12, 4.4), (12, 19.6), (4.4, 12), (19.6, 12),
             (6.6, 6.6), (17.4, 6.6), (6.6, 17.4), (17.4, 17.4)], 1.25)),
    'ventilador': ("<circle cx='12' cy='12' r='2.2'/>"
                   "<path d='M12 9.8c0-3.6.9-6.4 3.4-6.4 2 0 2.8 2.4 1.2 4.3-1.2 1.4-2.9 2.1-4.6 2.1z'/>"
                   "<path d='M14.2 12c3.6 0 6.4.9 6.4 3.4 0 2-2.4 2.8-4.3 1.2-1.4-1.2-2.1-2.9-2.1-4.6z'/>"
                   "<path d='M9.8 12c-3.6 0-6.4-.9-6.4-3.4 0-2 2.4-2.8 4.3-1.2 1.4 1.2 2.1 2.9 2.1 4.6z'/>"
                   "<path d='M12 14.2c0 3.6-.9 6.4-3.4 6.4-2 0-2.8-2.4-1.2-4.3 1.2-1.4 2.9-2.1 4.6-2.1z'/>"),
    'tubos': ("<path d='M2.6 8.4h7.2a2.6 2.6 0 0 1 2.6 2.6v2a2.6 2.6 0 0 0 2.6 2.6h6.4'/>"
              "<path d='M18.6 12.8l2.8 2.8-2.8 2.8M2.6 5.6v5.6'/>"),
    'calendario': ("<rect x='3.5' y='5' width='17' height='15.5' rx='2.2'/>"
                   "<path d='M3.5 10h17M8 3v4M16 3v4'/>"),
    'info': "<circle cx='12' cy='12' r='9'/><path d='M12 11v6M12 7.4v.2'/>",
}


def chip(icone, tam=60, ic=31, cor=CLARO, fundo=CHIP, borda=CHIP_B, raio=14):
    return ("<div style='width:" + str(tam) + "px;height:" + str(tam) + "px;flex:none;border-radius:"
            + str(raio) + "px;background:" + fundo + ";border:1px solid " + borda + ";color:" + cor
            + ";display:flex;align-items:center;justify-content:center'>"
            + _svg(ICONE[icone], ic) + "</div>")


# ------------------------------------------------------- cabeçalho de painel
def cab_painel(titulo, sub, icones, grad, sub_dir=True):
    """sub_dir=False cola o subtítulo no título — nos painéis largos, encostado
    na borda direita ele ficaria longe demais do que está nomeando."""
    ic = ''.join("<span style='color:" + c + ";display:flex'>" + _svg(ICONE[n], 34, 1.9) + "</span>"
                 for n, c in icones)
    folga = 'margin-left:auto;padding-left:14px' if sub_dir else 'margin-left:34px'
    sb = ("<span style='" + folga + ";font-size:16px;color:#9dbbd8;"
          "font-weight:400;white-space:nowrap'>" + sub + "</span>") if sub else ''
    return ("<div style='height:" + str(H_FAIXA) + "px;flex:none;border-radius:10px;background:" + grad
            + ";border:1px solid #2a6ca8;display:flex;align-items:center;gap:14px;padding:0 18px'>"
            + ic
            + "<span style='font-size:27px;font-weight:700;color:" + BRANCO
            + ";letter-spacing:0.8px;white-space:nowrap'>" + titulo + "</span>" + sb + "</div>")


def barra(larg, cor, marcadores, alt=24):
    """Trilho + preenchimento + um tracejado em cada limite da meta (IX.marcadores).
    Sem tracejado ([]) a barra não é contra a meta: sai azul, sem juízo de bom ou ruim.
    None = não há com o que comparar: fica só o contorno do trilho."""
    raio = str(alt // 2)
    if marcadores is None:
        return ("<div style='height:" + str(alt) + "px;border:1px dashed #2a5f78;border-radius:"
                + raio + "px'></div>")
    tracos = ''.join("<div style='position:absolute;left:%.1f%%;top:-4px;height:%dpx;"
                     "border-left:2px dashed rgba(255,255,255,0.92)'></div>" % (m, alt + 8)
                     for m in marcadores)
    return ("<div style='position:relative;height:" + str(alt) + "px;background:" + TRILHO
            + ";border-radius:" + raio + "px;border:1px solid #16375a'>"
            + "<div style='width:" + larg + "%;height:100%;background:" + (cor if marcadores else AZUL)
            + ";border-radius:" + raio + "px'></div>" + tracos + "</div>")


# ------------------------------------------------------- aba do indicador
def _celula(rotulo, valor, abaixo=''):
    """Uma informação da aba: rótulo pequeno, o dado em destaque e, embaixo, um complemento."""
    return ("<div><div style='font-size:16px;color:" + SEC + "'>" + rotulo + "</div>"
            "<div style='font-size:25px;font-weight:700;color:" + BRANCO + "'>" + valor + "</div>"
            + ("<div style='font-size:21px;font-weight:600;color:" + CLARO + "'>" + abaixo + "</div>"
               if abaixo else '') + "</div>")


def dica(D, onde):
    """A aba que abre ao passar o mouse num indicador: com o que o número é comparado.
    As datas do período exibido, a meta e, nos cartões, o período anterior com o valor
    dele (o que o Delta Per. compara). `onde` é a posição dentro do visual: a aba não
    pode sair do retângulo dele, e fica da largura do que tem dentro. Não recebe o
    mouse, para que o indicador de baixo responda mesmo estando coberto."""
    if 'ant' in D:
        celulas = (_celula('Período exibido', D['periodo'], D['valor'])
                   + _celula('Período anterior', D['ant_periodo'], D['ant']))
    else:
        celulas = _celula('Período exibido', D['periodo'])
    celulas += (_celula('Meta', D['meta'], D['pct'] + ' da meta') if D['meta']
                else _celula('Meta', 'sem meta'))
    return ("<div class='dc' style='position:absolute;" + onde + ";z-index:9;pointer-events:none;"
            "padding:11px 18px 13px 18px;background:#04182a;border:1px solid " + BOTAO_B
            + ";border-radius:10px;box-shadow:0 8px 22px rgba(0,0,0,0.6);font-weight:400;"
            "line-height:1.3;text-align:left;white-space:nowrap'>"
            + "<div style='display:flex;align-items:baseline;gap:9px'>"
            + "<b style='font-size:22px;color:" + BRANCO + "'>" + D['nome'] + "</b>"
            + "<span style='font-size:18px;color:" + SEC + "'>" + D['unidade'] + "</span>"
            + ("<b style='margin-left:auto;padding-left:28px;font-size:20px;color:" + D['cor'] + "'>"
               + D['situacao'] + "</b>" if D['meta'] else '') + "</div>"
            + "<div style='display:flex;gap:36px;margin-top:7px'>" + celulas + "</div></div>")


# ------------------------------------------------------- linha de indicador
def linha_ind(L, i, n):
    """Uma linha: ícone | nome/unidade | valor | barra | meta. É a linha i de n: as de
    cima abrem a aba para baixo e as de baixo, para cima."""
    uni = ("<div style='font-size:17px;color:" + SEC + ";margin-top:2px'>"
           + L['unidade'] + "</div>") if L['unidade'] else ''
    onde = 'left:12px;margin:3px 0;' + ('top:100%' if i < (n + 1) // 2 else 'bottom:100%')
    return ("<div class='ind' style='position:relative;flex:1;min-height:0;display:flex;align-items:center;"
            "gap:14px;padding:0 14px 0 18px;border-top:1px solid " + SEP + "'>"
            + chip(L['icone'])
            + "<div style='flex:1;min-width:0'>"
            + "<div style='font-size:19px;font-weight:600;color:" + BRANCO + ";line-height:1.15;"
            "white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" + L['nome'] + "</div>"
            + uni + "</div>"
            + "<div style='width:88px;flex:none;text-align:right;font-size:34px;font-weight:700;color:"
            + BRANCO + ";white-space:nowrap'>" + L['valor'] + "</div>"
            + "<div style='width:132px;flex:none'>" + L['barra'] + "</div>"
            + "<div style='width:96px;flex:none;text-align:left;line-height:1.22'>"
            + "<div style='font-size:17px;color:" + SEC + "'>Meta</div>"
            + "<div style='font-size:19px;font-weight:700;color:" + CLARO + ";white-space:nowrap'>"
            + (L['meta'] or '&#8212;') + "</div></div>" + dica(L, onde) + "</div>")


def painel_linhas(d, linhas):
    return RESET + DICA_CSS + (
        "<div style='" + FONTE + "height:100vh;width:100%;display:flex;flex-direction:column;gap:5px'>"
        + cab_painel(d['titulo'], d['sub'], d['icones'], d['grad'], d.get('sub_dir', True))
        + "<div style='flex:1;min-height:0;display:flex;flex-direction:column;background:" + PANEL
        + ";border:1px solid " + BORDA + ";border-radius:10px;overflow:hidden'>" + linhas + "</div></div>")


# -------------------------------------------------------- cartão de consumo
def cartao_ind(C, i, n):
    """Um cartão. É o cartão i de n: a aba abre no alto do painel, por cima do título e
    dos nomes, do lado em que o cartão está. Os números continuam à vista."""
    uni = ("<div style='font-size:16px;color:" + SEC + ";margin-top:1px;white-space:nowrap'>"
           + C['unidade'] + "</div>") if C['unidade'] else ''
    onde = 'top:0;' + ('left:0' if i < n / 2 else 'right:0')
    if C['meta']:
        pe = ("<span>Meta " + C['meta'] + "</span><span style='margin-left:auto;padding-left:8px'>"
              "<b style='font-size:17px;color:" + BRANCO + "'>" + C['pct'] + "</b> da meta</span>")
    else:
        pe = ("<span>" + ('Sem meta' if C['obs'] else IX.SEM_META) + "</span>"
              "<span style='margin-left:auto;padding-left:8px'>" + C['obs'] + "</span>")
    return ("<div class='ind' style='flex:1;min-width:0;display:flex;flex-direction:column;background:" + CARTAO
            + ";border:1px solid " + BORDA_C + ";border-radius:10px;padding:13px 12px 12px 12px'>"
            + "<div style='display:flex;align-items:center;gap:11px'>" + chip(C['icone'], 44, 23, raio=11)
            + "<div style='min-width:0'><div style='font-size:16px;font-weight:600;color:" + BRANCO
            + ";line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
            + C['nome'] + "</div>" + uni + "</div></div>"
            + "<div style='flex:1'></div>"
            + "<div style='display:flex;align-items:flex-end;gap:6px'>"
            + "<div style='font-size:38px;font-weight:700;color:" + BRANCO + ";line-height:1;"
            "white-space:nowrap'>" + C['valor'] + "</div>"
            + "<div style='margin-left:auto;text-align:right'>"
            + "<div style='font-size:18px;font-weight:700;color:" + C['cor_var'] + ";white-space:nowrap'>"
            + C['seta'] + " " + C['var'] + "</div>"
            + "<div style='font-size:15px;color:" + SEC + ";margin-top:2px'>&#916; Per.</div></div></div>"
            + "<div style='margin-top:12px'>" + C['barra'] + "</div>"
            + "<div style='margin-top:7px;height:24px;display:flex;align-items:baseline;font-size:14px;"
            "line-height:24px;color:" + SEC + ";white-space:nowrap'>" + pe + "</div>" + dica(C, onde) + "</div>")


def painel_cartoes(d, cartoes):
    # position:relative: é a este retângulo, o do visual, que a aba dos cartões se prende.
    return RESET + DICA_CSS + (
        "<div style='" + FONTE + "position:relative;height:100vh;width:100%;display:flex;"
        "flex-direction:column;gap:5px'>"
        + cab_painel(d['titulo'], d['sub'], d['icones'], d['grad'], d.get('sub_dir', True))
        + "<div style='flex:1;min-height:0;display:flex;gap:9px;padding:11px;background:" + PANEL2
        + ";border:1px solid " + BORDA + ";border-radius:10px'>" + cartoes + "</div></div>")


# --------------------------------------------------------- caixas do cabeçalho
# Duas caixas no estilo do seletor pintado: o período exibido e o status da
# atualização. Ao passar o mouse, cada uma abre embaixo um detalhe. O detalhe
# abre dentro do retângulo do próprio visual, por isso o visual é mais alto
# que a caixa (estilo_op.H_DET diz até onde ele pode ir).
def _caixa(icone, cor_icone, rotulo, valor, cor_valor, larg=None):
    """A parte sempre visível: ícone, uma linha pequena e uma linha em destaque.
    Com `larg`, a caixa é mais estreita que o visual e fica encostada à direita."""
    return ("<div class='cx' style='" + ('width:%dpx;margin-left:auto;' % larg if larg else '')
            + "height:" + str(H_BOTAO) + "px;display:flex;align-items:center;gap:12px;"
            "padding:0 12px 0 16px;background:" + BOTAO + ";border:1px solid " + BOTAO_B
            + ";border-radius:10px;cursor:default'>"
            + "<span style='color:" + cor_icone + ";display:flex;flex:none'>" + _svg(ICONE[icone], 34, 1.8) + "</span>"
            + "<div style='min-width:0'>"
            + "<div style='font-size:15px;color:" + CLARO + ";white-space:nowrap;overflow:hidden;"
            "text-overflow:ellipsis'>" + rotulo + "</div>"
            + "<div style='font-size:23px;font-weight:700;color:" + cor_valor + ";line-height:1.25;"
            "white-space:nowrap'>" + valor + "</div></div></div>")


def _cabecalho(caixa, detalhe, fonte):
    return RESET + (
        "<style>.cx:hover+.dt,.dt:hover{display:block!important}</style>"
        "<div style='" + FONTE + "height:100vh;width:100%'>" + caixa
        + "<div class='dt' style='display:none;margin-top:5px;padding:8px 14px 9px 14px;background:#04182a;"
        "border:1px solid " + BOTAO_B + ";border-radius:10px;font-size:" + str(fonte) + "px'>"
        + detalhe + "</div></div>")


def _par(nome, valor, alt='1.6'):
    """Uma linha do detalhe: o nome à esquerda e o valor à direita."""
    return ("<div style='display:flex;justify-content:space-between;gap:10px;line-height:" + alt + "'>"
            "<span style='color:" + SEC + ";white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
            + nome + "</span><b style='color:" + CLARO + ";white-space:nowrap;font-weight:600'>"
            + valor + "</b></div>")


def status(d):
    """Os dados estão em dia? No detalhe, à esquerda as três datas da cadeia e à
    direita o que falta fazer."""
    detalhe = ("<div style='display:flex;align-items:center;gap:16px'>"
               "<div style='flex:none;width:266px'>" + _par('Dados até', d['dados'], '1.4')
               + _par('Planilha salva', d['plan'], '1.4') + _par('Power BI atualizado', d['bi'], '1.4')
               + "</div><div style='flex:1;padding-left:16px;border-left:1px solid " + BOTAO_B + ";color:"
               + CLARO + ";line-height:1.35'>" + d['falta'] + "</div></div>")
    return _cabecalho(_caixa('retro', d['cor'], d['rotulo'], d['palavra'], d['cor'], W_CX_STA), detalhe, 17)


def periodo(d):
    """De que dia a que dia vai o período exibido. No detalhe, as datas com o ano. O
    período de cada indicador fica na aba dele."""
    detalhe = ("<div style='font-size:18px;font-weight:700;color:" + BRANCO + ";white-space:nowrap'>"
               + d['completo'] + "</div>"
               + "<div style='margin-top:3px;color:" + CLARO + ";line-height:1.3'>" + d['nota'] + "</div>")
    return _cabecalho(_caixa('calendario', CLARO, d['rotulo'], d['valor'], BRANCO), detalhe, 16)


# -------------------------------------------------------------------- rodapé
def _glossario(termo, texto):
    return ("<div style='display:flex;align-items:center;gap:11px'>"
            "<b style='font-size:17px;color:" + CLARO + ";white-space:nowrap'>" + termo + "</b>"
            "<span style='font-size:15px;color:" + SEC + ";line-height:1.3'>" + texto + "</span></div>")


def rodape():
    """Como ler a página: o aviso da aba de explicação e a legenda das cores, da meta,
    da barra e da variação. A data dos dados fica na caixa do cabeçalho."""
    div = "<div style='width:1px;height:42px;background:#2a5f78;flex:none'></div>"
    pt = ("<span style='display:inline-block;width:14px;height:14px;border-radius:50%;"
          "vertical-align:-2px;margin-right:8px;background:")
    return RESET + (
        "<div style='" + FONTE + "height:100vh;width:100%;display:flex;align-items:center;gap:22px;"
        "padding:0 24px;background:#04182a;border:1px solid #1f5a66;border-radius:10px'>"
        + "<span style='color:" + CLARO + ";display:flex;flex:none'>" + _svg(ICONE['info'], 28, 1.6) + "</span>"
        + "<span style='font-size:16px;color:" + CLARO + ";line-height:1.3;white-space:nowrap'>"
        + "<b>Passe o mouse</b> num indicador para ver<br>como é calculado e com o que é comparado</span>"
        + div
        + "<div><div style='font-size:17px;color:" + CLARO + ";white-space:nowrap'>"
        + "<b>Cores</b> <span style='font-size:15px;color:" + SEC
        + "'>(valor em relação à meta)</span></div>"
        + "<div style='margin-top:7px;font-size:16px;color:" + CLARO + ";white-space:nowrap'>"
        + pt + VERDE + "'></span>Dentro da meta &nbsp;&nbsp;"
        + pt + AMARELO + "'></span>Atenção: até " + ('%d' % (IX.TOLERANCIA * 100)) + "% fora &nbsp;&nbsp;"
        + pt + VERMELHO + "'></span>Fora da meta &nbsp;&nbsp;"
        + pt + AZUL + "'></span>Sem meta</div></div>"
        + div + _glossario('Meta', '&#8804; no máximo &nbsp;&#183;&nbsp; &#8805; no mínimo<br>'
                                   'a &#8211; b: dentro da faixa')
        + div + _glossario('Barra', 'Valor em relação à meta;<br>o tracejado marca a meta')
        + div + _glossario('&#916; Per.', 'Variação sobre o período<br>anterior, de mesmo tamanho')
        + "</div>")
