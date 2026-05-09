import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, Text, Scrollbar, VERTICAL, END
import sqlite3
from datetime import datetime

# ── Usuários autorizados ──────────────────────────────────────────────────────
USUARIOS_AUTORIZADOS = ["Usuario1", "Usuario2", "Usuario3", "Usuario4"]
usuario_logado = None


# ── Banco de dados ────────────────────────────────────────────────────────────
def setup_database():
    conn = sqlite3.connect('chaves.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT NOT NULL,
            cor TEXT NOT NULL,
            retirado_por TEXT,
            data_retirada TEXT,
            data_devolucao TEXT,
            UNIQUE(chave, cor)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT NOT NULL,
            cor TEXT NOT NULL,
            evento TEXT NOT NULL,
            pessoa TEXT,
            usuario TEXT,
            data_evento TEXT NOT NULL
        )
    ''')

    for cor in ["green", "blue", "orange"]:
        for chave_num in range(1, 16):
            chave_nome = f"Chave {chave_num:02d}"
            cursor.execute('''
                INSERT OR IGNORE INTO chaves (chave, cor)
                VALUES (?, ?)
            ''', (chave_nome, cor))

    conn.commit()
    conn.close()


# ── Login ─────────────────────────────────────────────────────────────────────
def tela_login():
    """Exibe a janela de login antes de abrir o sistema principal."""
    login_window = tk.Tk()
    login_window.title("Login — Quadro de Chaves")
    login_window.geometry("340px" if False else "340x220")
    login_window.resizable(False, False)

    # Centraliza na tela
    login_window.eval('tk::PlaceWindow . center')

    tk.Label(login_window, text="🗝️  Quadro de Chaves",
             font=("Arial", 14, "bold")).pack(pady=(20, 4))
    tk.Label(login_window, text="Faça login para continuar",
             font=("Arial", 10), fg="gray").pack(pady=(0, 16))

    frame = tk.Frame(login_window)
    frame.pack(padx=30, fill="x")

    tk.Label(frame, text="Usuário:", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
    entry_usuario = tk.Entry(frame, width=24)
    entry_usuario.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    tk.Label(frame, text="Senha:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
    entry_senha = tk.Entry(frame, width=24, show="*")
    entry_senha.grid(row=1, column=1, sticky="ew", padx=(8, 0))

    def confirmar_login():
        global usuario_logado
        usuario = entry_usuario.get().strip()
        senha = entry_senha.get().strip()

        if usuario not in USUARIOS_AUTORIZADOS:
            messagebox.showerror("Acesso negado", "Usuário não autorizado.", parent=login_window)
            return

        # Senha simples: igual ao nome do usuário (pode ser personalizado)
        if senha != usuario:
            messagebox.showerror("Acesso negado", "Senha incorreta.", parent=login_window)
            return

        usuario_logado = usuario
        login_window.destroy()
        abrir_sistema()

    def ao_pressionar_enter(event):
        confirmar_login()

    entry_senha.bind("<Return>", ao_pressionar_enter)

    tk.Button(login_window, text="Entrar", bg="#2E7D32", fg="white",
              font=("Arial", 10, "bold"), width=16,
              command=confirmar_login).pack(pady=14)

    login_window.mainloop()


# ── Resetar estado ────────────────────────────────────────────────────────────
def resetar_estado_chaves():
    confirmar = messagebox.askyesno(
        "Resetar Estado",
        "Tem certeza que deseja resetar todas as chaves?\nEsta ação também limpará o histórico."
    )
    if not confirmar:
        return

    conn = sqlite3.connect('chaves.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE chaves
        SET retirado_por = NULL, data_retirada = NULL, data_devolucao = NULL
    ''')
    cursor.execute('DELETE FROM historico')
    conn.commit()
    conn.close()

    messagebox.showinfo("Resetar Estado", "Todas as chaves foram resetadas para disponíveis.")

    for botao in botoes:
        botao.config(bg=botao.original_color, fg='white')

    atualizar_relatorio_em_uso()


# ── Registrar evento ──────────────────────────────────────────────────────────
def registrar_evento(chave_id, chave_nome, cor):
    conn = sqlite3.connect('chaves.db')
    cursor = conn.cursor()

    cursor.execute('SELECT retirado_por FROM chaves WHERE chave = ? AND cor = ?', (chave_nome, cor))
    result = cursor.fetchone()

    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if result and result[0]:
        cursor.execute('''
            UPDATE chaves
            SET retirado_por = NULL, data_retirada = NULL, data_devolucao = ?
            WHERE chave = ? AND cor = ?
        ''', (agora, chave_nome, cor))
        cursor.execute('''
            INSERT INTO historico (chave, cor, evento, usuario, data_evento)
            VALUES (?, ?, 'Devolução', ?, ?)
        ''', (chave_nome, cor, usuario_logado, agora))
        messagebox.showinfo("Devolução", f"{chave_nome} devolvida por {usuario_logado}.")
        botoes[chave_id].config(bg=botoes[chave_id].original_color, fg='white')
    else:
        nome = simpledialog.askstring(
            "Retirada de Chave",
            f"Quem está retirando a {chave_nome}?\n(Operador: {usuario_logado})"
        )
        if nome:
            cursor.execute('''
                UPDATE chaves
                SET retirado_por = ?, data_retirada = ?, data_devolucao = NULL
                WHERE chave = ? AND cor = ?
            ''', (nome, agora, chave_nome, cor))
            cursor.execute('''
                INSERT INTO historico (chave, cor, evento, pessoa, usuario, data_evento)
                VALUES (?, ?, 'Retirada', ?, ?, ?)
            ''', (chave_nome, cor, nome, usuario_logado, agora))
            messagebox.showinfo("Retirada", f"{chave_nome} retirada por {nome}.\nOperador: {usuario_logado}")
            botoes[chave_id].config(bg='white', fg='black')

    conn.commit()
    conn.close()
    atualizar_relatorio_em_uso()


