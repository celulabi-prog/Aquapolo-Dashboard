# Dashboard - Aquapolo

Relatório do Power BI salvo como projeto PBIP: o relatório está em PBIR e o modelo semântico em TMDL.

## Como abrir

1. Abra `Dashboard - Aquapolo.pbip` no Power BI Desktop.
2. O repositório não traz dados. O parâmetro `PastaBase` lê a base de `C:\Aquapolo\Base_PowerBI\`, um caminho igual em todos os computadores. Essa pasta precisa ter `fato_indicadores.parquet` e `dim_indicadores.parquet`. Há duas formas de montá-la:
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

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `Dashboard - Aquapolo.pbip` | Arquivo que abre o projeto |
| `Dashboard - Aquapolo.Report/` | Relatório (PBIR). Os visuais do painel ficam em `definition/pages/a822121ef6e9b05473aa/visuals/html_*` |
| `Dashboard - Aquapolo.SemanticModel/` | Modelo semântico (TMDL). As medidas do painel ficam em `definition/tables/Medidas HTML.tmdl` |
| `fundo_painel_operacional.png` | Imagem de fundo original do painel (1920×1080) |

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
- Commitar dados. O repositório é **público**: a pasta `Base_PowerBI/`, os arquivos `.parquet` e `.csv`, `.pbi/cache.abf` e `.pbi/localSettings.json` nunca entram no git (já estão no `.gitignore`). A base é distribuída pela pasta compartilhada do OneDrive. Credenciais e senhas também não.
- Mudar o parâmetro `PastaBase` (`expressions.tmdl`). Ele é `C:\Aquapolo\Base_PowerBI\` para todos; se a sua base estiver em outro lugar, use o atalho do passo 2 de **Como abrir**.

### Evitar conflitos no PBIP

Os arquivos do Power BI não fazem merge bem quando duas pessoas mexem na mesma coisa.

- Combine no grupo antes de editar uma página (`definition/pages/<id>/`) ou uma tabela do modelo (`definition/tables/*.tmdl`) em que outra pessoa já está trabalhando.
- Feche o Power BI Desktop antes de fazer `pull`, `rebase` ou trocar de branch. Abra o projeto de novo depois.
- Se houver conflito em arquivo `.json` ou `.tmdl`, resolva com cuidado: mantenha a sintaxe válida e abra o projeto no Power BI Desktop para conferir antes de continuar.
