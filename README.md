# Dashboard - Aquapolo

Relatório do Power BI salvo como projeto PBIP: o relatório está em PBIR e o modelo semântico em TMDL.

## Como abrir

1. Abra `Dashboard - Aquapolo.pbip` no Power BI Desktop.
2. O repositório não traz dados. O parâmetro `PastaBase` lê a base de `C:\Aquapolo\Base_PowerBI\`, um caminho igual em todos os computadores. Essa pasta precisa ter `fato_indicadores.parquet`, `dim_indicadores.parquet` e a subpasta `Planilhas\` com `Consumo de quimicos EPAI.xlsm` (usada pela página **Indicadores Químicos**). Há duas formas de montá-la:
   - **Recomendado:** sincronize a pasta compartilhada `Base_PowerBI` do OneDrive e crie um atalho para ela no Prompt de Comando, uma vez só:
     `mkdir C:\Aquapolo` e depois `mklink /J C:\Aquapolo\Base_PowerBI "<caminho da Base_PowerBI no seu OneDrive>"`. Assim a base se atualiza sozinha.
   - **Manual:** crie a pasta e copie os arquivos para ela sempre que houver uma extração nova.
3. Clique em **Atualizar**.
4. Se os visuais HTML da página **Visão Geral** aparecerem vazios, clique com o botão direito na tabela **Medidas HTML**, no painel Dados, e escolha **Atualizar dados**.

## Painel operacional

A página **Visão Geral** é o painel operacional, em tema escuro, com 23 indicadores em cinco painéis: **Qualidade EEBC**, **Performance TMBR**, **Performance OR**, **Consumo de Químicos e Energia** e **Volumes**, mais a faixa de rodapé com a data da base e a legenda.

- São **6 visuais HTML Content** (visual personalizado do AppSource), um por painel e um para o rodapé. Cada painel desenha todas as suas linhas ou cartões de uma vez.
- A imagem `fundo_painel_operacional.png` é o fundo da página e contém **só o cabeçalho** — a foto aérea e os logos GS Inima / Sabesp. Nenhum número está na imagem.
- As medidas ficam em **Medidas HTML** (`HTML Painel EEBC`, `HTML Painel TMBR`, `HTML Painel OR`, `HTML Painel Consumo`, `HTML Painel Volumes` e `HTML Rodapé`), ligadas à base pelo `ID_Indicador`.
- **Valor:** média dos últimos 30 dias com dado do indicador, até a última data disponível ou selecionada. Para indicadores calculados é a razão das somas (`Numerador / Denominador`), pela medida `[Valor Indicador]`.
- **Δ Per.:** variação em relação aos 30 dias anteriores (nos cartões de consumo e volumes).
- **Ref.:** meta (`Target_Min` / `Target_Max`) da `dim_indicadores`. Onde o indicador tem mínimo **e** máximo (Idade do Lodo, Alimento/Microorganismo, Fluxo), aparece **Faixa a – b**. Para mudar uma meta, altere a base, não a medida.
- **Cores:** verde dentro da meta, amarelo até 10% fora, vermelho além disso, cinza sem meta ou sem dado. A barra enche até 160% da referência e o tracejado marca os 100%.

Esta página **não é editada à mão**. Ela é gerada pelos scripts de `ferramentas/preview/`, a partir de um molde HTML único — veja o `LEIAME.md` de lá. Mexer no `visual.json` ou na medida direto no Power BI funciona, mas o próximo `python pagina_op.py` ou `python gerar_op.py` desfaz.

### Indicadores sem referência na base

Três pontos do layout de referência não têm correspondência na `dim_indicadores` e por isso aparecem diferentes do desenho original:

| Indicador | No painel | Motivo |
| --- | --- | --- |
| **Blend** | cartão vazio, com aviso | a base não traz o indicador |
| **Energia - Biológico** | `Ref. —`, sem barra | `Consumo SOP Biológico/ Amônia Removida` está sem `Target_Max` |
| **Coagulante** | `Ref. 17,0 gPAC/gP` | é o `Target_Max` da base (`PAC/ P rem`) |

Preenchendo o `Target_Max` desses indicadores na base, a barra e o percentual passam a aparecer sozinhos.

## Página Indicadores Químicos

- **Período:** seletor de mês no canto superior direito. "Último mês" é o mês mais recente com dado e acompanha a base sozinho a cada atualização.
- **Cartões:** consumo unitário total (kg/m³, da base, com variação contra o mês anterior e meta da `dim_indicadores`), menor autonomia e quantos químicos estão abaixo da autonomia alvo.
- **Tabelas:** consumo unitário por químico (g/m³) e autonomia (dias) de cada químico, com barra e status. Passe o mouse numa linha para abrir a dica **Detalhe do químico**: estoque, consumo médio de 7 e 30 dias, previsão de término, comparações e evolução no ano.
- **Comparativo mensal:** mês selecionado contra o mesmo mês do ano anterior.
- **Evolução:** Jan–Dez do ano do período. O seletor **Químico** troca entre o total (kg/m³) e um químico (g/m³), e a caixa **Comparar** liga a linha do ano anterior.
- **Fontes:** consumo diário (kg) e estoque (L) de cada químico vêm da planilha `Planilhas\Consumo de quimicos EPAI.xlsm` (tabela oculta **Químicos Diário**). Consumo unitário = consumo (kg) × 1000 / volume de clientes (m³) da base. Estoque em kg = litros × densidade da própria planilha. Autonomia e metas vêm da base.
- **Status:** verde no alvo, amarelo até 10% fora (a mesma regra da Visão Geral) e vermelho além disso. Cinza indica que não há meta ou dado.
- **Ainda sem dado:** RoClean 902 e RoClean 193 não têm autonomia nem estoque na planilha. Também não existe meta de consumo por químico; ao preencher `Target_Max` na `dim_indicadores`, o status do consumo passa a ter cor sozinho.
- Para mudar a lista ou a ordem dos químicos, edite a tabela **Químicos** e o `Mapa` da consulta **Químicos Diário** (os dois têm um comentário `EDITAR AQUI`). As medidas ficam na tabela **Medidas Químicos**.

## Página Energia

- Página **Energia** (`definition/pages/pagina_energia`): cabeçalho, card de consumo específico por área, card de perdas, bloco de comparativo mensal (colunas, linhas e rosca) e rodapé. São 5 visuais **HTML Content** e 4 segmentações.
- As medidas ficam na tabela **Medidas Energia**. Os gráficos são SVG gerados em DAX (pasta `SVG`), e os blocos da página ficam na pasta `HTML`.
- **Período:** é o mês escolhido nas segmentações **Ano** e **Mês**. Sem seleção, vale o último mês com dado de energia. O valor do mês é a razão das somas (kWh ÷ m³ no mês).
- **Área:** aceita uma área, várias (Ctrl + clique) ou **Selecionar tudo**. Filtra o gráfico de colunas e destaca as fatias na rosca. O gráfico de linhas mostra a área quando só uma está marcada. Com várias ou todas, mostra o Consumo Unitário - Energia.
- **Comparar:** com **Sim**, mostra também o mesmo mês do ano anterior.
- **Status:** verde até a meta, amarelo até 10% acima, vermelho acima disso e cinza quando o indicador não tem meta na `dim_indicadores`.
- **Rosca:** participação de cada área na soma de kWh (Numerador) das 6 áreas no mês.
- **Pop-ups ao passar o mouse:** feitos só com CSS (`:hover`) dentro de cada visual HTML Content. Um visual não desenha fora do próprio retângulo, por isso cada pop-up abre dentro do seu card.
  - **Linha de área ou de perda:** abre o painel de detalhe com status, valor do mês, target, energia ou volume, média diária, participação, variação contra o mês anterior e contra o mesmo mês do ano anterior, e um mini gráfico de 12 meses.
  - **Coluna de uma área, mês no gráfico de linhas ou fatia da rosca:** mostra um cartão com os valores daquele ponto.
  - Os pop-ups ficam ocultos por padrão. Se o CSS não carregar, a página funciona sem eles.
- As tabelas `Energia Ano`, `Energia Mês`, `Energia Área` e `Energia Comparar` são calculadas e desconectadas do modelo. Servem só às segmentações da página. Para mudar a cor de uma área na rosca, altere `Energia Área`.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `Dashboard - Aquapolo.pbip` | Arquivo que abre o projeto |
| `Dashboard - Aquapolo.Report/` | Relatório (PBIR). Os visuais do painel operacional ficam em `definition/pages/a822121ef6e9b05473aa/visuals/painel_*` e `.../rodape` |
| `Dashboard - Aquapolo.SemanticModel/` | Modelo semântico (TMDL). As medidas do painel ficam em `definition/tables/Medidas HTML.tmdl` |
| `ferramentas/preview/` | Scripts que geram o painel operacional e a página Volumes: molde HTML único, preview em PNG, medidas DAX e visuais PBIR |
| `fundo_painel_operacional.png` | Fundo da página Visão Geral (1920×1080): só o cabeçalho, o resto é cor chapada |
| `fundo_indicadores_quimicos.png` | Imagem de fundo da página Indicadores Químicos (1920×1080) |
| `Dashboard - Aquapolo.SemanticModel/definition/tables/Medidas Químicos.tmdl` | Medidas da página Indicadores Químicos. As tabelas de apoio dela são `Químicos Diário`, `Químicos`, `Meses`, `Mês do Ano`, `Seletor Químico` e `Comparar Ano Anterior` |

## Regras de Git e GitHub (pessoas e agentes)

Cinco pessoas trabalham neste repositório, cada uma com a própria conta do GitHub. A branch `main` é protegida: só recebe mudanças por pull request com 1 aprovação, e a regra vale também para administradores.

### Antes de começar

1. Confira se está na conta certa: `gh auth status` deve mostrar a conta de quem está operando a máquina. Não use a conta de outra pessoa.
2. Confira o autor dos commits: `git config user.name` e `git config user.email` devem ser os dessa mesma pessoa. Se estiverem errados, corrija só neste repositório: `git config user.name "Nome"` e `git config user.email "email@dominio"`.
3. Atualize a `main` local: `git switch main` e depois `git pull`.

### Fluxo de trabalho

1. Crie uma branch a partir da `main`: `git switch -c <tipo>/<descricao-curta>`. Use `feat/` para algo novo, `fix/` para correção e `docs/` para documentação. Exemplo: `feat/medida-turbidez`.
2. Faça commits pequenos, com mensagens em português que digam o que mudou.
3. Antes de abrir o PR, traga as novidades da `main`: `git fetch origin` e depois `git rebase origin/main`.
4. Envie a branch com `git push -u origin <branch>` e abra o PR com `gh pr create`. Na descrição, diga o que mudou e quais páginas ou tabelas foram mexidas.
5. Outra pessoa revisa e aprova. Ninguém aprova o próprio PR.
6. O merge é feito por **squash** ou **rebase**, porque o merge commit está desativado. A branch é apagada automaticamente depois do merge.

### Proibido

- Commitar ou fazer push direto na `main`.
- Usar `git push --force` na `main`. Na própria branch, use só `--force-with-lease`, e apenas se ninguém mais estiver trabalhando nela.
- Pular hooks ou verificações (`--no-verify`).
- Alterar as regras de proteção da branch ou a visibilidade do repositório.
- Commitar dados. O repositório é **público**: a pasta `Base_PowerBI/`, os arquivos `.parquet`, `.csv`, `.xlsx` e `.xlsm`, `.pbi/cache.abf` e `.pbi/localSettings.json` nunca entram no git (já estão no `.gitignore`). A base é distribuída pela pasta compartilhada do OneDrive. Credenciais e senhas também não.
- Mudar o parâmetro `PastaBase` (`expressions.tmdl`). Ele é `C:\Aquapolo\Base_PowerBI\` para todos; se a sua base estiver em outro lugar, use o atalho do passo 2 de **Como abrir**.

### Evitar conflitos no PBIP

Os arquivos do Power BI não fazem merge bem quando duas pessoas mexem na mesma coisa.

- Combine no grupo antes de editar uma página (`definition/pages/<id>/`) ou uma tabela do modelo (`definition/tables/*.tmdl`) em que outra pessoa já está trabalhando.
- Feche o Power BI Desktop antes de fazer `pull`, `rebase` ou trocar de branch. Abra o projeto de novo depois.
- Se houver conflito em arquivo `.json` ou `.tmdl`, resolva com cuidado: mantenha a sintaxe válida e abra o projeto no Power BI Desktop para conferir antes de continuar.
