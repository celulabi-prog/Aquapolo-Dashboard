# Geradores das páginas Painel Operacional e Volumes

O HTML dos painéis é escrito **uma vez só**, num molde. O mesmo molde serve a dois usos:

| | entrada | saída |
| --- | --- | --- |
| `preview*.py` | números reais da base | um PNG de 1920×1080 com a página renderizada |
| `gerar*.py` | pedaços de DAX | as medidas do Power BI (`.tmdl`) |
| `pagina*.py` | as posições de `estilo*.py` | os visuais da página (PBIR) |

Como o molde é o mesmo, **o que aparece no preview é o que o Power BI desenha**. Dá para
ajustar espaçamento, cor e tipografia olhando a imagem, sem abrir o Power BI a cada tentativa.

## Instalação

```
pip install pandas pyarrow playwright pillow
python -m playwright install chromium
```

## Painel Operacional (página Visão Geral)

```
python preview_op.py     # gera preview_op.png — olhe antes de gerar o resto
python fundo_op.py       # refaz o PNG de fundo (a faixa do cabeçalho)
python gerar_op.py       # reescreve Medidas HTML.tmdl
python pagina_op.py      # reescreve os visuais da página Visão Geral
python dados_op.py       # só imprime os números, sem desenhar nada
python dados_op.py 2026-09-14    # idem, como o painel estaria nesse dia
python dados_op.py 2026-09-14 7  # idem, com o seletor Período em Semanal (7 dias)
```

A página lê a planilha `G:\OME\Operacao\BI\Dados BI.xlsx` (só leitura). No Power BI ela entra
pela tabela **Dados BI**; aqui, por `dados_op.ler()`, que faz a mesma arrumação.

| Arquivo | Papel |
| --- | --- |
| `estilo_op.py` | paleta e grade da página — medidas tiradas do print de referência |
| `indicadores_op.py` | **os 23 indicadores**: nome, unidade, ícone, coluna da planilha, meta, tipo de conta (média, ponderada ou mediana) e casas decimais. É o arquivo que se mexe no dia a dia |
| `molde_op.py` | o HTML de cada painel, cartão e linha, e os ícones SVG. Só texto, nenhuma conta |
| `dados_op.py` | lê a planilha e refaz em Python as contas das medidas. Para se a planilha não tiver mais alguma coluna de `indicadores_op.py` |
| `prep_op.py` | formata os dados reais para o molde (lado do preview) |
| `fundo_op.py` | recorta a faixa do cabeçalho e monta o PNG de fundo |
| `gerar_op.py` | monta em DAX as medidas de cada indicador (`... Período`), as medidas HTML dos painéis e as das duas caixas do cabeçalho (`HTML Período` e `HTML Status`), e escreve o TMDL |
| `pagina_op.py` | escreve os visuais e a página no formato PBIR: os painéis, o rodapé, as duas caixas do cabeçalho (período exibido e indicador de atualização) e a segmentação **Período**. Só grava os visuais da própria lista, sem apagar a pasta |
| `preview_op.py` | monta a página e tira o print |
| `cabecalho_painel.png` | a faixa do cabeçalho (1920×156): foto aérea e logos. **Versionada** |
| `referencia_painel.png` | o print do layout de referência (1600×900). Fora do git, por tamanho |

### Mudanças mais comuns

- **Trocar a meta, a unidade, o ícone ou a casa decimal de um indicador:** `indicadores_op.py`.
- **Renomearam uma coluna na planilha:** acerte o `coluna=` do indicador em `indicadores_op.py`
  (tem de ser o título da linha 2, letra por letra). Enquanto não acertar, o indicador mostra `—`.
- **Tirar ou acrescentar um indicador de um painel:** mesma lista, em `EEBC`, `TMBR`, `OR`,
  `CONSUMO` ou `VOLUMES`. As linhas se redistribuem sozinhas na altura do painel.
- **Cor, fonte, espaçamento:** `molde_op.py` (aparência) ou `estilo_op.py` (paleta e grade).
- **Regra de cor ou escala da barra:** `TOLERANCIA` e `ESCALA` no topo de `indicadores_op.py`.

O preview mostra o seletor **Período** como está pintado no cabeçalho ("Mensal"): no Power BI ele
é uma lista suspensa nativa, que fica por cima da pintura. As opções do seletor ficam na tabela
**Período Painel** do modelo, e a opção que já vem marcada, em `PERIODO_PADRAO` de `pagina_op.py`.
O controle de datas da opção **Datas exatas** também é nativo e não aparece no preview; para ver
os números de um intervalo, use `dados_op.calcular(de='2026-11-01', ate='2026-11-10')`.

Depois de `gerar_op.py` ou `pagina_op.py`, feche e reabra o `.pbip` no Power BI Desktop.
Se os visuais ficarem vazios, clique com o botão direito em **Medidas HTML**, no painel
Dados, e escolha **Atualizar dados**.

## Página Volumes

```
python preview.py                 # gera preview.png com o cliente "Todos Clientes"
python preview.py "Q3 ABC"        # gera com outro cliente
python gerar.py                   # reescreve Medidas Volumes.tmdl
python pagina3.py                 # reescreve os visuais da página Volumes
```

| Arquivo | Papel |
| --- | --- |
| `estilo.py` | paleta e grade da página (margens, colunas, alturas das faixas) |
| `molde.py` | o HTML de cada painel. Só texto, nenhuma conta |
| `dados.py` | lê os parquet e refaz em Python as contas das medidas |
| `prep.py` | formata os dados reais para o molde (lado do preview) |
| `apoio.py` | medidas DAX de apoio (mês em foco, volumes, média de referência) |
| `gerar.py` | monta as medidas HTML em DAX e escreve o TMDL |
| `pagina3.py` | escreve os visuais e a página no formato PBIR |
| `preview.py` | monta a página e tira o print |

O preview desenha a segmentação (filtro) como uma caixa aproximada: no Power BI ela é um
visual nativo, que fica por cima do cartão. Serve para conferir o espaço que ela ocupa.

## Regra que vale para os dois

Nada de **aspas duplas** no HTML dos moldes. Ele vira literal de string no DAX, e uma aspa
dupla solta quebra a medida inteira. Use aspas simples nos atributos e entidades HTML
(`&#916;`, `&#8211;`) no lugar de caracteres que possam atrapalhar.
