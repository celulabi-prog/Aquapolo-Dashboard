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
| `molde_op.py` | o HTML de cada painel, cartão e linha, a aba que abre ao passar o mouse num indicador, e os ícones SVG. Só texto, nenhuma conta |
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
- **O que aparece na aba do indicador:** `dica()` em `molde_op.py`. A aba tem pouco espaço: nos
  cartões ela não pode passar da linha dos números.
- **Indicador sem meta:** fica sem cor e sem percentual. Com `escala=` (o valor que enche a barra)
  ele ganha uma barra azul; sem isso, só o contorno.

### Abas, mouse e folga dos visuais

- A aba de cada indicador abre **dentro do retângulo do próprio visual** (um visual HTML não desenha
  fora dele): nas linhas, embaixo ou em cima da linha; nos cartões, no alto do painel.
- **A área de um visual recebe o mouse mesmo onde é transparente.** Um visual por cima de um
  indicador tira dele o mouse, e a aba não abre. Por isso os visuais das duas caixas do cabeçalho
  só descem até o fim do título dos painéis (`H_DET` em `estilo_op.py`).
- Todos os visuais HTML ficam com a folga interna (`padding`) em zero. Com a folga padrão do Power BI,
  uns 16 px de cada lado, o conteúdo fica mais estreito que no preview e os nomes são cortados.

O preview mostra o seletor **Período** como está pintado no cabeçalho ("Mensal"): no Power BI ele
é uma lista suspensa nativa, que fica por cima da pintura. As opções do seletor ficam na tabela
**Período Painel** do modelo, e a opção que já vem marcada, em `PERIODO_PADRAO` de `pagina_op.py`.
O controle de datas da opção **Datas exatas** também é nativo e não aparece no preview; para ver
os números de um intervalo, use `dados_op.calcular(de='2026-11-01', ate='2026-11-10')`.

Depois de `gerar_op.py` ou `pagina_op.py`, feche e reabra o `.pbip` no Power BI Desktop.
Se os visuais ficarem vazios, clique com o botão direito em **Medidas HTML**, no painel
Dados, e escolha **Atualizar dados**.

## Visão Geral v2 (fluxo com destaque no lugar)

Página nova, ao lado da Visão Geral, que continua como está. Os arquivos têm o sufixo `_v2` e
nenhum deles grava em `Medidas HTML.tmdl` nem na pasta da página atual.

```
python prep_v2.py           # confere as regras (frase do desvio, situação, ponteiro), sem ler a planilha
python preview_v2.py        # gera preview_v2.png com os dados reais (precisa da unidade G:)
python preview_v2.py hoje   # idem, com os números do print de 03/11 a 18/11, sem ler a planilha
python preview_v2.py t3     # casos fictícios t1 a t7: os extremos do destaque (tudo fora, nada fora...)
python fundo_v2.py          # refaz o PNG de fundo (cabeçalho de 104 px e os tubos entre as colunas)
python gerar_v2.py          # reescreve Medidas HTML v2.tmdl
python pagina_v2.py         # reescreve os visuais da página visao_geral_v2
```

| Arquivo | Papel |
| --- | --- |
| `estilo_v2.py` | paleta, grade e posição de cada visual; `ABSOLUTOS` (frase do desvio em unidade) e os limites do minigráfico |
| `molde_v2.py` | o HTML de cada peça: medidor, minigráfico, linha, bloco, nó do trem, cartão, entrega, abas. A forma (calma, atenção, fora) entra como argumento |
| `prep_v2.py` | as regras em Python e o HTML do preview; guarda os casos de teste |
| `gerar_v2.py` | as mesmas regras em DAX e as 9 medidas `HTML v2 ...` (uma por visual), na tabela **Medidas HTML v2** |
| `pagina_v2.py` | os 11 visuais e o `page.json` da página **Visão Geral v2** |
| `fundo_v2.py` | o PNG de fundo `fundo_visao_geral_v2.png` |
| `preview_v2.py` | monta a página e tira o print |
| `confere_v2.py` | compara o texto de cada medida, pedido ao motor do Power BI, com o HTML do `prep_v2` |
| `referencia_v2/` | o protótipo aprovado, para comparar com o preview |

Como funciona o destaque: cada indicador fica sempre no mesmo lugar, na ordem do processo. A linha
tem peso de altura 1 (dentro da meta), 1,5 (atenção) ou 2 (fora); a que está em destaque mostra o
valor maior, o desvio em palavras e o minigráfico do período. Como a forma depende do dado, o
`gerar_v2.py` chama o molde uma vez por forma e o DAX escolhe com `SWITCH` sobre a situação.

### Mudanças mais comuns na v2

- **Meta, unidade, casas decimais, coluna da planilha:** continuam em `indicadores_op.py`, e valem
  para as duas páginas. Depois, `python gerar_op.py` e `python gerar_v2.py`.
- **Que indicador fica em qual coluna ou grupo de utilidades:** `COLUNAS` e `GRUPOS`, no topo de `prep_v2.py`.
- **Frase do desvio em unidade (hoje só a Idade do Lodo, em dias):** `ABSOLUTOS` em `estilo_v2.py`.
- **Peso e altura mínima das linhas, tamanho das letras:** `linha()` em `molde_v2.py`.
- **Cor, grade, posição dos visuais:** `estilo_v2.py`.

Toda regra existe duas vezes, em `prep_v2.py` e em `gerar_v2.py` (os comentários dizem qual espelha
qual). Mexeu numa, mexa na outra e rode a conferência:

```
python confere_v2.py consultas q.dax    # grava 47 consultas DAX
(rodar cada uma no motor do Desktop e gravar a resposta da consulta N em q.dax.N.out)
python confere_v2.py comparar q.dax     # tem de terminar em TUDO IGUAL
```

As segmentações Período e datas da v2 são cópias próprias: a escolha feita numa página não muda a outra.

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
