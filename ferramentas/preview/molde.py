# -*- coding: utf-8 -*-
"""
Molde ÚNICO do HTML dos painéis.

Toda função recebe apenas TEXTO já pronto e devolve HTML. Nenhuma conta aqui.
Isso permite usar o mesmo molde de dois jeitos:
  - preview .......: os valores são números já formatados  -> vira uma página que eu renderizo
  - gerador de DAX : os valores são pedaços de DAX         -> vira a medida do Power BI
Como o molde é o mesmo, o que aparece no preview é o que o Power BI desenha.
"""
from estilo import *

RESET = ("<style>html,body{margin:0;padding:0;height:100%;overflow:hidden}"
         "*{box-sizing:border-box}</style>")
FONTE = "font-family:Segoe UI,sans-serif;"


# ------------------------------------------------------------------ cabeçalho
def cabecalho(d):
    pt = ("<span style='display:inline-block;width:7px;height:7px;border-radius:50%;"
          "margin-right:5px;background:")
    return RESET + (
        "<div style='" + FONTE + "position:relative;height:100%;"
        "background:linear-gradient(100deg,#0c2038 0%,#133053 58%,#17436f 100%);"
        "border:1px solid " + BORDA + ";border-radius:8px'>"
        + "<div style='position:absolute;left:22px;top:24px'>"
        + "<div style='font-size:26px;font-weight:800;color:#fff;line-height:1;letter-spacing:-0.6px'>Aquapolo</div>"
        + "<div style='margin-top:5px;font-size:10px;color:#9dc2e6'>GS Inima &nbsp;|&nbsp; Sabesp</div></div>"
        + "<div style='position:absolute;left:196px;top:24px;width:1px;height:44px;background:#2d5c8a'></div>"
        + "<div style='position:absolute;left:220px;top:25px'>"
        + "<div style='font-size:19px;font-weight:700;color:#fff;line-height:1.1'>Painel Operacional</div>"
        + "<div style='margin-top:4px;font-size:11px;color:#8fb6dd'>Indicadores de volumes por cliente</div></div>"
        + "<div style='position:absolute;left:1040px;top:40px;font-size:10px;color:#9dc2e6'>"
        + pt + VERDE + "'></span>Dentro da meta &nbsp;&nbsp;"
        + pt + AMARELO + "'></span>Atenção &nbsp;&nbsp;"
        + pt + VERMELHO + "'></span>Fora da meta</div>"
        + "<div style='position:absolute;right:20px;top:28px;text-align:right'>"
        + "<div style='font-size:10px;color:#8fb6dd'>Última atualização</div>"
        + "<div style='margin-top:3px;font-size:13px;font-weight:600;color:#cfe4fa'>" + d['ult'] + "</div></div>"
        + "</div>")


def card_cliente(d):
    return RESET + (
        "<div style='" + FONTE + CARD + ";padding:12px 16px'>"
        + "<div style='font-size:11px;color:" + SEC + ";letter-spacing:0.3px'>Cliente selecionado</div></div>")


def card_volume(d):
    div = "<div style='width:1px;height:58px;background:" + BORDA + ";flex:none'></div>"
    rot = "<div style='font-size:11px;color:" + SEC + "'>"
    return RESET + (
        "<div style='" + FONTE + CARD + ";flex-direction:row;align-items:center;padding:0 22px;gap:22px'>"
        + "<div style='flex:1.2'>" + rot + "Volume atual &#183; " + d['rot'] + "</div>"
        + "<div style='font-size:32px;font-weight:700;color:#fff;line-height:1.05;margin-top:2px'>" + d['vol'] + "</div>"
        + "<div style='font-size:10.5px;color:" + SEC + "'>m&#179;/d</div></div>"
        + div
        + "<div style='flex:0.9'>" + rot + "Vazão</div>"
        + "<div style='font-size:27px;font-weight:700;color:#cfe4fa;line-height:1.05;margin-top:2px'>" + d['ls'] + "</div>"
        + "<div style='font-size:10.5px;color:" + SEC + "'>L/s</div></div>"
        + div
        + "<div style='flex:1.1'>" + rot + "vs. " + d['rot_ant'] + "</div>"
        + "<div style='font-size:24px;font-weight:700;margin-top:2px;line-height:1.05;color:" + d['cor_var'] + "'>"
        + d['seta_var'] + " " + d['var_mes'] + "</div>"
        + "<div style='font-size:10.5px;color:" + SEC + "'>volume anterior " + d['ant'] + "</div></div>"
        + "</div>")


