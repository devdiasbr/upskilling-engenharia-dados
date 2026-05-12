# Trilha de Engenharia de Dados — Para Facilitadores

## Papel do Facilitador

Você não é o expositor — você é o guia. O conteúdo teórico está no `conteudo.md` de cada módulo. Sua função na sessão ao vivo é:

1. **Conectar** o conteúdo com a experiência real do grupo
2. **Provocar** com perguntas antes de dar respostas
3. **Fazer avançar** quando o grupo trava
4. **Sintetizar** padrões que emergem da discussão

A sessão funciona melhor quando o grupo chega tendo lido o conteúdo e tentado os exercícios. Invista tempo em comunicar isso antes de cada módulo.

---

## Preparação Antes de Cada Sessão

**48h antes:**
- [ ] Leia o `conteudo.md` do módulo (mesmo que já conheça o tema — o participante vai citar exemplos dali)
- [ ] Faça todos os exercícios você mesmo. Você precisa conhecer os pontos de dificuldade.
- [ ] Leia o `gabarito.md` para ter as soluções e as explicações na cabeça
- [ ] Leia o `sessao-ao-vivo.md` — o roteiro está pronto, mas você precisa internalizá-lo

**15 min antes:**
- [ ] Ambiente funcionando: banco SQLite criado, Python + pandas + pyarrow instalados
- [ ] PPT aberto no slide correto
- [ ] Terminal aberto na pasta do projeto

---

## Estrutura Padrão de Sessão (2h)

Todos os módulos seguem o mesmo padrão geral:

| Bloco | Tempo | Objetivo |
|-------|-------|----------|
| Abertura | 10 min | Conectar o grupo, verificar ambiente, apresentar agenda |
| Bloco 1 | 30–40 min | Conceito central — demo ou análise coletiva |
| Bloco 2 | 30–40 min | Exercício em duplas ou grupo |
| Bloco 3 | 15–20 min | Fechamento do módulo + preview do próximo |

O roteiro detalhado de cada sessão está em `modulos/0X-nome/sessao-ao-vivo.md`.

---

## Dinâmicas que Funcionam Bem

### "Leia em silêncio e responda"
Mostre um trecho de código ou um dataset na tela. Dê 1–2 minutos de silêncio. Depois pergunte. Evita que a resposta do primeiro participante influencie os demais.

### "Levantar a mão" (ou reação no chat)
Bom para sondagens rápidas: "Quem já usou Parquet antes?" "Quem terminou todos os exercícios?"

### "Você faria diferente?"
Após mostrar um gabarito ou solução, pergunte se alguém resolveu diferente. As divergências são os momentos de aprendizado mais ricos.

### "O que aconteceria se...?"
Perguntas de variação: "E se o banco estivesse fora ar?" / "E se tivéssemos 10 bilhões de linhas?" Força aplicação do conceito em contextos diferentes.

---

## Como Lidar com Situações Comuns

**O grupo não tentou os exercícios:**
Não pule os exercícios. Reserve 10 min para que façam ao menos a Parte A ao vivo. A sessão perde muito valor sem a tentativa prévia.

**Alguém domina o assunto e responde tudo:**
"Ótimo. Mas antes de você responder, o que o resto do grupo acha?" Use o especialista para validar, não para substituir a participação dos demais.

**Ninguém responde às perguntas:**
Espere. Silêncio de 10–15 segundos parece longo, mas funciona. Se persistir, quebre com: "Tudo bem — o que vocês acham que eu quero ouvir aqui?"

**A demo técnica não funciona:**
Tenha o resultado esperado salvo (um arquivo de saída, um screenshot). "Não deu certo ao vivo, mas o resultado seria este. Por quê?" — mantenha a discussão conceitual.

**O grupo quer aprofundar demais em uma ferramenta específica:**
"Isso é exatamente o que o Airflow / dbt / Spark faz — vocês vão ver isso na prática. O que estamos construindo hoje é o fundamento que vai fazer aquela ferramenta fazer sentido."

---

## Módulo a Módulo — O que Enfatizar

| Módulo | Armadilha comum | O que enfatizar |
|--------|----------------|----------------|
| 01 SQL | Focar em sintaxe, não em lógica | "O que a query quer saber?" antes de como escrever |
| 02 Modelagem | Normalização como dogma | Trade-offs práticos — normalização tem custo de join |
| 03 Formatos | "Parquet é sempre melhor" | Legibilidade humana tem valor. CSV ainda é rei para interoperabilidade |
| 04 Python | Pandas gotchas (SettingWithCopy, inplace) | Funções com responsabilidade única > script monolítico |
| 05 ETL/ELT | `except: pass` como solução | Falha explícita é feature, não bug |
| 06 Pipelines | Airflow como agendador de cron | DAG modela dependências, não só agendamento |
| 07 Armazenamento | Lake = destino de tudo | Promover para trusted/ exige validação — raw/ é sagrado |
| 08 Qualidade | Testes como burocracia | TDD economiza tempo — o ciclo vermelho-verde é rápido |
| 09 Troubleshooting | Mudar várias coisas ao mesmo tempo | Uma mudança por vez. Hipótese explícita antes de mudar. |

---

## Antes de Começar a Primeira Sessão

Na primeira sessão (Módulo 1), reserve 5 minutos extras para:

1. Apresentar a trilha como um todo — mostre os 9 módulos e como se conectam
2. Mostrar o banco de dados (`recursos/schema.md`) — ele será o fio condutor de tudo
3. Combinar as regras de engajamento: conteúdo assíncrono antes da sessão, exercícios antes da sessão, gabarito só depois de tentar

---

## Material de Suporte

Tudo está no repositório:

```
apresentacao-curso/
  para-participantes.md    ← compartilhe com a turma antes do início
  para-gestores.md         ← use para alinhamento com sponsors
  para-facilitadores.md    ← este documento

modulos/
  0X-nome/
    README.md              ← objetivos e pré-requisitos do módulo
    conteudo.md            ← material de leitura
    sessao-ao-vivo.md      ← seu roteiro
    exercicios/
      exercicios.md
      gabarito.md
    sessao-ao-vivo-*.pptx  ← apresentação do módulo

recursos/
  dados.db                 ← banco SQLite gerado pelo setup_db.py
  schema.md                ← descrição das tabelas
```
