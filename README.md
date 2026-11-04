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

- A página **Visão Geral** tem 23 visuais **HTML Content** (visual personalizado do AppSource) sobre a imagem `fundo_painel_operacional.png`.
- Cada visual mostra uma medida da tabela calculada **Medidas HTML**, ligada à base real pelo `ID_Indicador` (variável `Ids` no início da medida).
- **Valor:** média dos últimos 30 dias com dado do indicador, até a última data disponível ou selecionada. Para indicadores calculados é a razão das somas (`Numerador / Denominador`), pela medida `[Valor Indicador]`.
- **Δ Per.:** variação em relação aos 30 dias anteriores.
- **Ref.:** meta (`Target_Min` / `Target_Max`) da `dim_indicadores`. Para mudar uma meta, altere a base, não a medida.
- O cartão **Blend** ainda não tem fonte na base e mostra "Sem fonte de dados na base".

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

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `Dashboard - Aquapolo.pbip` | Arquivo que abre o projeto |
| `Dashboard - Aquapolo.Report/` | Relatório (PBIR). Os visuais do painel ficam em `definition/pages/a822121ef6e9b05473aa/visuals/html_*` |
| `Dashboard - Aquapolo.SemanticModel/` | Modelo semântico (TMDL). As medidas do painel ficam em `definition/tables/Medidas HTML.tmdl` |
| `fundo_painel_operacional.png` | Imagem de fundo original do painel (1920×1080) |
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
