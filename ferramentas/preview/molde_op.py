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
from estilo_op import *

RESET = ("<style>html,body{margin:0;padding:0;height:100%;overflow:hidden}"
         "*{box-sizing:border-box}</style>")


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
    'relogio': "<circle cx='12' cy='12' r='9'/><path d='M12 6.6V12l3.6 2.2'/>",
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


def _barra(larg, cor, marcador, alt=24, trilho=TRILHO):
    """Trilho + preenchimento + traço da referência."""
    return ("<div style='position:relative;height:" + str(alt) + "px;background:" + trilho
            + ";border-radius:" + str(alt // 2) + "px;border:1px solid #16375a'>"
            + "<div style='width:" + larg + "%;height:100%;background:" + cor
            + ";border-radius:" + str(alt // 2) + "px'></div>"
            + "<div style='position:absolute;left:" + marcador + "%;top:-4px;height:"
            + str(alt + 8) + "px;border-left:2px dashed rgba(255,255,255,0.92)'></div></div>")


# ------------------------------------------------------- linha de indicador
def linha_ind(L):
    """Uma linha: ícone | nome/unidade | valor | barra | referência."""
    uni = ("<div style='font-size:17px;color:" + SEC + ";margin-top:2px'>"
           + L['unidade'] + "</div>") if L['unidade'] else ''
    return ("<div style='flex:1;min-height:0;display:flex;align-items:center;gap:14px;"
            "padding:0 14px 0 18px;border-top:1px solid " + SEP + "'>"
            + chip(L['icone'])
            + "<div style='flex:1;min-width:0'>"
            + "<div style='font-size:19px;font-weight:600;color:" + BRANCO + ";line-height:1.15;"
            "white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" + L['nome'] + "</div>"
            + uni + "</div>"
            + "<div style='width:88px;flex:none;text-align:right;font-size:34px;font-weight:700;color:"
            + BRANCO + ";white-space:nowrap'>" + L['valor'] + "</div>"
            + "<div style='width:144px;flex:none'>" + _barra(L['larg'], L['cor'], L['marcador']) + "</div>"
            + "<div style='width:84px;flex:none;text-align:left;line-height:1.22'>"
            + "<div style='font-size:17px;color:" + SEC + "'>" + L['rot_ref'] + "</div>"
            + "<div style='font-size:19px;font-weight:700;color:" + CLARO + ";white-space:nowrap'>"
            + L['ref'] + "</div></div></div>")


def painel_linhas(d, linhas):
    return RESET + (
        "<div style='" + FONTE + "height:100vh;width:100%;display:flex;flex-direction:column;gap:5px'>"
        + cab_painel(d['titulo'], d['sub'], d['icones'], d['grad'], d.get('sub_dir', True))
        + "<div style='flex:1;min-height:0;display:flex;flex-direction:column;background:" + PANEL
        + ";border:1px solid " + BORDA + ";border-radius:10px;overflow:hidden'>" + linhas + "</div></div>")


# -------------------------------------------------------- cartão de consumo
def cartao_ind(C):
    uni = ("<div style='font-size:16px;color:" + SEC + ";margin-top:1px;white-space:nowrap'>"
           + C['unidade'] + "</div>") if C['unidade'] else ''
    return ("<div style='flex:1;min-width:0;display:flex;flex-direction:column;background:" + CARTAO
            + ";border:1px solid " + BORDA_C + ";border-radius:10px;padding:13px 14px 12px 14px'>"
            + "<div style='display:flex;align-items:center;gap:11px'>" + chip(C['icone'], 44, 23, raio=11)
            + "<div style='min-width:0'><div style='font-size:17px;font-weight:600;color:" + BRANCO
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
            + "<div style='margin-top:12px'>" + _barra(C['larg'], C['cor'], C['marcador'], 20) + "</div>"
            + "<div style='margin-top:9px;display:flex;align-items:baseline;font-size:16px;color:" + SEC + "'>"
            + "<span style='white-space:nowrap'>" + C['ref'] + "</span>"
            + "<b style='margin-left:auto;padding-left:8px;font-size:19px;color:" + BRANCO + "'>"
            + C['pct'] + "</b></div></div>")


def cartao_vazio(C):
    """Cartão de indicador que a base ainda não tem."""
    uni = ("<div style='font-size:16px;color:" + SEC + ";margin-top:1px;white-space:nowrap'>"
           + C['unidade'] + "</div>") if C['unidade'] else ''
    return ("<div style='flex:1;min-width:0;display:flex;flex-direction:column;background:" + CARTAO
            + ";border:1px solid " + BORDA_C + ";border-radius:10px;padding:13px 14px 12px 14px'>"
            + "<div style='display:flex;align-items:center;gap:11px'>" + chip(C['icone'], 44, 23, raio=11)
            + "<div style='min-width:0'><div style='font-size:17px;font-weight:600;color:" + BRANCO
            + ";line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
            + C['nome'] + "</div>" + uni + "</div></div>"
            + "<div style='flex:1'></div>"
            + "<div style='font-size:38px;font-weight:700;color:" + CINZA + ";line-height:1'>&#8212;</div>"
            + "<div style='margin-top:12px;font-size:15px;color:" + TER + ";line-height:1.35'>"
            + C['aviso'] + "</div></div>")


def painel_cartoes(d, cartoes):
    return RESET + (
        "<div style='" + FONTE + "height:100vh;width:100%;display:flex;flex-direction:column;gap:5px'>"
        + cab_painel(d['titulo'], d['sub'], d['icones'], d['grad'], d.get('sub_dir', True))
        + "<div style='flex:1;min-height:0;display:flex;gap:9px;padding:11px;background:" + PANEL2
        + ";border:1px solid " + BORDA + ";border-radius:10px'>" + cartoes + "</div></div>")


# -------------------------------------------------------------------- rodapé
def _glossario(termo, texto):
    return ("<div style='display:flex;align-items:center;gap:11px'>"
            "<b style='font-size:17px;color:" + CLARO + ";white-space:nowrap'>" + termo + "</b>"
            "<span style='font-size:15px;color:" + SEC + ";line-height:1.3'>" + texto + "</span></div>")


def rodape(d):
    div = "<div style='width:1px;height:42px;background:#2a5f78;flex:none'></div>"
    pt = ("<span style='display:inline-block;width:14px;height:14px;border-radius:50%;"
          "vertical-align:-2px;margin-right:8px;background:")
    return RESET + (
        "<div style='" + FONTE + "height:100vh;width:100%;display:flex;align-items:center;gap:24px;"
        "padding:0 26px;background:#04182a;border:1px solid #1f5a66;border-radius:10px'>"
        + "<span style='color:" + SEC + ";display:flex;flex:none'>" + _svg(ICONE['relogio'], 25, 1.6) + "</span>"
        + "<span style='font-size:17px;color:" + CLARO + ";white-space:nowrap'>Última atualização: "
        + d['ult'] + "</span>"
        + div
        + "<div><div style='font-size:17px;color:" + CLARO + ";white-space:nowrap'>"
        + "<b>Legenda do status</b> <span style='font-size:15px;color:" + SEC
        + "'>(em relação à referência)</span></div>"
        + "<div style='margin-top:7px;font-size:16px;color:" + CLARO + ";white-space:nowrap'>"
        + pt + VERDE + "'></span>Dentro da meta &nbsp;&nbsp;&nbsp;"
        + pt + AMARELO + "'></span>Atenção &nbsp;&nbsp;&nbsp;"
        + pt + VERMELHO + "'></span>Fora da meta</div></div>"
        + div + _glossario('&#916; Per.', 'Variação em relação ao<br>período anterior')
        + div + _glossario('Ref.', 'Valor de referência<br>(meta)')
        + div + _glossario('Faixa', 'Faixa operacional')
        + "<div style='margin-left:auto;padding-left:24px;font-size:16px;color:" + SEC
        + ";white-space:nowrap'>Aquapolo &nbsp;&#124;&nbsp; GS Inima &nbsp;&#124;&nbsp; Sabesp</div>"
        + "</div>")
