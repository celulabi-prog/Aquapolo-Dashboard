# -*- coding: utf-8 -*-
"""Proposta D, regra final. Monta a tela so por "SE situacao ENTAO trecho", como o DAX fara.

    python gera_final.py          -> regrava a proposta D (dados de hoje) e as copias t*.dc.html desta pasta
    python gera_final.py hoje     -> so a proposta D

Parte de D-original.dc.html (copia congelada da D antes da correcao) e troca os trechos por numero de linha.
Os valores das copias t* sao ficticios: servem para provar que a regra cabe nos extremos.
"""
import pathlib, sys
AQUI = pathlib.Path(__file__).parent
BASE = AQUI / 'D-original.dc.html'
SAIDA = AQUI.parent.parent / 'canvas' / 'project' / 'D-Fluxo-Dinamico.dc.html'
VERDE = '#2b7d62'
COR = {'f': '#ff5c63', 'a': '#ffd257', 'd': '#57d68d'}
RGB = {'f': '255,92,99', 'a': '255,210,87'}
TINTA = {'f': '0.13', 'a': '0.08'}
CORTE = {'f': '#261a2c', 'a': '#1c2424'}
NOME_SIT = {'d': 'dentro', 'a': 'atenção', 'f': 'fora', 's': 'sem meta'}
r1 = lambda v: ('%.1f' % v).rstrip('0').rstrip('.')
ANEL = '<span style="width:14px;height:14px;flex:none;box-sizing:border-box;border-radius:50%;border:2px solid #a8bfd6"></span><span style="font-size:16px;color:#a8bfd6">sem meta</span>'

# ---------- medidor ----------
# kind: max = meta "<=" (p = % da meta) | min = meta ">=" (p = % da meta) | faixa (p = (valor - piso) / (teto - piso))
def medidor(kind, p, sit, aria, W=160):
    if sit == 's':
        return '<div style="width:%dpx;height:32px;flex:none;display:flex;align-items:center;gap:8px">%s</div>' % (W, ANEL)
    X = lambda v: 4 + (v - 4) * (W - 8) / 152.0
    bruto = 4 + 0.95 * p if kind != 'faixa' else 57.2 + 45.6 * p
    z0, z1 = {'max': (4, 99), 'min': (99, 156), 'faixa': (57.2, 102.8)}[kind]
    lims = [99] if kind != 'faixa' else [57.2, 102.8]
    x = X(max(4, min(156, bruto)))                      # o ponteiro nunca sai do trilho
    zona = lambda y, h: 'x="%s" y="%d" width="%s" height="%d" fill="%s"' % (r1(X(z0)), y, r1(X(z1) - X(z0)), h, VERDE)
    abre = lambda h: '<svg width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="%s" style="display:block;flex:none;overflow:visible">' % (W, h, W, h, aria)
    if sit == 'd':
        t = ''.join('M%s 12v14' % r1(X(l)) for l in lims)
        return (abre(32) + '<rect x="4" y="16" width="%d" height="6" fill="#143454"/><rect %s/><path d="%s" stroke="#f3f8fd" stroke-width="1.5"/><path d="M%s 3h10l-5 8z" fill="#f3f8fd"/><path d="M%s 10v16" stroke="#f3f8fd" stroke-width="2.5"/></svg>'
                % (W - 8, zona(16, 6), t, r1(x - 5), r1(x)))
    c = COR[sit]
    t = ''.join('M%s 8v20' % r1(X(l)) for l in lims)
    if bruto > 156:      # alem da escala para a direita
        L = X(lims[-1])
        return (abre(32) + '<rect x="4" y="13" width="%s" height="10" fill="#143454"/><rect %s/><rect x="%s" y="10" width="%s" height="16" fill="%s"/><path d="M%s 29l5-22M%s 29l5-22" stroke="%s" stroke-width="3.5"/><path d="%s" stroke="#f3f8fd" stroke-width="1.5"/><path d="M%s 4l14 14-14 14z" fill="%s"/></svg>'
                % (r1(X(144) - 4), zona(13, 10), r1(L), r1(X(145) - L), c, r1(L + 14), r1(L + 23), CORTE[sit], t, r1(X(144)), c))
    if bruto < 4:        # alem da escala para a esquerda (so acontece em faixa)
        L = X(lims[0])
        return (abre(32) + '<rect x="16" y="13" width="%s" height="10" fill="#143454"/><rect %s/><rect x="15" y="10" width="%s" height="16" fill="%s"/><path d="M%s 29l-5-22M%s 29l-5-22" stroke="%s" stroke-width="3.5"/><path d="%s" stroke="#f3f8fd" stroke-width="1.5"/><path d="M16 4l-14 14 14 14z" fill="%s"/></svg>'
                % (r1(X(156) - 16), zona(13, 10), r1(L - 15), c, r1(L - 14), r1(L - 23), CORTE[sit], t, c))
    if kind == 'max': a, b = X(99), x
    elif kind == 'min': a, b = x, X(99)
    elif bruto > 102.8: a, b = X(102.8), x
    else: a, b = x, X(57.2)
    if sit == 'a':
        t = ''.join('M%s 7v16' % r1(X(l)) for l in lims)
        return (abre(26) + '<rect x="4" y="11" width="%d" height="8" fill="#143454"/><rect %s/><rect x="%s" y="11" width="%s" height="8" fill="%s"/><path d="%s" stroke="#f3f8fd" stroke-width="1.5"/><path d="M%s 0h12l-6 9z" fill="%s"/><path d="M%s 7v16" stroke="%s" stroke-width="3"/></svg>'
                % (W - 8, zona(11, 8), r1(a), r1(b - a), c, t, r1(x - 6), c, r1(x), c))
    return (abre(32) + '<rect x="4" y="13" width="%d" height="10" fill="#143454"/><rect %s/><rect x="%s" y="13" width="%s" height="10" fill="%s"/><path d="%s" stroke="#f3f8fd" stroke-width="1.5"/><path d="M%s 0h14l-7 11z" fill="%s"/><path d="M%s 9v19" stroke="%s" stroke-width="3.5"/></svg>'
            % (W - 8, zona(13, 10), r1(a), r1(b - a), c, t, r1(x - 7), c, r1(x), c))