def card_situacao(d):
    return RESET + (
        "<div style='" + FONTE + CARD + ";flex-direction:row;align-items:center;padding:0 22px;gap:16px'>"
        + "<div style='width:44px;height:44px;flex:none;border-radius:50%;border:2px solid " + d['cor']
        + ";color:" + d['cor'] + ";font-size:22px;font-weight:700;display:flex;align-items:center;"
        + "justify-content:center'>" + d['icone'] + "</div>"
        + "<div><div style='font-size:11px;color:" + SEC + "'>Situação</div>"
        + "<div style='font-size:22px;font-weight:700;line-height:1.2;color:" + d['cor'] + "'>" + d['texto'] + "</div>"
        + "<div style='font-size:10.5px;color:" + SEC + ";margin-top:2px'>Faixa esperada: "
        + d['faixa_min'] + " &#8211; " + d['faixa_max'] + " m&#179;/d</div></div></div>")


# ---------------------------------------------------------- resumo por cliente
def linha_resumo(L):
    return ("<tr style='border-top:1px solid " + TRILHO + "'>"
            + "<td style='padding:0 6px 0 14px;color:" + L['cor_nome'] + ";font-weight:" + L['peso'] + "'>"
            + L['nome'] + "</td>"
            + "<td style='text-align:right;padding:0 6px;color:#fff;font-weight:600;font-size:11.5px'>"
            + L['vol'] + "</td>"
            + "<td style='padding:0 8px'><div style='position:relative;height:9px;background:" + TRILHO
            + ";border-radius:5px'><div style='width:" + L['larg'] + "%;height:9px;background:" + L['cor']
            + ";border-radius:5px'></div>"
            + "<div style='position:absolute;left:77%;top:-3px;height:15px;border-left:1px dashed rgba(255,255,255,0.65)'></div>"
            + "</div></td>"
            + "<td style='text-align:right;padding:0 4px;font-weight:700;font-size:11px;color:" + L['cor'] + "'>"
            + L['pct'] + "</td>"
            + "<td style='padding:0 12px 0 2px;text-align:center'><span style='display:inline-block;"
            + "width:9px;height:9px;border-radius:50%;background:" + L['cor'] + "'></span></td></tr>")


def resumo(d, linhas):
    th = ("<th style='font-size:9.5px;color:" + SEC + ";font-weight:600;letter-spacing:0.3px;"
          "padding:5px 6px;text-align:")
    return RESET + (
        "<div style='" + FONTE + CARD + "'>"
        + cabecalho_painel('RESUMO POR CLIENTE', d['rot'])
        + "<div style='flex:1;min-height:0;display:flex;flex-direction:column'>"
        + "<table style='width:100%;height:100%;border-collapse:collapse;font-size:11px;table-layout:fixed'>"
        + "<colgroup><col style='width:168px'><col style='width:88px'><col style='width:160px'>"
        + "<col style='width:46px'><col style='width:30px'></colgroup>"
        + "<tr style='height:24px'>" + th + "left'>CLIENTE</th>" + th + "right'>ATUAL m&#179;/d</th>"
        + th + "left'>ATING. META</th><th></th><th></th></tr>"
        + linhas + "</table></div></div>")


# ------------------------------------------------------------ histórico mensal
def linha_historico(L):
    return ("<tr style='border-top:1px solid " + TRILHO + ";background:" + L['fundo'] + "'>"
            + "<td style='padding:0 8px 0 16px;color:" + L['cor_rot'] + "'>" + L['rot'] + "</td>"
            + "<td style='padding:0 8px'><div style='height:13px;background:" + TRILHO
            + ";border-radius:3px'><div style='width:" + L['larg'] + "%;height:13px;background:" + BARRA
            + ";border-radius:3px'></div></div></td>"
            + "<td style='padding:0 8px;text-align:right;color:#fff;font-weight:600'>" + L['vol'] + "</td>"
            + "<td style='padding:0 8px;text-align:right;color:#cfe4fa'>" + L['ls'] + "</td>"
            + "<td style='padding:0 8px;text-align:right;color:" + L['cor_dias'] + "'>" + L['dias'] + "</td>"
            + "<td style='padding:0 16px 0 8px;text-align:right;font-weight:600;color:" + L['cor_var'] + "'>"
            + L['var'] + "</td></tr>")


def historico(d, linhas):
    th = ("<th style='font-size:9.5px;color:" + SEC + ";font-weight:600;letter-spacing:0.3px;"
          "padding:5px 8px;text-align:")
    return RESET + (
        "<div style='" + FONTE + CARD + "'>"
        + cabecalho_painel('HISTÓRICO DE MEDIÇÃO &#8212; ' + d['cliente'], '13 meses')
        + "<div style='flex:1;min-height:0;display:flex;flex-direction:column'>"
        + "<table style='width:100%;height:100%;border-collapse:collapse;font-size:11px;table-layout:fixed'>"
        + "<colgroup><col style='width:78px'><col style='width:228px'><col style='width:104px'>"
        + "<col style='width:68px'><col style='width:56px'><col style='width:126px'></colgroup>"
        + "<tr style='height:24px'>"
        + th.replace('padding:5px 8px', 'padding:5px 8px 5px 16px') + "left'>REF/MÊS</th><th></th>"
        + th + "right'>VOLUME m&#179;/d</th>" + th + "right'>L/S</th>" + th + "right'>DIAS</th>"
        + th.replace('padding:5px 8px', 'padding:5px 16px 5px 8px') + "right'>VS. MÊS ANT.</th></tr>"
        + linhas + "</table></div>"
        + "<div style='padding:8px 16px;background:" + HEADBG + ";border-top:1px solid " + BORDA
        + ";display:flex;font-size:10.5px;color:" + SEC + "'>"
        + "<span>Média 13m <b style='color:#fff;font-size:12px'>" + d['media13'] + "</b> &#183; "
        + d['media13_ls'] + " L/s</span>"
        + "<span style='margin-left:auto'>Mín <b style='color:#fff'>" + d['min13'] + "</b> (" + d['min13_mes']
        + ") &nbsp;&#183;&nbsp; Máx <b style='color:#fff'>" + d['max13'] + "</b> (" + d['max13_mes']
        + ")</span></div></div>")


