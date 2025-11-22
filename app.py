"""mini-shell (Python)

Implementação educativa de um mini interpretador de comandos usando chamadas ao
sistema: `os.read`, `os.write`, `os.fork`, `os.execvp`, `os.waitpid`.

Funcionalidades:
- Prompt (`> `)
- Leitura da entrada padrão com `os.read()`
- Parsing usando `shlex.split()` (preserva aspas)
- Execução de comandos externos via `execvp`
- Built-ins: `exit` e `cd`
- Mensagens de erro amigáveis via `os.write()` (stderr)

Uso: executar `python3 app.py` e digitar comandos. O shell encerra com `exit` ou EOF.
"""

import os
import shlex
import sys


def read_line(prompt=b"> "):
	"""Lê uma linha da stdin usando `os.read` e retorna a string (sem newline).

	Se EOF for encontrado retorna None.
	"""
	# Mostra o prompt
	try:
		os.write(1, prompt)
	except OSError:
		pass

	buf = bytearray()
	while True:
		try:
			chunk = os.read(0, 1024)
		except OSError:
			return None

		if not chunk:
			# EOF
			if not buf:
				return None
			break

		buf.extend(chunk)
		if b"\n" in buf:
			break

	# separa até o primeiro newline
	if b"\n" in buf:
		line, rest = buf.split(b"\n", 1)
		# note: rest ficará no pipe (perdido aqui), mas para a maioria dos usos funcionará
	else:
		line = bytes(buf)

	try:
		return line.decode().strip()
	except Exception:
		return None


def parse_command(line):
	"""Parseia a linha em lista de argumentos, preservando aspas."""
	if not line:
		return []
	try:
		parts = shlex.split(line)
	except ValueError:
		parts = line.split()
	return parts


def execute_command(args):
	"""Executa o comando representado por `args`.

	- Built-ins: `exit` (retorna False para encerrar), `cd`.
	- Para outros: cria um filho com fork() e chama execvp(). O pai espera com waitpid().
	- Em caso de erro escreve mensagem amigável em stderr.
	"""
	if not args:
		return True

	cmd = args[0]

	# built-in: exit
	if cmd == "exit":
		return False

	# built-in: cd
	if cmd == "cd":
		try:
			target = args[1] if len(args) > 1 else os.path.expanduser("~")
			os.chdir(target)
		except Exception as e:
			msg = f"cd: {e}\n"
			os.write(2, msg.encode())
		return True

	# Execução de comando externo
	try:
		pid = os.fork()
	except OSError as e:
		os.write(2, f"fork failed: {e}\n".encode())
		return True

	if pid == 0:
		# processo filho
		try:
			os.execvp(cmd, args)
		except FileNotFoundError:
			os.write(2, f"{cmd}: comando não encontrado\n".encode())
		except PermissionError:
			os.write(2, f"{cmd}: permissão negada\n".encode())
		except Exception as e:
			os.write(2, f"{cmd}: erro ao executar: {e}\n".encode())
		# se execvp falhar, terminar o filho
		os._exit(1)
	else:
		# processo pai espera o filho terminar
		try:
			_, status = os.waitpid(pid, 0)
			# opcional: pode-se checar status e avisar se não-zero
			if os.WIFSIGNALED(status):
				sig = os.WTERMSIG(status)
				os.write(2, f"{cmd}: terminado por sinal {sig}\n".encode())
		except ChildProcessError:
			pass
		except KeyboardInterrupt:
			pass
		return True


def shell_loop():
	"""Loop principal do shell."""
	running = True
	while running:
		try:
			line = read_line()
			if line is None:
				# EOF
				os.write(1, b"\n")
				break

			if line == "":
				continue

			args = parse_command(line)
			running = execute_command(args)
		except KeyboardInterrupt:
			# Ctrl-C: escreve nova linha e continua
			os.write(1, b"\n")
			continue


if __name__ == "__main__":
	try:
		shell_loop()
	except Exception as e:
		os.write(2, f"Erro inesperado: {e}\n".encode())
		sys.exit(1)