# ---------- minigrafico das linhas em destaque (forma ilustrativa, sem numeros) ----------
FORMAS = {
 'pouco': ('<rect x="0" y="28" width="160" height="26" fill="rgba(87,214,141,0.20)"/>', 'M0 28H160M0 54H160', 28, 'pouco acima da faixa da meta',
           '4,18 14.1,18 24.3,17 34.4,23 44.5,22 54.7,18 64.8,19 74.9,15 85.1,19 95.2,24 105.3,19 115.5,18 125.6,17 135.7,17 145.9,23 156,20'),
 'abaixo': ('<rect x="0" y="8" width="160" height="24" fill="rgba(87,214,141,0.20)"/>', 'M0 8H160M0 32H160', 32, 'abaixo da faixa da meta',
            '4,47 14.1,48 24.3,49 34.4,50 44.5,45 54.7,45 64.8,48 74.9,48 85.1,51 95.2,47 105.3,44 115.5,47 125.6,48 135.7,49 145.9,50 156,45'),
 'acima': ('<rect x="0" y="51" width="160" height="9" fill="rgba(87,214,141,0.20)"/>', 'M0 51H160', 51, 'acima do teto da meta',
           '4,22 14.1,24 24.3,19 34.4,12 44.5,18 54.7,23 64.8,25 74.9,20 85.1,10 95.2,17 105.3,22 115.5,24 125.6,12 135.7,19 145.9,15 156,17'),
}
def mini(sit, forma):
    zona, lim, y, fala, pts = FORMAS[forma]
    area = 'M4 %d' % y + ''.join('L' + p.replace(',', ' ') for p in pts.split()) + 'L156 %dZ' % y
    return ('<svg viewBox="0 0 160 60" preserveAspectRatio="none" role="img" aria-label="Tendência no período, %s" style="display:block;flex:1 1 0;min-height:0;max-height:56px;width:160px">%s<path d="%s" fill="rgba(%s,0.28)"/><path d="%s" stroke="#57d68d" stroke-width="1.5" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/><polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>'
            % (fala, zona, area, RGB[sit], lim, pts, COR[sit]))

# ---------- frase do desvio: (quantidade, referencia); extremo = 2 vezes o teto ou metade do piso ----------
ETIQUETA = 'margin:0 -6px;padding:0 6px;background:#ff5c63;border-radius:2px;color:#1c0508'
def frase(desvio, sit, extremo, fonte, duas):
    q, ref = desvio
    txt = '<div>%s</div><div>%s</div>' % (q, ref) if duas else '%s %s' % (q, ref)
    return '<div style="font-size:%dpx;font-weight:700;line-height:%dpx;%s">%s</div>' % (fonte[0], fonte[1], ETIQUETA if (extremo and sit == 'f') else 'color:' + COR[sit], txt)

