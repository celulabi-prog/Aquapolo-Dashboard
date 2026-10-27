# Dashboard - Aquapolo

Relatório do Power BI salvo como projeto PBIP: o relatório está em PBIR e o modelo semântico em TMDL.

## Como abrir

1. Abra `Dashboard - Aquapolo.pbip` no Power BI Desktop.
2. O repositório não traz dados: o cache do modelo (`.pbi/cache.abf`) e os arquivos `.parquet` ficam de fora. As consultas `fato_indicadores` e `dim_indicadores` leem `fato_indicadores.parquet` e `dim_indicadores.parquet` da pasta `Base_PowerBI`. Ajuste o caminho no Power Query para onde esses arquivos estão na sua máquina e clique em **Atualizar**.
3. Se os visuais HTML da página **Visão Geral** aparecerem vazios, clique com o botão direito na tabela **Medidas HTML**, no painel Dados, e escolha **Atualizar dados**.

## Painel operacional

- A página **Visão Geral** tem 23 visuais **HTML Content** (visual personalizado do AppSource) sobre a imagem `fundo_painel_operacional.png`.
- Cada visual mostra uma medida da tabela calculada **Medidas HTML**. As medidas ainda usam valores fixos provisórios: para ligar ao dado real, troque os números de `VAR Valor`, `VAR Ref` e `VAR VarPeriodo` pela medida correspondente.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `Dashboard - Aquapolo.pbip` | Arquivo que abre o projeto |
| `Dashboard - Aquapolo.Report/` | Relatório (PBIR). Os visuais do painel ficam em `definition/pages/a822121ef6e9b05473aa/visuals/html_*` |
| `Dashboard - Aquapolo.SemanticModel/` | Modelo semântico (TMDL). As medidas do painel ficam em `definition/tables/Medidas HTML.tmdl` |
| `fundo_painel_operacional.png` | Imagem de fundo original do painel (1920×1080) |
