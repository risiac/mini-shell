# mini-shell

Este repositório contém uma implementação educativa de um mini interpretador de comandos (shell) em Python.

**Como compilar e rodar**
- Não há compilação necessária. Execute com Python 3:

```bash
python3 app.py
```

- Para testes não interativos (ex.: em um script), envie comandos pelo stdin:

```bash
printf 'echo Olá Mundo\nls -1\nexit\n' | python3 app.py
```

**Quais chamadas ao sistema foram utilizadas**
- `os.read()` — leitura da entrada padrão (stdin).
- `os.write()` — escrita de prompt e mensagens (stdout/stderr).
- `os.fork()` — criação de processo filho para executar comandos.
- `os.execvp()` — substitui o processo filho pelo programa solicitado.
- `os.waitpid()` — processo pai aguarda término do filho.
- `os._exit()` — encerra o processo filho em caso de falha.
- `os.chdir()` — usado pelo built-in `cd`.

**Exemplos de comandos testados e suas saídas**
- `echo Olá Mundo`
  - Saída: `Olá Mundo`
- `ls -1`
  - Saída: lista de arquivos no diretório corrente (uma entrada por linha).
- `cat arquivo_que_nao_existe`
  - Saída: mensagem de erro do `cat` ou do próprio sistema: `cat: arquivo_que_nao_existe: No such file or directory`.
- `cd /tmp` seguido de `pwd` (via `pwd` externo)
  - Altera o diretório corrente do processo shell.
- `comando_inexistente`
  - Saída: `comando_inexistente: comando não encontrado` (mensagem gerada pelo filho quando exec falha).

**Limitações conhecidas**
- Não implementa pipes (`|`), redirecionamentos (`>`, `<`) nem background (`&`).
- Leitura com `os.read()` consome blocos do stdin; em alguns casos de redirecionamento complexo, o buffer residual pode ser perdido.
- Parsing é simples (usa `shlex.split`) — não há expansão de variáveis (`$VAR`) nem globbing (curinga `*`).
- Não há histórico de comandos nem edição de linha (não usa readline).
- Tratamento de sinais é básico (Ctrl-C apenas interrompe o comando atual).

Se quiser, eu posso adicionar suporte a pipes/redirecionamento e mais built-ins (`pwd`, `history`).

## Casos de Teste (reprodutíveis)

Os testes abaixo criam um ambiente controlado (arquivos de teste) e executam o `mini-shell` de forma não-interativa,
assim as saídas esperadas são determinísticas.

1) Teste básico: `echo`, `ls`, `cat` com arquivo existente e não-existente

```bash
# preparar ambiente de teste
rm -rf test_env && mkdir test_env
printf 'Conteúdo do arquivo 1\n' > test_env/file1.txt
printf 'Outro arquivo\n' > test_env/file2.txt

# executar o mini-shell dentro de test_env (usando o app.py do diretório superior)
cd test_env
printf 'echo Olá Mundo\nls -1\ncat file1.txt\ncat nao_existe.txt\nexit\n' | python3 ../app.py
```

Saída esperada (exemplo exato):

```
> Olá Mundo
> file1.txt
file2.txt
> Conteúdo do arquivo 1
> cat: nao_existe.txt: No such file or directory
>
```

Observações: a linha `ls -1` lista os arquivos do diretório (`file1.txt` e `file2.txt`). A mensagem de erro de `cat` pode variar ligeiramente
de acordo com a implementação local do `cat`, mas normalmente será algo como `cat: nao_existe.txt: No such file or directory`.

2) Teste de `cd` e comando externo `pwd`

```bash
# dentro de test_env (retorne para o repositório, se necessário)
cd ..
printf 'cd test_env\npwd\nexit\n' | python3 app.py
```

Saída esperada (exemplo):

```
> /caminho/para/mini-shell/test_env
>
```

3) Teste de comando inexistente

```bash
printf 'comando_inexistente\nexit\n' | python3 app.py
```

Saída esperada:

```
> comando_inexistente: comando não encontrado
>
```

Observação: a mensagem exata pode aparecer no stderr; aqui mostramos o conteúdo que o shell gera ao falhar no execvp.

4) Teste rápido via arquivo de script

Você pode juntar os testes em um arquivo e executá-los de uma vez:

```bash
cat > run_tests.sh <<'EOF'
#!/usr/bin/env bash
rm -rf test_env && mkdir test_env
printf 'Conteúdo do arquivo 1\n' > test_env/file1.txt
printf 'Outro arquivo\n' > test_env/file2.txt

cd test_env
printf 'echo Teste1\nls -1\ncat file1.txt\nexit\n' | python3 ../app.py
EOF
chmod +x run_tests.sh
./run_tests.sh
```

Saídas esperadas seguem os exemplos descritos nos testes 1-3.

# mini-shell
O projeto consiste em criar um mini interpretador de comandos que simula um shell Linux, implementado em Python. O mini shell interpreta comandos digitados, cria processos, executa programas via exec(), espera sua finalização e permite encerrar a sessão com exit.