# ---------- linha de indicador ----------
COMUM = 'box-sizing:border-box;display:grid;grid-template-columns:minmax(0,1fr) auto 160px;column-gap:14px;align-items:center;padding:0 14px 0 12px;border-top:1px solid #11304c;'
TEXTO = 'display:flex;flex-direction:column;align-items:flex-start;white-space:nowrap'
# linha = (nome, unidade·meta, valor, situacao, desvio, tipo, p, forma, extremo)
def linha(estreito, sem_mini, nome, um, valor, sit, desvio, kind, p, forma=None, extremo=None):
    if extremo is None:
        extremo = (kind == 'max' and p >= 200) or (kind == 'min' and p <= 50)
    if sit in 'ds':
        aria = 'Sem meta' if sit == 's' else ('Dentro da faixa' if kind == 'faixa' else '%d%% da meta, dentro' % p)
        return ('<div style="flex:1 1 0;min-height:50px;%sborder-left:6px solid transparent">\n<div style="white-space:nowrap">\n<div style="font-size:19px;font-weight:600;line-height:24px">%s</div>\n<div style="font-size:16px;line-height:20px;color:#a8bfd6">%s</div></div>\n<div style="font-size:34px;font-weight:700;line-height:38px;text-align:right">%s</div>%s</div>'
                % (COMUM, nome, um, valor, medidor(kind, p, sit, aria)))
    f = sit == 'f'
    c = COR[sit]
    forma = forma or ('pouco' if sit == 'a' else 'acima')
    aria = '%s %s, %s' % (desvio[0], desvio[1], NOME_SIT[sit])
    col3 = ('<div style="%salign-self:stretch;min-height:0;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;gap:%dpx;padding:5px 0">%s%s</div>'
            % ('grid-row:1 / 3;grid-column:3;' if estreito else '', 4 if f else 3, '' if sem_mini else mini(sit, forma), medidor(kind, p, sit, aria)))
    fundo = 'border-left:6px solid %s;background:rgba(%s,%s)' % (c, RGB[sit], TINTA[sit])
    um_ = '<div style="font-size:16px;line-height:20px;color:#a8bfd6">%s</div>' % um
    val = 'font-size:%dpx;font-weight:700;line-height:%dpx;%stext-align:right;color:%s' % (((56, 60, 'letter-spacing:-1px;') if f else (44, 48, '')) + (c,))
    if not estreito:     # bloco largo (TMBR): texto e valor lado a lado, frase em uma linha
        return ('<div style="flex:%s 1 0;min-height:%dpx;%s%s">\n<div style="%s">\n<div style="font-size:%dpx;font-weight:700;line-height:%dpx">%s</div>\n%s\n%s</div>\n<div style="%s">%s</div>\n%s</div>'
                % ('2' if f else '1.5', 72 if f else 70, COMUM, fundo, TEXTO, 22 if f else 20, 26 if f else 24, nome, um_,
                   frase(desvio, sit, extremo, (20, 24) if f else (17, 20), False), val, valor, col3))
    val = val.replace('font-size:56px', 'font-size:52px').replace('line-height:60px', 'line-height:56px')
    return ('<div style="flex:%s 1 0;min-height:%dpx;%sgrid-template-rows:auto auto;align-content:center;%s">\n<div style="grid-row:1;grid-column:1 / 3;font-size:%dpx;font-weight:700;line-height:24px;white-space:nowrap">%s</div>\n%s\n<div style="grid-row:2;grid-column:1;%s">\n%s\n%s</div>\n<div style="grid-row:2;grid-column:2;%s">%s</div></div>'
            % ('2' if f else '1.5', 88 if f else 86, COMUM, fundo, 22 if f else 20, nome, col3, TEXTO, um_,
               frase(desvio, sit, extremo, (18, 20) if f else (16, 18), True), val, valor))

# ---------- bloco de etapa (moldura + cabecalho + linhas) ----------
def bloco(linhas, estreito):
    sits = [l[3] for l in linhas]
    nf, na, T = sits.count('f'), sits.count('a'), len(sits) - sits.count('s')
    borda = '#ff5c63' if nf else ('#ffd257' if na else '#1f4263')
    fundo = '#2a1524' if nf else '#0a2137'
    if nf or na:         # o cabecalho so diz o que esta errado; o resto a fita mostra
        v = ''
        if nf: v += '<span style="font-size:28px;font-weight:700;color:#ff5c63">%d fora da meta</span>' % nf
        if na: v += '<span style="font-size:%dpx;font-weight:700;color:#ffd257">%d em atenção</span>' % (24 if nf else 28, na)
        v = '<div style="display:flex;align-items:baseline;gap:14px;white-space:nowrap;line-height:36px">%s</div>' % v
    else:
        v = '<div style="display:flex;align-items:baseline;gap:10px;white-space:nowrap;line-height:36px"><span style="font-size:28px;font-weight:700">%d de %d</span><span style="font-size:24px;color:#d3e1ef">dentro da meta</span></div>' % (T, T)
    seg = {'d': ('6px', VERDE), 'a': ('10px', '#ffd257'), 'f': ('14px', '#ff5c63'), 's': ('6px', '#5f88b0')}
    fita = ''.join('<span style="flex:1;height:%s;background:%s"></span>' % seg[s] for s in sits)
    aria = '%d indicadores na ordem das linhas: %s' % (len(sits), ', '.join(NOME_SIT[s] for s in sits))
    sem_mini = len(sits) >= 6 and nf + na >= 5
    return ('<div style="box-sizing:border-box;display:flex;flex-direction:column;background:#041729;border:2px solid %s;border-radius:3px">\n'
            '<div style="height:78px;flex:none;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;padding:8px 14px 12px;background:%s">\n%s\n'
            '<div role="img" aria-label="%s" style="height:14px;display:flex;align-items:flex-end;gap:4px">%s</div></div>\n'
            '<div style="flex:1;min-height:0;display:flex;flex-direction:column">\n%s</div></div>'
            % (borda, fundo, v, aria, fita, '\n'.join(linha(estreito, sem_mini, *l) for l in linhas)))

