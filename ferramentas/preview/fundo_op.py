# -*- coding: utf-8 -*-
"""Monta o PNG de fundo da página Painel Operacional.

Da página inteira, só o cabeçalho é imagem: ele traz a foto aérea da planta e
os logos GS Inima / Sabesp, que são arte, não dado. Todo o resto é desenhado
pelos visuais HTML, a partir da base.

A faixa do cabeçalho fica guardada em `cabecalho_painel.png` (1920x156). Se o
print de referência estiver na pasta (`referencia_painel.png`, 1600x900, fora
do git por ser grande), a faixa é recortada dele de novo e regravada.
"""
import pathlib
from PIL import Image
from estilo_op import PAG, LARG_PAG, ALT_PAG, H_CAB

AQUI = pathlib.Path(__file__).parent
REF = AQUI / 'referencia_painel.png'      # print de referência (opcional)
FAIXA = AQUI / 'cabecalho_painel.png'     # a faixa já recortada (esta vai pro git)

REPO = pathlib.Path(r'C:\Users\Iza\Documents\dashboard aquapolo claude')
SAIDA = REPO / 'fundo_painel_operacional.png'
# o Power BI lê a imagem daqui; a da raiz é a cópia legível do repositório
RECURSO = (REPO / 'Dashboard - Aquapolo.Report' / 'StaticResources' / 'RegisteredResources'
           / 'fundo_painel_operacional3936334463390476.png')

CORTE = 130       # altura do cabeçalho no print de 1600x900


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def faixa():
    """A faixa do cabeçalho em 1920xH_CAB, recortada do print se ele existir."""
    if REF.exists():
        ref = Image.open(REF).convert('RGB')
        f = ref.crop((0, 0, ref.width, CORTE)).resize((LARG_PAG, H_CAB), Image.LANCZOS)
        f.save(FAIXA)
        return f
    if not FAIXA.exists():
        raise SystemExit('falta %s (ou o print %s para recortá-la)' % (FAIXA.name, REF.name))
    return Image.open(FAIXA).convert('RGB').resize((LARG_PAG, H_CAB), Image.LANCZOS)


def montar():
    pag = Image.new('RGB', (LARG_PAG, ALT_PAG), rgb(PAG))
    pag.paste(faixa(), (0, 0))
    pag.save(SAIDA)
    RECURSO.parent.mkdir(parents=True, exist_ok=True)
    pag.save(RECURSO)
    return SAIDA


if __name__ == '__main__':
    p = montar()
    print('ESCRITO:', FAIXA)
    print('ESCRITO:', p, Image.open(p).size)
    print('ESCRITO:', RECURSO)