# ----------------------------------------------------------------- diagnóstico
def linha_diagnostico(L):
    sub = ("<div style='font-size:9.5px;color:" + TER + ";margin-top:1px'>" + L['sub'] + "</div>") if L.get('sub') else ''
    unid = ("<span style='font-size:10.5px;color:" + SEC + ";font-weight:400'> m&#179;/d</span>") if L.get('unidade', True) else ''
    return ("<tr style='border-bottom:1px solid " + TRILHO + "'>"
            + "<td style='padding:10px 16px;color:" + SEC + ";font-size:11px'>" + L['rotulo'] + sub + "</td>"
            + "<td style='padding:10px 10px;text-align:right;font-weight:700;font-size:18px;"
            + "white-space:nowrap;color:" + L.get('cor', BRANCO) + "'>" + L['valor'] + unid + "</td>"
            + "<td style='padding:10px 16px 10px 4px;text-align:right;color:" + SEC
            + ";font-size:10.5px;white-space:nowrap'>" + L.get('lado', '') + "</td></tr>")


def diagnostico(d, linhas):
    return RESET + (
        "<div style='" + FONTE + CARD + "'>"
        + cabecalho_painel('DIAGNÓSTICO &#8212; ' + d['cliente'], 'mês ref. vs histórico')
        + "<div style='flex:1;min-height:0;display:flex;flex-direction:column'>"
        + "<table style='width:100%;height:100%;border-collapse:collapse'>" + linhas + "</table></div>"
        + "<div style='margin:0 16px 16px 16px;padding:11px 13px;background:rgba(74,158,255,0.09);"
        + "border:1px solid #27527d;border-radius:8px;display:flex;gap:9px'>"
        + "<span style='color:" + AZUL + ";font-size:14px'>&#9432;</span>"
        + "<span style='font-size:11px;color:#b9d3ec;line-height:1.5'>O volume atual está "
        + "<b style='color:" + d['cor_desvio'] + "'>" + d['desvio_txt'] + "</b>"
        + " da média dos 12 meses anteriores e <b style='color:" + d['cor_faixa'] + "'>" + d['faixa_txt'] + "</b>"
        + " da faixa esperada para o período.</span></div></div>")


# --------------------------------------------- variação vs. mesmo mês ano ant.
LARG_SVG, ALT_SVG = 1848, 210
TOPO_R, BASE_R, NOMES_R = 22, 26, 26          # folgas: rótulo de cima, de baixo, nomes
ALTO_PLOT = ALT_SVG - TOPO_R - BASE_R - NOMES_R


def barra_variacao(B):
    return ("<rect x='" + B['x'] + "' y='" + B['y'] + "' width='" + B['w'] + "' height='" + B['h']
            + "' rx='3' fill='" + B['cor'] + "' fill-opacity='0.88'/>"
            + "<text x='" + B['cx'] + "' y='" + B['yr'] + "' fill='" + B['cor']
            + "' font-size='13' font-weight='700' text-anchor='middle'>" + B['pct'] + "</text>"
            + "<text x='" + B['cx'] + "' y='" + str(ALT_SVG - 6) + "' fill='" + SEC
            + "' font-size='12' text-anchor='middle'>" + B['nome'] + "</text>")


def variacao(d, barras):
    return RESET + (
        "<div style='" + FONTE + CARD + "'>"
        + cabecalho_painel('VARIAÇÃO VS. MESMO MÊS DO ANO ANTERIOR', d['contexto'])
        + "<div style='flex:1;min-height:0;padding:4px 12px 6px 12px'>"
        + "<svg viewBox='0 0 " + str(LARG_SVG) + " " + str(ALT_SVG)
        + "' style='width:100%;height:100%;display:block' font-family='Segoe UI,sans-serif'>"
        + "<line x1='8' y1='" + d['y0'] + "' x2='" + str(LARG_SVG - 8) + "' y2='" + d['y0']
        + "' stroke='#2a4d75' stroke-width='1'/>"
        + barras + "</svg></div></div>")