# ---------- cartao de utilidade ----------
SETA = {'+': 'M8 13.5V2.5M3 7.5l5-5 5 5', '-': 'M8 2.5v11M3 8.5l5 5 5-5'}
MINI_C = {
 'pouco': ('<rect x="0" y="15" width="64" height="11" fill="rgba(87,214,141,0.20)"/><path d="M0 15h64"', 'pouco acima da linha da meta',
           '3,12.5 6.8,11.7 10.6,12.1 14.4,10.6 18.2,8.4 22,11.4 25.8,12.1 29.6,11.8 33.4,12 37.2,8.9 41,9.6 44.8,12.2 48.6,11.6 52.4,12.5 56.2,10.5 60,8.5'),
 'acima': ('<rect x="0" y="18" width="64" height="8" fill="rgba(87,214,141,0.20)"/><path d="M0 18h64"', 'acima da linha da meta',
           '3,7.8 6.8,7.4 10.6,10 14.4,9.8 18.2,11.6 22,10 25.8,6.7 29.6,9 33.4,9.7 37.2,10.7 41,11.7 44.8,7.8 48.6,7.7 52.4,9.6 56.2,9.6 60,6'),
}
# cartao = (nome, unidade·meta, valor, situacao, % da meta, desvio, variacao, rotulo, sufixo, largura do medidor)
def cartao(nome, um, valor, sit, pct, desvio, var, rot, sufixo='', W=160):
    vari = ('<div style="display:flex;align-items:center;gap:6px;white-space:nowrap"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#f3f8fd" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex:none"><path d="%s"/></svg><span style="font-size:18px;font-weight:700;line-height:24px">%s</span><span style="font-size:16px;line-height:24px;color:#a8bfd6;margin-left:2px">%s</span></div>'
            % (SETA[var[0]], var, rot))
    g = medidor('max', pct, sit, '%d%% da meta, %s' % (pct, NOME_SIT[sit]), W)
    suf = '<span style="font-size:22px;color:#a8bfd6">%s</span>' % sufixo if sufixo else ''
    if sit == 'd':
        return ('<div style="flex:1;min-width:0;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;padding:8px 12px;background:#041729;border:1px solid #1f4263;border-left:6px solid #1f4263;border-radius:3px">\n<div>\n<div style="height:26px;display:flex;align-items:center;white-space:nowrap"><span style="font-size:19px;font-weight:600;line-height:24px">%s</span></div>\n<div style="font-size:16px;line-height:20px;color:#a8bfd6;white-space:nowrap">%s</div></div>\n'
                '<div style="height:48px;display:flex;align-items:center;justify-content:space-between;white-space:nowrap">\n<div style="display:flex;align-items:baseline;gap:6px"><span style="font-size:38px;font-weight:700;line-height:48px">%s</span>%s</div>\n<div style="text-align:right">\n<div style="font-size:22px;font-weight:700;line-height:24px">%d%%</div>\n<div style="font-size:16px;line-height:20px;color:#a8bfd6">da meta</div></div></div>%s\n%s</div>'
                % (nome, um, valor, suf, pct, g, vari))
    c = COR[sit]
    zona, fala, pts = MINI_C['pouco' if sit == 'a' else 'acima']
    mc = '<svg width="64" height="26" viewBox="0 0 64 26" role="img" aria-label="Tendência no período, %s" style="display:block;flex:none">%s stroke="#57d68d" stroke-width="1.5" stroke-dasharray="4 3"/><polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>' % (fala, zona, pts, c)
    return ('<div style="flex:1;min-width:0;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;padding:8px 12px;background:rgba(%s,%s);border:1px solid %s;border-left:6px solid %s;border-radius:3px">\n<div>\n<div style="height:26px;display:flex;align-items:center;justify-content:space-between;gap:8px;white-space:nowrap"><span style="font-size:19px;font-weight:700;line-height:24px">%s</span>%s</div>\n<div style="font-size:16px;line-height:20px;color:#a8bfd6;white-space:nowrap">%s</div></div>\n'
            '<div style="height:48px;display:flex;align-items:center;justify-content:space-between;white-space:nowrap">\n<div style="display:flex;align-items:baseline;gap:6px"><span style="font-size:40px;font-weight:700;line-height:48px;color:%s">%s</span>%s</div>\n<div style="text-align:right">%s</div></div>%s\n%s</div>'
            % (RGB[sit], TINTA[sit], c, c, nome, mc, um, c, valor, suf, frase(desvio, sit, pct >= 200, (18, 22), True), g, vari))