# ── Criar botões ──────────────────────────────────────────────────────────────
def create_buttons(root, color, start_row, botoes):
    frame = tk.Frame(root)
    frame.grid(row=start_row, column=0, columnspan=5, padx=50)

    for chave_num in range(1, 16):
        chave_nome = f"Chave {chave_num:02d}"
        button_index = len(botoes)
        button = tk.Button(
            frame, text=chave_nome, bg=color, fg='white', width=10,
            command=lambda i=button_index, cn=chave_nome: registrar_evento(i, cn, color),
            highlightbackground='black', highlightthickness=2
        )
        button.original_color = color
        button.grid(row=(chave_num - 1) // 5, column=(chave_num - 1) % 5, padx=2, pady=2)
        botoes.append(button)


# ── Relatório em uso ──────────────────────────────────────────────────────────
def atualizar_relatorio_em_uso():
    conn = sqlite3.connect('chaves.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chave, cor, retirado_por, data_retirada FROM chaves
        WHERE retirado_por IS NOT NULL
    ''')
    rows = cursor.fetchall()
    conn.close()

    relatorio_em_uso.delete(1.0, END)
    if not rows:
        relatorio_em_uso.insert(END, "Nenhuma chave está em uso no momento.")
    else:
        for row in rows:
            chave, cor, retirado_por, data_retirada = row
            relatorio_em_uso.insert(END, f"{chave} (Cor: {cor}) — retirada por {retirado_por} em {data_retirada}\n")


# ── Gerar relatório ───────────────────────────────────────────────────────────
def gerar_relatorio():
    conn = sqlite3.connect('chaves.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chave, cor, evento, pessoa, usuario, data_evento FROM historico
        ORDER BY chave, data_evento
    ''')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("Relatório", "Nenhum evento registrado até o momento.")
        return

    relatorio_window = Toplevel()
    relatorio_window.title("Relatório de Chaves")
    relatorio_window.geometry("560x420")

    text_area = Text(relatorio_window, wrap='word', width=80, height=20)
    scroll_bar = Scrollbar(relatorio_window, orient=VERTICAL, command=text_area.yview)
    text_area.configure(yscrollcommand=scroll_bar.set)
    text_area.pack(side='left', fill='both', expand=True)
    scroll_bar.pack(side='right', fill='y')

    relatorio = "RELATÓRIO DE CHAVES — RETIRADAS E DEVOLUÇÕES\n"
    relatorio += "=" * 50 + "\n\n"
    chave_atual = None

    for row in rows:
        chave, cor, evento, pessoa, usuario, data_evento = row
        if chave != chave_atual:
            if chave_atual is not None:
                relatorio += "\n"
            relatorio += f"▸ {chave} (Cor: {cor})\n"
            chave_atual = chave
        pessoa_info = f" — {pessoa}" if pessoa else ""
        operador_info = f" [op: {usuario}]" if usuario else ""
        relatorio += f"   {evento}{pessoa_info}{operador_info} em {data_evento}\n"

    text_area.insert(END, relatorio)
    text_area.configure(state='disabled')


# ── Sistema principal ─────────────────────────────────────────────────────────
def abrir_sistema():
    global botoes, relatorio_em_uso

    root = tk.Tk()
    root.title(f"Quadro de Chaves — {usuario_logado}")
    root.geometry("600x520")

    for i in range(5):
        root.grid_columnconfigure(i, weight=1)
    root.grid_rowconfigure(8, weight=1)

    botoes = []

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    menu_bar.add_command(label="Gerar Relatório", command=gerar_relatorio)
    menu_bar.add_command(label="Resetar Estado das Chaves", command=resetar_estado_chaves)

    create_buttons(root, "green", 0, botoes)
    create_buttons(root, "blue", 3, botoes)
    create_buttons(root, "orange", 6, botoes)

    relatorio_em_uso = Text(root, height=5, wrap='word')
    relatorio_em_uso.grid(row=8, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')

    label_usuario = tk.Label(root, text=f"Usuário: {usuario_logado}", anchor='w', fg='gray')
    label_usuario.grid(row=9, column=0, columnspan=3, sticky='sw', padx=10, pady=4)

    label_direitos = tk.Label(root, text="Desenvolvido por @ReehCitelli", anchor='e', fg='gray')
    label_direitos.grid(row=9, column=2, columnspan=3, sticky='se', padx=10, pady=4)

    atualizar_relatorio_em_uso()
    root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    setup_database()
    tela_login()
