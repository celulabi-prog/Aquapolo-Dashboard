# -*- coding: utf-8 -*-
"""Confere as medidas 'HTML v2 ...' contra o HTML que o prep_v2 monta em Python.

Não lê a planilha: pede ao motor do Power BI os dados da tabela 'Dados BI' e o
texto de cada medida, e refaz a página em Python com esses mesmos dados. Assim a
conferência vale mesmo com a unidade G: fora do ar.

    python confere_v2.py consultas q.dax    # grava as consultas DAX, separadas por "-----"
    (rodar cada consulta no motor e gravar a resposta da consulta N em q.dax.N.out,
     colunas separadas por tabulação, números e datas no formato invariante)
    python confere_v2.py comparar q.dax     # compara e diz onde cada medida difere

Cada medida é conferida em cinco períodos: Mensal, Semanal, Diário, Trimestral e
Datas exatas. Só o travessão difere de propósito (— no Python, &#8212; no DAX).
"""
import io, re, sys
import pandas as pd
import indicadores_op as IX
import dados_op
import prep_v2 as P
import gerar_v2 as GV

EXATAS = ('2026-11-03', '2026-11-18')
MODOS = [('mensal', None), ('semanal', 7), ('diario', 1), ('trimestral', 90), ('exatas', 0)]
CHAVES = [d['chave'] for d in GV.MEDIDAS]
DADOS = ("EVALUATE SELECTCOLUMNS ( 'Dados BI', \"d\", 'Dados BI'[Data], \"i\", 'Dados BI'[Indicador], "
         "\"v\", 'Dados BI'[Valor] )")
DATAS = ("EVALUATE ROW ( \"plan\", MAX ( 'Dados BI'[Planilha salva em] ), \"bi\", MAX ( 'Dados BI'[Carregado em] ), "
         "\"agora\", UTCNOW () - 3 / 24 )")


def consulta(chave, dias):
    m = 'ROW ( "h", [%s] )' % GV.NOME[chave]
    if dias is None:
        return 'EVALUATE ' + m
    if dias:
        return "EVALUATE CALCULATETABLE ( %s, 'Período Painel'[Dias] = %d )" % (m, dias)
    return ("EVALUATE CALCULATETABLE ( %s, 'Período Painel'[Dias] = 0, 'Datas Painel'[Data] >= DATE ( %s ), "
            "'Datas Painel'[Data] <= DATE ( %s ) )" % ((m,) + tuple(d.replace('-0', '-').replace('-', ', ') for d in EXATAS)))


def consultas():
    return [DADOS, DATAS] + [consulta(k, dias) for _, dias in MODOS for k in CHAVES]


def le(arq, n):
    return io.open('%s.%d.out' % (arq, n), encoding='utf-8').read()


def normal(h):
    """O que pode diferir sem ser erro: o travessão e a última casa de uma coordenada."""
    return h.replace(u'—', '&#8212;').strip()


def perto(a, b, folga=0.11):
    """Iguais, a menos de 0,1 em números com uma casa (coordenadas de SVG)."""
    if a == b:
        return True
    pa, pb = re.split(r'(-?\d+\.\d)', a), re.split(r'(-?\d+\.\d)', b)
    if len(pa) != len(pb):
        return False
    for x, y in zip(pa, pb):
        if x != y:
            try:
                if abs(float(x) - float(y)) > folga:
                    return False
            except ValueError:
                return False
    return True


def comparar(arq):
    linhas = [l.split('\t') for l in le(arq, 0).splitlines() if l.strip()]
    longa = pd.DataFrame(linhas, columns=['Data', 'Indicador', 'Valor'])
    longa = longa.assign(Data=pd.to_datetime(longa['Data']), Valor=longa['Valor'].astype(float))
    plan, bi, agora = [pd.to_datetime(v) for v in le(arq, 1).strip().split('\t')]
    hoje = agora.normalize()
    dados_op.ler = lambda arquivo=None: longa
    ruins = 0
    for m, (modo, dias) in enumerate(MODOS):
        if dias == 0:
            c = dados_op.calcular(hoje, de=EXATAS[0], ate=EXATAS[1])
        else:
            c = dados_op.calcular(hoje, dias)
        S = P.series(c, longa, hoje)
        atraso = None if pd.isna(c['ult']) else (hoje - c['ult'].normalize()).days
        nivel = (0 if atraso is None else 1 if atraso <= IX.ATRASO_EM_DIA else 2 if atraso <= IX.ATRASO_PENDENTE else 3)
        falta = ('nada' if nivel == 1 else 'bi' if bi.normalize() < hoje else 'planilha' if plan.normalize() < hoje else 'origem')
        a = {'nivel': nivel, 'atraso': atraso, 'dados': c['ult'], 'plan': plan, 'bi': bi, 'falta': falta}
        py = P.paineis(c, S, a)
        n = P.contagem(c)
        print('%-10s fora %d, atenção %d, dentro %d, sem meta %d' % (modo, n['f'], n['a'], n['d'], n['s']))
        for i, k in enumerate(CHAVES):
            dax = normal(le(arq, 2 + m * len(CHAVES) + i))
            esp = normal(py[k])
            if dax == esp:
                continue
            if perto(dax, esp):
                print('   %-11s igual, com diferença de 0,1 em coordenada' % k)
                continue
            ruins += 1
            j = next((x for x in range(min(len(dax), len(esp))) if dax[x] != esp[x]), min(len(dax), len(esp)))
            print('   %-11s DIFERE no caractere %d (DAX %d, Python %d)' % (k, j, len(dax), len(esp)))
            print('      DAX   : ...' + dax[max(0, j - 90):j + 110].replace('\n', ' '))
            print('      Python: ...' + esp[max(0, j - 90):j + 110].replace('\n', ' '))
    print('TUDO IGUAL' if not ruins else '%d medida(s) diferem' % ruins)
    return ruins


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'consultas':
        io.open(sys.argv[2], 'w', encoding='utf-8').write('\n-----\n'.join(consultas()))
        print(len(consultas()), 'consultas em', sys.argv[2])
    else:
        sys.exit(1 if comparar(sys.argv[2]) else 0)
