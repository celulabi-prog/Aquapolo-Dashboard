# Preview da página Volumes

O HTML dos painéis é escrito **uma vez só**, em `molde.py`. O mesmo molde serve a dois usos:

| | entrada | saída |
| --- | --- | --- |
| `preview.py` | números reais da base (`dados.py` → `prep.py`) | `preview.png`, a página renderizada em 1920×1080 |
| `gerar.py` | pedaços de DAX | `Medidas Volumes.tmdl`, as medidas do Power BI |

Como o molde é o mesmo, **o que aparece no preview é o que o Power BI desenha**. Dá para
ajustar espaçamento, cor e tipografia olhando a imagem, sem abrir o Power BI a cada tentativa.

## Como usar

```
pip install pandas pyarrow playwright
python -m playwright install chromium

python preview.py                 # gera preview.png com o cliente "Todos Clientes"
python preview.py "Q3 ABC"        # gera com outro cliente
python gerar.py                   # reescreve Medidas Volumes.tmdl
python pagina3.py                 # reescreve os visuais da página Volumes
```

Depois de `gerar.py` ou `pagina3.py`, feche e reabra o `.pbip` no Power BI Desktop.

## Arquivos

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