# ---------- entrega aos clientes (numero-heroi): mesmo tamanho e lugar, so a cor acompanha a situacao ----------
ICONE = {'d': '<span style="width:16px;height:16px;flex:none;border-radius:50%;background:#57d68d"></span>',
         'a': '<span style="width:0;height:0;flex:none;border-left:10px solid transparent;border-right:10px solid transparent;border-bottom:17px solid #ffd257"></span>',
         'f': '<span style="width:14px;height:14px;flex:none;background:#ff5c63;transform:rotate(45deg);margin:0 3px"></span>'}
SERIE = [46, 34, 56, 40, 52, 30, 44, 60, 38, 32, 54, 42, 28, 50, 36, 44]
def heroi(valor, pct, sit, var, rot):
    c = COR[sit]
    d = sit == 'd'
    x = 4 + 300 * max(0, min(160, pct)) / 160.0
    desce = 0 if d else 62            # ilustrativo: fora da meta a serie fica abaixo da linha da meta
    pts = [(6 + i * 296 / 15.0, y + desce) for i, y in enumerate(SERIE)]
    poli = ' '.join('%s,%s' % (r1(a), b) for a, b in pts)
    area = 'M6 160' + ''.join('L%s %s' % (r1(a), b) for a, b in pts) + 'L302 160Z'
    falta = '' if d else '<rect x="%s" y="15" width="%s" height="8" fill="%s"/>' % (r1(x), r1(191.5 - x), c)
    return ('<div style="box-sizing:border-box;display:flex;flex-direction:column;padding:6px 16px 10px;background:linear-gradient(180deg,#0b3157 0%%,#061d33 58%%);border:2px solid %s;border-radius:3px">\n'
            '<div style="display:flex;align-items:baseline;gap:6px;margin-left:-5px;white-space:nowrap"><span style="font-size:108px;font-weight:700;line-height:108px;letter-spacing:-3px%s">%s</span><span style="font-size:24px;font-weight:600;color:#7cc4f8">L/s</span></div>\n'
            '<div style="display:flex;align-items:center;gap:10px;margin-top:2px;white-space:nowrap">%s<span style="font-size:30px;font-weight:700;line-height:36px;color:%s">%d%% da meta</span><span style="flex:1"></span><span style="font-size:17px;color:#a8bfd6">≥ 311,9</span></div>'
            '<svg width="308" height="32" viewBox="0 0 308 32" role="img" aria-label="%d%% da meta, %s" style="display:block;flex:none;margin-top:6px"><rect x="4" y="15" width="300" height="8" fill="#143454"/><rect x="191.5" y="15" width="112.5" height="8" fill="%s"/>%s<path d="M191.5 10v18" stroke="#f3f8fd" stroke-width="1.5"/><path d="M%s 1h14l-7 10z" fill="%s"/><path d="M%s 9v19" stroke="%s" stroke-width="3"/></svg>'
            '<svg viewBox="0 0 308 160" preserveAspectRatio="none" role="img" aria-label="Tendência da entrega no período, %s da linha da meta" style="display:block;flex:1 1 0;min-height:0;width:308px;margin-top:10px"><defs><linearGradient id="d-hero-area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3aa7f2" stop-opacity="0.50"/><stop offset="1" stop-color="#3aa7f2" stop-opacity="0.08"/></linearGradient></defs><path d="%s" fill="url(#d-hero-area)"/><path d="M0 84H308" stroke="#57d68d" stroke-width="1.5" stroke-dasharray="7 6" vector-effect="non-scaling-stroke"/><polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/><path d="M302 %dh0.01" stroke="#f3f8fd" stroke-width="11" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>\n'
            '<div style="display:flex;justify-content:space-between;font-size:16px;line-height:22px;color:#a8bfd6"><span>03/11</span><span>tracejado = meta</span><span>18/11</span></div>\n'
            '<div style="margin-top:8px;border-top:1px solid #1f4263;padding-top:8px;display:flex;align-items:center;gap:8px;white-space:nowrap"><svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="#f3f8fd" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex:none"><path d="%s"/></svg><span style="font-size:26px;font-weight:700;line-height:32px">%s</span><span style="font-size:17px;line-height:32px;color:#a8bfd6;margin-left:2px">%s</span></div></div>'
            % ('#3aa7f2' if d else c, '' if d else ';color:' + c, valor, ICONE[sit], c, pct, pct, NOME_SIT[sit], VERDE, falta,
               r1(x - 7), '#f3f8fd' if d else c, r1(x), '#f3f8fd' if d else c, 'acima' if d else 'abaixo', area, poli, '#5cc0ff' if d else c, pts[-1][1], SETA[var[0]], var, rot))

# ---------- dados de hoje ----------
HOJE = {
 'eebc': [('Retrolavagens', 'ciclos · ≤ 12', '10', 'd', None, 'max', 83), ('DQO', 'mg/L · ≤ 100', '40', 'd', None, 'max', 40),
          ('NH3', 'mg/L · ≤ 20,0', '4,1', 'd', None, 'max', 21), ('Condutividade', 'µS/cm · ≤ 650', '356', 'd', None, 'max', 55),
          ('Dureza', 'mg/L · ≤ 100', '94', 'd', None, 'max', 94)],
 'tmbr': [('Idade do Lodo', 'dias · 18 a 22', '23', 'a', ('1 dia acima', 'da faixa'), 'faixa', 1.25),
          ('Alimento/Microorg.', 'g/g.d⁻¹ · 0,08 a 0,16', '0,05', 'f', ('38% abaixo', 'do piso'), 'faixa', -0.375, 'abaixo'),
          ('TMP', 'bar · ≤ 0,60', '0,14', 'd', None, 'max', 23), ('Permeabilidade', 'LMH/bar · ≥ 100', '114', 'd', None, 'min', 114),
          ('Turbidez', 'NTU · ≤ 0,40', '3,42', 'f', ('8,5 vezes', 'o teto'), 'max', 855), ('Fluxo', 'LMH · 17 a 24', '21,3', 'd', None, 'faixa', 0.614)],
 'or': [('SDI', '≤ 3,0', '1,8', 'd', None, 'max', 60), ('dP Skid 1', 'bar · ≤ 3,5', '1,9', 'd', None, 'max', 54),
        ('dP Skid 2', 'bar · ≤ 3,5', '1,6', 'd', None, 'max', 46), ('dP Skid 3', 'bar · ≤ 3,5', '2,5', 'd', None, 'max', 71)],
 'quimicos': ('Químicos', 'kg/m³ · ≤ 0,12', '0,13', 'a', 106, ('6% acima', 'do teto'), '-4,7%', 'melhorou'),
 'energia': ('Energia', 'kWh/m³ · ≤ 0,98', '0,91', 'd', 93, None, '-3,4%', 'melhorou'),
 'coagulante': ('Coagulante', 'gPAC/gP rem · ≤ 17,0', '20,8', 'f', 122, ('22% acima', 'do teto'), '+29,3%', 'piorou'),
 'energia_or': ('Energia OR', 'kWh/m³ · ≤ 0,50', '0,13', 'd', 25, None, '+4,1%', 'piorou'),
 'perdas': ('Perdas', '% · ≤ 18,0', '14,0', 'd', 78, None, '-0,1 p.p.', 'melhorou', '%', 308),
 'clientes': ('343,3', 110, 'd', '+13,8%', 'melhorou'),
}

# ---------- copias de teste (valores ficticios) ----------
def troca(lista, i, novo):
    l = list(lista); l[i] = novo; return l
T6 = [('Idade do Lodo', 'dias · 18 a 22', '9', 'f', ('9 dias abaixo', 'da faixa'), 'faixa', -2.25, 'abaixo', True),
      HOJE['tmbr'][1],
      ('TMP', 'bar · ≤ 0,60', '0,74', 'f', ('23% acima', 'do teto'), 'max', 123),
      ('Permeabilidade', 'LMH/bar · ≥ 100', '48', 'f', ('52% abaixo', 'do piso'), 'min', 48, 'abaixo'),
      ('Turbidez', 'NTU · ≤ 0,40', '12,40', 'f', ('31,0 vezes', 'o teto'), 'max', 3100),
      ('Fluxo', 'LMH · 17 a 24', '12,4', 'f', ('27% abaixo', 'do piso'), 'faixa', -0.657, 'abaixo')]
E5 = [('Retrolavagens', 'ciclos · ≤ 12', '19', 'f', ('58% acima', 'do teto'), 'max', 158),
      ('DQO', 'mg/L · ≤ 100', '148', 'f', ('48% acima', 'do teto'), 'max', 148),
      ('NH3', 'mg/L · ≤ 20,0', '27,5', 'f', ('38% acima', 'do teto'), 'max', 138),
      ('Condutividade', 'µS/cm · ≤ 650', '1.430', 'f', ('2,2 vezes', 'o teto'), 'max', 220),
      ('Dureza', 'mg/L · ≤ 100', '131', 'f', ('31% acima', 'do teto'), 'max', 131)]
O4 = [('SDI', '≤ 3,0', '4,2', 'f', ('40% acima', 'do teto'), 'max', 140),
      ('dP Skid 1', 'bar · ≤ 3,5', '10,5', 'f', ('3,0 vezes', 'o teto'), 'max', 300),
      ('dP Skid 2', 'bar · ≤ 3,5', '4,4', 'f', ('26% acima', 'do teto'), 'max', 126),
      ('dP Skid 3', 'bar · ≤ 3,5', '5,1', 'f', ('46% acima', 'do teto'), 'max', 146)]
UT = dict(
    quimicos=('Químicos', 'kg/m³ · ≤ 0,12', '0,15', 'f', 125, ('25% acima', 'do teto'), '+15,4%', 'piorou'),
    energia=('Energia', 'kWh/m³ · ≤ 0,98', '1,21', 'f', 123, ('23% acima', 'do teto'), '+18,6%', 'piorou'),
    energia_or=('Energia OR', 'kWh/m³ · ≤ 0,50', '1,10', 'f', 220, ('2,2 vezes', 'o teto'), '+124,5%', 'piorou'),
    perdas=('Perdas', '% · ≤ 18,0', '22,4', 'f', 124, ('24% acima', 'do teto'), '+8,3 p.p.', 'piorou', '%', 308))
CALMO = dict(HOJE,
    tmbr=[('Idade do Lodo', 'dias · 18 a 22', '20', 'd', None, 'faixa', 0.5), ('Alimento/Microorg.', 'g/g.d⁻¹ · 0,08 a 0,16', '0,12', 'd', None, 'faixa', 0.5),
          HOJE['tmbr'][2], ('Permeabilidade', 'LMH/bar · ≥ 100', '180', 'd', None, 'min', 180), ('Turbidez', 'NTU · ≤ 0,40', '0,21', 'd', None, 'max', 53), HOJE['tmbr'][5]],
    quimicos=('Químicos', 'kg/m³ · ≤ 0,12', '0,11', 'd', 92, None, '-4,7%', 'melhorou'),
    coagulante=('Coagulante', 'gPAC/gP rem · ≤ 17,0', '15,2', 'd', 89, None, '-6,2%', 'melhorou'))
CASOS = {
 't1-tmbr-6-fora': dict(HOJE, tmbr=T6,
    eebc=troca(HOJE['eebc'], 3, E5[3]),
    **{'or': troca(HOJE['or'], 2, ('dP Skid 2', 'bar · ≤ 3,5', '3,7', 'a', ('6% acima', 'do teto'), 'max', 106))}),
 't2-pior-mistura': dict(HOJE, **UT,
    eebc=troca(E5, 2, ('NH3', 'mg/L · ≤ 20,0', '21,6', 'a', ('8% acima', 'do teto'), 'max', 108)),
    tmbr=troca(T6, 0, HOJE['tmbr'][0]),
    clientes=('274,5', 88, 'f', '-9,1%', 'piorou'),
    **{'or': troca(troca(O4, 0, ('SDI', '≤ 3,0', '3,2', 'a', ('7% acima', 'do teto'), 'max', 107)), 2, ('dP Skid 2', 'bar · ≤ 3,5', '3,7', 'a', ('6% acima', 'do teto'), 'max', 106))}),
 't3-tudo-fora': dict(HOJE, **UT, eebc=E5, tmbr=T6, clientes=('274,5', 88, 'f', '-9,1%', 'piorou'), **{'or': O4}),
 't4-calmo': dict(CALMO, **{'or': troca(HOJE['or'], 0, ('SDI', 'sem meta', '1,8', 's', None, 'max', 0))}),
 't5-um-destaque': dict(CALMO,
    tmbr=troca(CALMO['tmbr'], 4, HOJE['tmbr'][4]),
    eebc=troca(HOJE['eebc'], 4, ('Dureza', 'mg/L · ≤ 100', '104', 'a', ('4% acima', 'do teto'), 'max', 104)),
    clientes=('296,3', 95, 'a', '-2,0%', 'piorou'),
    **{'or': troca(HOJE['or'], 3, ('dP Skid 3', 'bar · ≤ 3,5', '4,6', 'f', ('31% acima', 'do teto'), 'max', 131))}),
 't6-tmbr-4-destaques': dict(HOJE, tmbr=[HOJE['tmbr'][0], T6[1], HOJE['tmbr'][2], T6[3], T6[4], HOJE['tmbr'][5]]),
}

def no(L, n, k, fora, fundo='#041729'):
    ln = L[n - 1]
    for b, f in (('#ff5c63', '#1d1626'), ('#3aa7f2', fundo)):
        ln = ln.replace('border:2px solid %s;border-radius:3px;background:%s' % (b, f), 'border:2px solid @B;border-radius:3px;background:@F')
        ln = ln.replace('fill="none" stroke="%s"' % b, 'fill="none" stroke="@B"')
    assert '@B' in ln and '@F' in ln, n
    L[n - 1] = ln.replace('@B', '#ff5c63' if fora else '#3aa7f2').replace('@F', '#1d1626' if fora else fundo)
    lc = L[k - 1]
    for c in ('#ff5c63', '#2a77b0', '#3aa7f2'):
        lc = lc.replace('width:2px;background:' + c, 'width:2px;background:@C')
    assert '@C' in lc, k
    L[k - 1] = lc.replace('@C', '#ff5c63' if fora else ('#3aa7f2' if fundo == '#0a2a47' else '#2a77b0'))

def gera(destino, c):
    L = BASE.read_text(encoding='utf-8').split('\n')
    def sub(a, b, novo):           # linhas a..b (1-based, inclusive); mantem a numeracao
        L[a - 1:b] = [novo] + [''] * (b - a)
    def tr(n, velho, novo):        # troca obrigatoria numa linha
        assert velho in L[n - 1], (n, velho)
        L[n - 1] = L[n - 1].replace(velho, novo)
    cards = [c[k] for k in ('quimicos', 'energia', 'coagulante', 'energia_or', 'perdas')]
    todos = [l[3] for k in ('eebc', 'tmbr', 'or') for l in c[k]] + [k[3] for k in cards] + [c['clientes'][2], 's', 's']  # + Blend e Energia - Biologico
    # legenda
    tr(300, 'Fora da meta, a linha cresce no próprio lugar · a ordem nunca muda', 'Fora ou em atenção: a linha cresce · a ordem não muda')
    tr(302, 'Faixa verde = meta · ponteiro = valor', 'Faixa verde e tracejado = meta · ponteiro = valor')
    # utilidades
    sub(283, 292, cartao(*c['perdas']) + '</div></div></div>')
    sub(262, 270, cartao(*c['energia_or']))
    sub(241, 249, cartao(*c['coagulante']))
    sub(227, 235, cartao(*c['energia']) + '</div></div>')
    sub(218, 226, cartao(*c['quimicos']))
    # entrega
    sub(199, 203, heroi(*c['clientes']))
    # etapas
    sub(172, 196, bloco(c['or'], True))
    sub(129, 169, bloco(c['tmbr'], False))
    sub(97, 126, bloco(c['eebc'], True))
    # trem: no e ligacao vermelhos so quando a etapa tem indicador fora
    for n, k, key in ((53, 56, 'eebc'), (65, 68, 'tmbr'), (80, 84, 'or')):
        no(L, n, k, any(l[3] == 'f' for l in c[key]))
    no(L, 93, 95, c['clientes'][2] == 'f', '#0a2a47')
    # tubulacao: mesma espessura no desvio e no trecho da OR (o modelo nao tem vazao entre etapas)
    tr(74, 'border:6px solid #3aa7f2', 'border:4px solid #3aa7f2')
    tr(79, 'height:3px', 'height:4px')
    tr(81, 'height:3px', 'height:4px')
    # contagens da faixa de situacao; contagem zero perde a cor de alerta
    for i, s, cor, velho in ((43, 'f', '#ff5c63', '>3<'), (44, 'a', '#ffd257', '>2<'), (45, 'd', None, '>16<'), (46, 's', None, '>2<')):
        n = todos.count(s)
        tr(i, velho, '>%d<' % n)
        if n == 0 and s != 's':     # contagem zero: numero e icone apagados
            L[i - 1] = L[i - 1].replace(cor or '#57d68d', '#5f88b0').replace('line-height:44px"', 'line-height:44px;color:#5f88b0"').replace('font-size:20px;font-weight:600', 'font-size:20px;font-weight:600;color:#a8bfd6')
    assert len(todos) == 23
    txt = '\n'.join(l for l in L)
    assert txt.count('#379a78') > 0
    txt = txt.replace('#379a78', VERDE)
    # tira as linhas vazias deixadas pelas trocas (so dentro do miolo; as linhas em branco originais ficam)
    while '\n\n\n' in txt:
        txt = txt.replace('\n\n\n', '\n\n')
    for proibido in ('{{', 'class=', '<iframe'):
        assert proibido not in txt, proibido
    destino.write_text(txt, encoding='utf-8')
    print(destino.name, '| fora', todos.count('f'), 'atencao', todos.count('a'), 'dentro', todos.count('d'), 'sem meta', todos.count('s'))

if __name__ == '__main__':
    alvo = sys.argv[1] if len(sys.argv) > 1 else ''
    if alvo in ('', 'hoje'):
        gera(SAIDA, HOJE)
    for nome, c in CASOS.items():
        if alvo == '' or alvo in nome:
            gera(AQUI / (nome + '.dc.html'), c)
