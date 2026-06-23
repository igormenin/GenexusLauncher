import hashlib
import sys
import json
import os
import queue
import shutil
import subprocess
import threading
import urllib.request
import zipfile
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
try:
    import sv_ttk
    HAS_SV_THEME = True
except ImportError:
    HAS_SV_THEME = False

GITHUB_REPO = "igormenin/GenexusLauncher"

# Centralized theme and UI color configurations
# Common Theme Colors
ACCENT = '#0b5cab'
GROUP_BORDER = '#000000'
FALLBACK_WHITE = '#ffffff'

# Dark Theme Colors
DARK_WINDOW_BG = '#1c1c1c'
DARK_FG = '#ffffff'
DARK_LOG_BG = DARK_WINDOW_BG
DARK_LOG_FG = DARK_FG
DARK_CURSOR = DARK_FG
DARK_SELECT_BG = '#0078d4'
DARK_BTN_BG = '#2d2d2d'
DARK_BTN_FG = DARK_FG
DARK_BTN_BORDER = DARK_WINDOW_BG
DARK_BTN_ACTIVE = '#3d3d3d'
DARK_BTN_DISABLED = '#202020'
DARK_DIALOG_BG = '#1e1e1e'
DARK_DIALOG_FG = 'white'
DARK_DIALOG_TEXT_BG = DARK_BTN_BG
DARK_DIALOG_TEXT_FG = '#cccccc'
DARK_DIALOG_LINK_FG = '#5cacee'
DARK_DIALOG_INFO_FG = '#888888'

# Light Theme Colors
LIGHT_WINDOW_BG = '#f0f0f0'
LIGHT_FG = '#000000'
LIGHT_LOG_BG = '#ffffff' #'#f3f3f3'
LIGHT_LOG_FG = LIGHT_FG
LIGHT_CURSOR = LIGHT_FG
LIGHT_SELECT_BG = '#0078d7' #'#b3d7ff'
LIGHT_BTN_BG = '#e1e1e1' #'#e1e1e1'
LIGHT_BTN_FG = LIGHT_FG
LIGHT_BTN_BORDER = '#adadad' #'#cccccc'
LIGHT_BTN_LIGHTCOLOR = '#ffffff'
LIGHT_BTN_DARKCOLOR = '#cccccc' # '#bbbbbb'
LIGHT_BTN_ACTIVE = '#e5f1fb' #'#d0d0d0'
LIGHT_BTN_DISABLED = LIGHT_WINDOW_BG
LIGHT_DIALOG_BG = LIGHT_WINDOW_BG # '#ffffff'
LIGHT_DIALOG_FG = 'black'
LIGHT_DIALOG_TEXT_BG = LIGHT_LOG_BG
LIGHT_DIALOG_TEXT_FG = LIGHT_DIALOG_FG #'#333333'
LIGHT_DIALOG_LINK_FG = ACCENT
LIGHT_DIALOG_INFO_FG = '#838383' # '#666666'

THEME_COLORS = {
    'common': {
        'accent': ACCENT,
        'group_border': GROUP_BORDER,
        'fallback_white': FALLBACK_WHITE,
    },
    'dark': {
        'window_bg': DARK_WINDOW_BG,
        'fg': DARK_FG,
        'log_bg': DARK_LOG_BG,
        'log_fg': DARK_LOG_FG,
        'cursor': DARK_CURSOR,
        'select_bg': DARK_SELECT_BG,
        'btn_bg': DARK_BTN_BG,
        'btn_fg': DARK_BTN_FG,
        'btn_border': DARK_BTN_BORDER,
        'btn_active': DARK_BTN_ACTIVE,
        'btn_disabled': DARK_BTN_DISABLED,
        'dialog_bg': DARK_DIALOG_BG,
        'dialog_fg': DARK_DIALOG_FG,
        'dialog_text_bg': DARK_DIALOG_TEXT_BG,
        'dialog_text_fg': DARK_DIALOG_TEXT_FG,
        'dialog_link_fg': DARK_DIALOG_LINK_FG,
        'dialog_info_fg': DARK_DIALOG_INFO_FG,
    },
    'light': {
        'window_bg': LIGHT_WINDOW_BG,
        'fg': LIGHT_FG,
        'log_bg': LIGHT_LOG_BG,
        'log_fg': LIGHT_LOG_FG,
        'cursor': LIGHT_CURSOR,
        'select_bg': LIGHT_SELECT_BG,
        'btn_bg': LIGHT_BTN_BG,
        'btn_fg': LIGHT_BTN_FG,
        'btn_border': LIGHT_BTN_BORDER,
        'btn_lightcolor': LIGHT_BTN_LIGHTCOLOR,
        'btn_darkcolor': LIGHT_BTN_DARKCOLOR,
        'btn_active': LIGHT_BTN_ACTIVE,
        'btn_disabled': LIGHT_BTN_DISABLED,
        'dialog_bg': LIGHT_DIALOG_BG,
        'dialog_fg': LIGHT_DIALOG_FG,
        'dialog_text_bg': LIGHT_DIALOG_TEXT_BG,
        'dialog_text_fg': LIGHT_DIALOG_TEXT_FG,
        'dialog_link_fg': LIGHT_DIALOG_LINK_FG,
        'dialog_info_fg': LIGHT_DIALOG_INFO_FG,
    }
}

APP_TITLE = 'GeneXus Launcher'
# CORREÇÃO: Configuração que funciona com PyInstaller onefile
if getattr(sys, 'frozen', False) and getattr(sys, '_MEIPASS', False):
    # Executável PyInstaller - salva na pasta do usuário
    CONFIG_DIR = Path.home() / ".gxlauncher"
    CONFIG_FILE = CONFIG_DIR / "installations.json"
else:
    # Script Python normal - salva na mesma pasta
    CONFIG_FILE = Path(__file__).with_name('installations.json')

# Cria diretório se não existir
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
DEFAULT_OPEN_ARGS = ['/nolastkb', '/measurecommandtime', '/IdeStyle:silver']
GXMODULES_PATH = Path.home() / '.gxmodules'


def center_window(window, parent=None):
    window.update_idletasks()
    width = window.winfo_width() or window.winfo_reqwidth()
    height = window.winfo_height() or window.winfo_reqheight()
    if parent is not None and parent.winfo_exists():
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
    x = max(x, 0)
    y = max(y, 0)
    window.geometry(f'{width}x{height}+{x}+{y}')


class InstallationStore:
    def __init__(self, path: Path):
        self.path = path
        self.data = {'installations': [], 'last_selected_hash': None}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding='utf-8'))
                if 'installations' not in self.data or not isinstance(self.data['installations'], list):
                    self.data['installations'] = []
                if 'last_selected_hash' not in self.data:
                    self.data['last_selected_hash'] = None
            except Exception:
                self.data = {'installations': [], 'last_selected_hash': None}
        else:
            self.data = {'installations': [], 'last_selected_hash': None}

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding='utf-8')

    def get_all(self):
        return self.data['installations']

    def _generate_hash(self, name, path):
        content = f"{name}|{path}".lower()
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def is_path_duplicate(self, path, exclude_index=None):
        target_path = os.path.realpath(os.path.normpath(path)).lower()
        for i, inst in enumerate(self.data['installations']):
            if i == exclude_index:
                continue
            if os.path.realpath(os.path.normpath(inst['path'])).lower() == target_path:
                return True
        return False

    def add(self, item):
        item['hash'] = self._generate_hash(item['name'], item['path'])
        self.data['installations'].append(item)
        self.save()

    def update(self, index, item):
        item['hash'] = self._generate_hash(item['name'], item['path'])
        self.data['installations'][index] = item
        self.save()

    def delete(self, index):
        del self.data['installations'][index]
        self.save()

    def get_last_selected_hash(self):
        return self.data.get('last_selected_hash')

    def set_last_selected_hash(self, hash_value):
        self.data['last_selected_hash'] = hash_value
        self.save()

    def move(self, index, direction):
        # direction: -1 para cima, 1 para baixo
        new_index = index + direction
        if 0 <= new_index < len(self.data['installations']):
            self.data['installations'][index], self.data['installations'][new_index] = \
                self.data['installations'][new_index], self.data['installations'][index]
            self.save()
            return True
        return False


class InstallationDialog(tk.Toplevel):
    def __init__(self, master, initial=None, edit_index=None):
        super().__init__(master)
        self.title('Cadastro de instalação')
        self.resizable(False, False)
        self.result = None
        self.edit_index = edit_index
        self.transient(master)
        self.grab_set()

        initial = initial or {}

        self.name_var = tk.StringVar(value=initial.get('name', ''))
        self.path_var = tk.StringVar(value=initial.get('path', ''))
        self.ide_style_var = tk.StringVar(value=initial.get('ide_style', 'silver'))
        self.args_var = tk.StringVar(value=' '.join(initial.get('open_args', DEFAULT_OPEN_ARGS)))

        body = ttk.Frame(self, padding=14)
        body.grid(sticky='nsew')

        ttk.Label(body, text='Nome').grid(row=0, column=0, sticky='w', pady=(0, 4))
        ttk.Entry(body, textvariable=self.name_var, width=42).grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        ttk.Label(body, text='Pasta do GeneXus').grid(row=2, column=0, sticky='w', pady=(0, 4))
        ttk.Entry(body, textvariable=self.path_var, width=42).grid(row=3, column=0, sticky='ew', pady=(0, 10))
        ttk.Button(body, text='Procurar', command=self.browse).grid(row=3, column=1, padx=(8, 0), pady=(0, 10))

        ttk.Label(body, text='IdeStyle').grid(row=4, column=0, sticky='w', pady=(0, 4))
        ttk.Entry(body, textvariable=self.ide_style_var, width=42).grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        ttk.Label(body, text='Argumentos de abertura').grid(row=6, column=0, sticky='w', pady=(0, 4))
        ttk.Entry(body, textvariable=self.args_var, width=42).grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0, 12))

        buttons = ttk.Frame(body)
        buttons.grid(row=8, column=0, columnspan=2, sticky='e')
        ttk.Button(buttons, text='Cancelar', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Salvar', command=self.on_save).pack(side='right', padx=(0, 8))

        self.columnconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self.update_idletasks()
        center_window(self, master)

    def browse(self):
        selected = filedialog.askdirectory(title='Selecione a pasta do GeneXus')
        if selected:
            self.path_var.set(selected)
            if not self.name_var.get().strip():
                self.name_var.set(Path(selected).name)

    def on_save(self):
        gx_path = Path(self.path_var.get().strip())
        name = self.name_var.get().strip()
        ide_style = self.ide_style_var.get().strip() or 'silver'
        raw_args = self.args_var.get().strip()
        open_args = raw_args.split() if raw_args else DEFAULT_OPEN_ARGS

        if not name:
            messagebox.showerror(APP_TITLE, 'Informe um nome para a instalação.')
            return
        if not gx_path.exists() or not gx_path.is_dir():
            messagebox.showerror(APP_TITLE, 'Informe uma pasta válida do GeneXus.')
            return
        if not (gx_path / 'genexus.exe').exists():
            messagebox.showerror(APP_TITLE, 'Não foi encontrado genexus.exe na pasta informada.')
            return
        if not (gx_path / 'genexus.com').exists():
            messagebox.showerror(APP_TITLE, 'Não foi encontrado genexus.com na pasta informada.')
            return

        if self.master.store.is_path_duplicate(gx_path, self.edit_index):
            messagebox.showerror(APP_TITLE, 'Este caminho de instalação já está cadastrado.')
            return

        self.result = {
            'name': name,
            'path': str(gx_path),
            'ide_style': ide_style,
            'open_args': open_args,
        }
        
        # Extrai o ícone agora para salvar no JSON
        icon_data = self.master._extract_icon_data(gx_path / 'genexus.exe')
        if icon_data:
            self.result['icon_data'] = icon_data
            
        self.destroy()



class LoadingOverlay(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.withdraw()
        self.overrideredirect(True)
        self.attributes('-alpha', 0.6)
        self.configure(bg='black')
        self.transient(master)
        
        self.message_var = tk.StringVar(value="Processando...")
        
        # Central container
        container = tk.Frame(self, bg='black')
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Spinner Canvas
        self.canvas = tk.Canvas(container, width=50, height=50, bg='black', highlightthickness=0)
        self.canvas.pack(pady=10)
        self.arc = self.canvas.create_arc(5, 5, 45, 45, start=0, extent=120, outline=THEME_COLORS['common']['accent'], width=4, style='arc')
        
        # Message Label
        tk.Label(container, textvariable=self.message_var, fg='white', bg='black', font=('', 12, 'bold')).pack()
        
        self.angle = 0
        self.running = False
        
        # Sincroniza posição com a janela principal
        self.master.bind("<Configure>", self._reposition, add="+")

    def _reposition(self, event=None):
        if self.winfo_exists() and self.master.winfo_exists():
            x = self.master.winfo_rootx()
            y = self.master.winfo_rooty()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            self.geometry(f"{w}x{h}+{x}+{y}")

    def start_animation(self):
        if not self.running:
            self.running = True
            self._animate()

    def stop_animation(self):
        self.running = False

    def _animate(self):
        if self.running:
            self.angle = (self.angle + 10) % 360
            self.canvas.itemconfig(self.arc, start=self.angle)
            self.after(30, self._animate)

    def show(self, message="Processando..."):
        self.message_var.set(message)
        self._reposition()
        self.deiconify()
        self.lift()
        self.start_animation()
        self.update()



    def hide(self):
        self.stop_animation()
        self.withdraw()


class DriveSelectionDialog(tk.Toplevel):
    def __init__(self, master, drives):
        super().__init__(master)
        self.title("Selecionar Unidade")
        self.resizable(False, False)
        self.result = None
        self.transient(master)
        self.grab_set()

        body = ttk.Frame(self, padding=20)
        body.pack(fill='both', expand=True)

        ttk.Label(body, text="Em qual unidade deseja procurar o GeneXus?", font=('', 11)).pack(pady=(0, 15))
        
        self.drive_var = tk.StringVar(value=drives[0])
        combo = ttk.Combobox(body, textvariable=self.drive_var, values=drives, state='readonly', font=('', 11))
        combo.pack(fill='x', pady=(0, 20))

        btns = ttk.Frame(body)
        btns.pack(fill='x')
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side='right')
        ttk.Button(btns, text="Iniciar Busca", command=self.confirm).pack(side='right', padx=(0, 10))

        center_window(self, master)

    def confirm(self):
        self.result = self.drive_var.get()
        self.destroy()


class NamingDialog(tk.Toplevel):
    def __init__(self, master, path):
        super().__init__(master)
        self.title("Nomear Instalação")
        self.resizable(False, False)
        self.result = None
        self.transient(master)
        self.grab_set()

        body = ttk.Frame(self, padding=20)
        body.pack(fill='both', expand=True)

        ttk.Label(body, text="Instalação encontrada em:", font=('', 10, 'bold')).pack(anchor='w')
        lbl_path = ttk.Label(body, text=str(path), font=('', 9), foreground='gray', wraplength=400)
        lbl_path.pack(anchor='w', pady=(2, 15))

        ttk.Label(body, text="Nome para esta instalação:", font=('', 11)).pack(anchor='w')
        self.name_var = tk.StringVar(value=path.name)
        self.entry = ttk.Entry(body, textvariable=self.name_var, font=('', 11), width=45)
        self.entry.pack(fill='x', pady=(5, 20))
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        btns = ttk.Frame(body)
        btns.pack(fill='x')
        ttk.Button(btns, text="Pular", command=self.destroy).pack(side='right')
        ttk.Button(btns, text="Adicionar", command=self.confirm).pack(side='right', padx=(0, 10))

        center_window(self, master)

    def confirm(self):
        name = self.name_var.get().strip()
        if name:
            self.result = name
            self.destroy()


class UpdateDialog(tk.Toplevel):

    def __init__(self, master, version, notes, commits=None):
        super().__init__(master)
        self.withdraw()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Cores adaptativas baseadas no tema do master
        theme = getattr(master, 'theme', 'dark')
        colors = THEME_COLORS.get(theme, THEME_COLORS['dark'])
        bg_color = colors['dialog_bg']
        fg_color = colors['dialog_fg']
        text_bg = colors['dialog_text_bg']
        text_fg = colors['dialog_text_fg']
        link_fg = colors['dialog_link_fg']
        info_fg = colors['dialog_info_fg']

        self.configure(bg=bg_color)
        
        # Aumentado para 480x380 para comportar os novos textos e links com boa proporção
        w, h = 480, 380
        # Tenta centralizar
        try:
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        except Exception:
            x = (self.winfo_screenwidth() - w) // 2
            y = (self.winfo_screenheight() - h) // 2
            
        self.geometry(f"{w}x{h}+{x}+{y}")

        container = tk.Frame(self, bg=bg_color, padx=30, pady=30, highlightbackground=THEME_COLORS['common']['accent'], highlightthickness=2)
        container.pack(fill='both', expand=True)

        tk.Label(container, text="Atualização Obrigatória", fg=THEME_COLORS['common']['accent'], bg=bg_color, font=('', 16, 'bold')).pack(pady=(0, 15))
        tk.Label(container, text=f"Uma nova versão ({version}) está disponível.", fg=fg_color, bg=bg_color, font=('', 11)).pack(pady=(0, 10))

        # Lógica de processamento das notas de atualização e commits
        import re
        changelog_url = None
        notes_display = ""
        
        if notes:
            # Extrair link do GitHub se houver
            link_match = re.search(r'https://github.com/[^\s)]+', notes)
            if link_match:
                changelog_url = link_match.group(0)
                notes = notes.replace(changelog_url, "")
            
            # Limpeza do Markdown
            notes = re.sub(r'\*+Full Changelog\*+:\s*', "", notes)
            notes = notes.replace("**", "").strip()
            
            # Converte marcadores markdown para marcadores limpos
            lines = []
            for line in notes.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith(('-', '*')):
                    line = "• " + line[1:].strip()
                lines.append(line)
            notes_display = "\n".join(lines)
            
        if commits:
            commits_lines = [f"• {c}" for c in commits if c.strip()]
            if commits_lines:
                if notes_display:
                    notes_display += "\n\nAlterações detalhadas (Commits):\n" + "\n".join(commits_lines)
                else:
                    notes_display = "\n".join(commits_lines)

        # Fallback amigável se não houver notas nem commits
        if not notes_display or len(notes_display) < 6:
            notes_display = (
                "• Correções de bugs e melhorias gerais de estabilidade.\n"
                "• Otimizações internas e estabilização de processos."
            )
            
        if not changelog_url:
            # Reconstrói a URL do compare se não estiver nas notas
            prefix = "v" if version.lower().startswith('v') else ""
            changelog_url = f"https://github.com/{GITHUB_REPO}/compare/v{master._get_version()}...{prefix}{version}"

        notes_frame = tk.Frame(container, bg=text_bg, padx=5, pady=5)
        notes_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        txt = tk.Text(notes_frame, height=4, bg=text_bg, fg=text_fg, font=('', 10), borderwidth=0, highlightthickness=0)
        txt.insert('1.0', notes_display)
        txt.config(state='disabled')
        txt.pack(side='left', fill='both', expand=True)
        
        scroll = tk.Scrollbar(notes_frame, command=txt.yview)
        scroll.pack(side='right', fill='y')
        txt.config(yscrollcommand=scroll.set)

        # Exibir link clicável do GitHub
        if changelog_url:
            link_lbl = tk.Label(container, text="Ver log de alterações completo no GitHub", 
                                fg=link_fg, bg=bg_color, font=('', 9, 'underline'), cursor="hand2")
            link_lbl.pack(pady=(0, 10))
            link_lbl.bind("<Button-1>", lambda e: webbrowser.open(changelog_url))

        # Guia Informativo sobre a atualização automática
        info_lbl = tk.Label(container, 
                            text="Nota: O launcher será fechado temporariamente para baixar o novo executável.\nAo final do processo, você será notificado sobre a conclusão.", 
                            fg=info_fg, bg=bg_color, font=('', 8), justify='center')
        info_lbl.pack(pady=(0, 12))

        self.btn = tk.Button(container, text="INICIAR ATUALIZAÇÃO", bg=THEME_COLORS['common']['accent'], fg="white", font=('', 11, 'bold'), 
                             padx=20, pady=10, borderwidth=0, cursor="hand2", command=self.confirm)
        self.btn.pack(pady=(5, 0))
        
        self.deiconify()
        self.grab_set()

    def confirm(self):
        self.destroy()
        self.master.start_update_process()


class AboutDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Sobre o GeneXus Launcher")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        body = ttk.Frame(self, padding=20)
        body.pack(fill='both', expand=True)

        # Cabeçalho com ícone e título
        header_frame = ttk.Frame(body)
        header_frame.pack(fill='x', pady=(0, 15))

        # Se existir o ícone da aplicação, exibe-o redimensionado
        if master.app_icon:
            try:
                # O ícone original é 1200x1200px, subsample(12, 12) reduz para ~100x100px
                self.resized_icon = master.app_icon.subsample(12, 12)
                lbl_icon = ttk.Label(header_frame, image=self.resized_icon)
                lbl_icon.pack(side='left', padx=(0, 15))
            except Exception:
                pass

        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side='left', fill='both', expand=True)

        ttk.Label(info_frame, text="GeneXus Launcher", font=('', 16, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"Versão {master._get_version()}", font=('', 11), foreground='gray').pack(anchor='w')
        ttk.Label(info_frame, text="Desenvolvido por Igor Menin", font=('', 10, 'italic')).pack(anchor='w', pady=(4, 4))

        # Informações de Contato sob o autor
        contact_frame = ttk.Frame(info_frame)
        contact_frame.pack(anchor='w')

        ttk.Label(contact_frame, text="E-mail:", font=('', 9, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 5))
        ttk.Label(contact_frame, text="igormenin@gmail.com", font=('', 9)).grid(row=0, column=1, sticky='w')

        ttk.Label(contact_frame, text="GitHub:", font=('', 9, 'bold')).grid(row=1, column=0, sticky='w', padx=(0, 5))
        ttk.Label(contact_frame, text="github.com/igormenin", font=('', 9)).grid(row=1, column=1, sticky='w')

        # Linha divisória
        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)

        # Seção sobre as Tecnologias
        ttk.Label(body, text="Tecnologias Utilizadas", font=('', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        tech_frame = ttk.Frame(body)
        tech_frame.pack(fill='x', pady=(0, 10))

        technologies = [
            ("Python 3", "Linguagem base do projeto, versátil e multiplataforma."),
            ("Tkinter / Ttk", "Interface gráfica leve, nativa e sem dependências pesadas."),
            ("PowerShell", "Integração profunda para monitorar e validar processos no Windows."),
            ("PyInstaller", "Empacotamento do app em executável único auto-suficiente."),
            ("GitHub Actions", "Automatização de compilação (CI) e fluxo de deploy (CD).")
        ]

        for idx, (tech, desc) in enumerate(technologies):
            ttk.Label(tech_frame, text=f"• {tech}:", font=('', 9, 'bold')).grid(row=idx, column=0, sticky='w', pady=2, padx=(0, 5))
            ttk.Label(tech_frame, text=desc, font=('', 9), wraplength=320, justify='left').grid(row=idx, column=1, sticky='w', pady=2)

        # Botão de Fechar
        btn_close = ttk.Button(body, text="Fechar", command=self.destroy)
        btn_close.pack(anchor='e', pady=(10, 0))

        center_window(self, master)


class App(tk.Tk):


    def __init__(self):
        super().__init__()
        self.app_icon = None
        self._setup_window_icon()
        self.title(APP_TITLE)
        self.geometry('1200x650')
        self.minsize(1000, 560)

        self.store = InstallationStore(CONFIG_FILE)
        self.theme = 'dark'
        if HAS_SV_THEME:
            sv_ttk.set_theme(self.theme)

        self.log_queue = queue.Queue()
        self.running = False
        self.current_process = None
        self.installation_icons = {}
        self.fallback_icon = self._create_fallback_icon()
        self._load_button_icons()

        self._build_ui()
        self.loading = LoadingOverlay(self)
        self._load_installations()
        
        self._apply_theme_non_ttk()

        self.update_idletasks()
        center_window(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(150, self._drain_log_queue)
        self.after(1000, self.check_for_updates)



    def _setup_window_icon(self):
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent
                
            icon_path = base_path / "images" / "AppIcon.png"
            if icon_path.exists():
                self.app_icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, self.app_icon)
            else:
                self.log_queue.put(f'Aviso: ícone da janela não encontrado em {icon_path}')
        except Exception as exc:
            self.log_queue.put(f'Aviso: não foi possível carregar o ícone da janela: {exc}')

    def _load_button_icons(self):
        self.btn_icons = {}
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent
            
        icon_files = {
            'plus': 'plus.png',
            'delete': 'delete.png',
            'search': 'search.png',
            'up': 'up-arrow.png',
            'down': 'down-arrow.png',
            'update': 'cloud-download.png',
            'edit': 'edit.png',
            'info': 'botao-de-informacao.png',
            'sun': 'sun.png',
            'moon': 'moon.png'
        }



        for key, filename in icon_files.items():
            try:
                path = base_path / "images" / filename
                if path.exists():
                    self.btn_icons[key] = tk.PhotoImage(file=str(path))

            except Exception:
                pass


    def _get_version(self):
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent

            version_file = base_path / "version.config"
            if version_file.exists():
                return version_file.read_text().strip()
        except Exception:
            pass
        return "1.00"

    def on_closing(self):
        self.running = False
        if hasattr(self, 'current_process') and self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass
        self.destroy()
        sys.exit(0)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        root = ttk.Frame(self, padding=12)
        root.grid(sticky='nsew')
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=('', 11), rowheight=38)
        style.configure("Treeview.Heading", font=('', 11, 'bold'))

        self.left_frame = tk.LabelFrame(root, text='Instalações', font=('', 11, 'bold'), bd=0, highlightbackground=THEME_COLORS['common']['group_border'], highlightthickness=1, padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky='nsw', padx=(0, 10))
        self.left_frame.rowconfigure(0, weight=1)
        self.left_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.left_frame, show='tree', height=24)
        self.tree.column('#0', width=300)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        tree_scroll = ttk.Scrollbar(self.left_frame, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=tree_scroll.set)

        left_buttons = ttk.Frame(self.left_frame)
        left_buttons.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        left_buttons.columnconfigure(0, weight=1)
        left_buttons.columnconfigure(1, weight=1)

        self.move_up_btn = ttk.Button(left_buttons, text=' Mover p/ Cima', command=self.move_up_installation,
                                      image=self.btn_icons.get('up'), compound='left')

        self.move_up_btn.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        self.move_down_btn = ttk.Button(left_buttons, text=' Mover p/ Baixo', command=self.move_down_installation,
                                        image=self.btn_icons.get('down'), compound='left')


        self.move_down_btn.grid(row=0, column=1, sticky='ew', padx=(2, 0))

        ttk.Button(left_buttons, text=' Nova', command=self.add_installation,
                   image=self.btn_icons.get('plus'), compound='left').grid(row=1, column=0, sticky='ew', pady=(8, 0), padx=(0, 2))
        ttk.Button(left_buttons, text=' Buscar Instalações', command=self.start_auto_scan,
                   image=self.btn_icons.get('search'), compound='left').grid(row=1, column=1, sticky='ew', pady=(8, 0), padx=(2, 0))


        self.edit_btn = ttk.Button(left_buttons, text=' Editar', command=self.edit_installation,
                                   image=self.btn_icons.get('edit'), compound='left')

        self.edit_btn.grid(row=2, column=0, columnspan=2, sticky='ew', pady=6)
        self.remove_btn = ttk.Button(left_buttons, text=' Remover', command=self.remove_installation,
                                     image=self.btn_icons.get('delete'), compound='left')
        self.remove_btn.grid(row=3, column=0, columnspan=2, sticky='ew')


        right = ttk.Frame(root)
        right.grid(row=0, column=1, sticky='nsew')
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        self.details_frame = tk.LabelFrame(right, text='Detalhes e ações', font=('', 11, 'bold'), bd=0, highlightbackground=THEME_COLORS['common']['group_border'], highlightthickness=1, padx=12, pady=12)
        self.details_frame.grid(row=0, column=0, sticky='ew')
        self.details_frame.columnconfigure(1, weight=1)

        self.name_value = tk.StringVar(value='-')
        self.path_value = tk.StringVar(value='-')
        self.exe_value = tk.StringVar(value='-')
        self.com_value = tk.StringVar(value='-')
        self.lmgr_path_value = tk.StringVar(value='-')

        tk.Label(self.details_frame, text='Nome:', font=('', 10)).grid(row=0, column=0, sticky='w', pady=2)
        tk.Label(self.details_frame, textvariable=self.name_value, font=('', 10)).grid(row=0, column=1, sticky='w', pady=2)
        tk.Label(self.details_frame, text='Pasta:', font=('', 10)).grid(row=1, column=0, sticky='nw', pady=2)
        tk.Label(self.details_frame, textvariable=self.path_value, font=('', 10), wraplength=640, justify='left').grid(row=1, column=1, sticky='w', pady=2)
        tk.Label(self.details_frame, text='genexus.exe:', font=('', 10)).grid(row=2, column=0, sticky='w', pady=2)
        tk.Label(self.details_frame, textvariable=self.exe_value, font=('', 10), wraplength=640, justify='left').grid(row=2, column=1, sticky='w', pady=2)
        tk.Label(self.details_frame, text='genexus.com:', font=('', 10)).grid(row=3, column=0, sticky='w', pady=2)
        tk.Label(self.details_frame, textvariable=self.com_value, font=('', 10), wraplength=640, justify='left').grid(row=3, column=1, sticky='w', pady=2)
        tk.Label(self.details_frame, text='GxLMgr.exe:', font=('', 10)).grid(row=4, column=0, sticky='w', pady=2)
        tk.Label(self.details_frame, textvariable=self.lmgr_path_value, font=('', 10), wraplength=640, justify='left').grid(row=4, column=1, sticky='w', pady=2)

        actions = ttk.Frame(self.details_frame)
        actions.grid(row=5, column=0, columnspan=2, sticky='w', pady=(12, 0))
        self.clean_open_btn = ttk.Button(actions, text='Limpar e iniciar GeneXus', command=self.prepare_and_open_selected)
        self.clean_open_btn.grid(row=0, column=0, padx=(0, 8))
        self.open_btn = ttk.Button(actions, text='Só iniciar GeneXus', command=self.open_selected)
        self.open_btn.grid(row=0, column=1)
        self.open_folder_btn = ttk.Button(actions, text='Abrir Pasta', command=self.open_folder_selected)
        self.open_folder_btn.grid(row=0, column=2, padx=(8, 0))
        self.lmgr_btn = ttk.Button(actions, text='License Manager', command=self.open_license_manager)
        self.lmgr_btn.grid(row=0, column=3, padx=(8, 0))
        self.check_btn = ttk.Button(actions, text='Validar Instância', command=self.check_selected_instance)
        self.check_btn.grid(row=0, column=4, padx=(8, 0))

        self.log_frame = tk.LabelFrame(right, text='Log', font=('', 11, 'bold'), bd=0, highlightbackground=THEME_COLORS['common']['group_border'], highlightthickness=1, padx=10, pady=10)
        self.log_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(self.log_frame, wrap='word', height=18, state='disabled')
        self.log_text.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.log_text.config(yscrollcommand=scrollbar.set)

        footer_frame = ttk.Frame(root)
        footer_frame.grid(row=1, column=1, sticky='e', pady=(6, 0))

        self.footer_label = tk.Label(footer_frame, text=f"Desenvolvido por Igor Menin - v{self._get_version()}", font=('', 8), fg='gray')
        self.footer_label.pack(side='left', padx=(0, 10))

        self.manual_update_btn = ttk.Button(footer_frame, text="Verificar Atualização", 
                                            command=lambda: self.check_for_updates(manual=True), 
                                            style='Small.TButton', image=self.btn_icons.get('update'), compound='left')
        self.manual_update_btn.pack(side='left')

        self.about_btn = ttk.Button(footer_frame, text=" Sobre", 
                                    command=self.show_about, 
                                    style='Small.TButton', image=self.btn_icons.get('info'), compound='left')
        self.about_btn.pack(side='left', padx=(4, 0))

        # Botão de alternar tema desabilitado por enquanto
        # self.theme_btn = ttk.Button(root, image='', 
        #                             command=self.toggle_theme, 
        #                             style='Small.TButton')
        # self.theme_btn.grid(row=1, column=0, sticky='w', pady=(6, 0))

        # Estilo para o botão do rodapé ficar menor
        style.configure('Small.TButton', font=('', 7))


        self._set_buttons_state('disabled')

    def show_loading(self, message="Processando..."):
        self.loading.show(message)

    def hide_loading(self):
        self.loading.hide()

    def is_dev_env(self):
        import os
        is_frozen = getattr(sys, 'frozen', False)
        username = os.environ.get('USERNAME', '').lower()
        return (not is_frozen) or (username == 'igoragl')

    def check_for_updates(self, manual=False):
        # Evita buscas duplicadas se já encontramos uma atualização e estamos exibindo a tela ou baixando
        if hasattr(self, 'update_url') and self.update_url:
            return

        if not manual and self.is_dev_env():
            self.log("[Update] Busca automática de atualizações desativada no ambiente de desenvolvimento.")
            self.after(0, self._ask_initial_scan)
            return
            
        thread = threading.Thread(target=self._check_updates_worker, args=(manual,), daemon=True)
        thread.start()
        
        # Se for a busca automática, reagenda a verificação para daqui a 1 hora (3.600.000 ms)
        if not manual:
            self.after(3600000, lambda: self.check_for_updates(manual=False))

    def _check_updates_worker(self, manual=False):
        def parse_version(v_str):
            try:
                return tuple(int(x) for x in v_str.strip().split('.'))
            except Exception:
                return (0,)

        try:
            current_version = self._get_version()
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            
            req = urllib.request.Request(url)
            # GitHub exige User-Agent
            req.add_header('User-Agent', 'GXLauncher-Updater')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                remote_version = data['tag_name'].strip('vV')
                
                # Comparação inteligente de versão
                if parse_version(remote_version) > parse_version(current_version):
                    notes = data.get('body', '')
                    # Encontra o asset last_version.zip
                    asset_url = None
                    for asset in data.get('assets', []):
                        if asset['name'] == 'last_version.zip':
                            asset_url = asset['browser_download_url']
                            break
                    
                    if asset_url:
                        self.update_url = asset_url
                        
                        # Tenta obter a lista de commits entre as duas versões
                        commits_info = []
                        try:
                            remote_tag = data['tag_name']
                            prefix = "v" if remote_tag.lower().startswith('v') else ""
                            current_tag = f"{prefix}{current_version}"
                            
                            compare_api_url = f"https://api.github.com/repos/{GITHUB_REPO}/compare/{current_tag}...{remote_tag}"
                            compare_req = urllib.request.Request(compare_api_url)
                            compare_req.add_header('User-Agent', 'GXLauncher-Updater')
                            with urllib.request.urlopen(compare_req) as compare_res:
                                compare_data = json.loads(compare_res.read().decode())
                                for commit_obj in compare_data.get('commits', []):
                                    msg = commit_obj.get('commit', {}).get('message', '').splitlines()
                                    if msg:
                                        commits_info.append(msg[0].strip())
                        except Exception:
                            pass
                            
                        self.after(0, lambda: UpdateDialog(self, remote_version, notes, commits_info))
                        return # Sai pois a atualização tem prioridade
                
            # Se não houve atualização, verifica se precisa de scan inicial
            if manual:
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, "Você já está na versão mais recente!"))
            
            self.after(0, self._ask_initial_scan)
        except Exception as e:
            if manual:
                self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Falha na comunicação com o servidor:\n{e}"))
            # Se falhar a verificação, também tenta o scan inicial
            self.after(0, self._ask_initial_scan)

    def show_about(self):
        dialog = AboutDialog(self)
        self.wait_window(dialog)

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
        else:
            self.theme = "dark"
            
        if HAS_SV_THEME:
            sv_ttk.set_theme(self.theme)
        self.store.data['theme'] = self.theme
        self.store.save()
        self._apply_theme_non_ttk()

    def _apply_theme_non_ttk(self):
        style = ttk.Style()
        
        colors = THEME_COLORS.get(self.theme, THEME_COLORS['dark'])
        window_bg = colors['window_bg']
        fg_color = colors['fg']
        bg_color = colors['log_bg']
        cursor_color = colors['cursor']
        text_select_bg = colors['select_bg']
        
        # Configura cor de fundo da janela de acordo com o tema
        self.configure(bg=window_bg)
        style.configure('TFrame', background=window_bg)
        
        if self.theme == "dark":
            theme_icon = self.btn_icons.get('sun')
            theme_btn_text = "☀️" if not theme_icon else ""
            
            # Restaura o layout padrão do sv_ttk escuro para os botões
            style.layout('TButton', [
                ('Button.button', {'sticky': 'nswe', 'children': [
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'expand': '1', 'sticky': 'nswe'})
                    ]})
                ]})
            ])
            
            # Configurações de cores nativas do sv_ttk escuro
            style.configure('TButton', background=colors['btn_bg'], foreground=colors['btn_fg'], bordercolor=colors['btn_border'])
            style.map('TButton', background=[('active', colors['btn_active']), ('disabled', colors['btn_disabled'])])
        else:
            theme_icon = self.btn_icons.get('moon')
            theme_btn_text = "🌙" if not theme_icon else ""
            
            # Altera o layout do TButton no modo claro para usar elementos planos (permitindo cor sólida cinza)
            style.layout('TButton', [
                ('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [
                    ('Button.focus', {'sticky': 'nswe', 'children': [
                        ('Button.padding', {'sticky': 'nswe', 'children': [
                            ('Button.label', {'expand': '1', 'sticky': 'nswe'})
                        ]})
                    ]})
                ]})
            ])
            
            # Configura botões Ttk com fundo cinza no modo claro
            style.configure('TButton', 
                            background=colors['btn_bg'], 
                            foreground=colors['btn_fg'], 
                            bordercolor=colors['btn_border'], 
                            lightcolor=colors['btn_lightcolor'], 
                            darkcolor=colors['btn_darkcolor'])
            style.map('TButton', background=[('active', colors['btn_active']), ('disabled', colors['btn_disabled'])])
            
        # Configura os tk.LabelFrame e tk.Label usando a cor de fundo da janela (window_bg)
        group_border = THEME_COLORS['common']['group_border']
        if hasattr(self, 'left_frame') and self.left_frame.winfo_exists():
            self.left_frame.config(bg=window_bg, fg=fg_color, highlightbackground=group_border)
        if hasattr(self, 'details_frame') and self.details_frame.winfo_exists():
            self.details_frame.config(bg=window_bg, fg=fg_color, highlightbackground=group_border)
            for child in self.details_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=window_bg, fg=fg_color)
        if hasattr(self, 'log_frame') and self.log_frame.winfo_exists():
            self.log_frame.config(bg=window_bg, fg=fg_color, highlightbackground=group_border)
            
        if hasattr(self, 'theme_btn') and self.theme_btn.winfo_exists():
            self.theme_btn.config(image=theme_icon, text=theme_btn_text)
            
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.log_text.config(
                bg=bg_color,
                fg=fg_color,
                insertbackground=cursor_color,
                selectbackground=text_select_bg
            )
            
        if hasattr(self, 'footer_label') and self.footer_label.winfo_exists():
            self.footer_label.config(bg=window_bg)
            
        # Re-apply our specific Treeview and button style configurations that sv_ttk might override
        style.configure("Treeview", font=('', 11), rowheight=38)
        style.configure("Treeview.Heading", font=('', 11, 'bold'))
        style.configure('Small.TButton', font=('', 7))

    def start_auto_scan(self):
        drives = []
        try:
            # Obtém drives no Windows
            import string
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:\\")
                bitmask >>= 1
        except Exception:
            drives = ["C:\\"]

        if not drives:
            return

        selected_drive = drives[0]
        if len(drives) > 1:
            dialog = DriveSelectionDialog(self, drives)
            self.wait_window(dialog)
            if not dialog.result:
                return
            selected_drive = dialog.result

        self.show_loading(f"Buscando instalações em {selected_drive}...\n(Isto pode levar alguns minutos)")
        thread = threading.Thread(target=self._auto_scan_worker, args=(selected_drive,), daemon=True)
        thread.start()

    def _auto_scan_worker(self, root_path):
        found_paths = []
        ignore_folders = {'windows', '$recycle.bin', 'users', 'usuários', 'system volume information', 'programdata', 'temp'}
        
        try:
            for root, dirs, files in os.walk(root_path):
                # Filtra pastas ignoradas para não descer nelas
                dirs[:] = [d for d in dirs if d.lower() not in ignore_folders]
                
                if 'genexus.exe' in [f.lower() for f in files]:
                    # Verifica se também tem o gxlmgr.exe
                    if 'gxlmgr.exe' in [f.lower() for f in files]:
                        found_paths.append(Path(root))
        except Exception as e:
            self.log(f"Erro durante a varredura: {e}")

        self.after(0, self.hide_loading)
        if not found_paths:
            self.after(0, lambda: messagebox.showinfo(APP_TITLE, "Nenhuma instalação válida foi encontrada."))
        else:
            self.after(0, lambda: self._ask_names_sequential(found_paths))

    def _ask_names_sequential(self, paths):
        added_count = 0
        for path in paths:
            # Verifica se já está cadastrado
            if any(os.path.realpath(inst['path']).lower() == os.path.realpath(path).lower() for inst in self.store.get_all()):
                continue
                
            dialog = NamingDialog(self, path)
            self.wait_window(dialog)
            if dialog.result:
                item = {
                    'name': dialog.result,
                    'path': str(path),
                    'ide_style': 'silver',
                    'open_args': DEFAULT_OPEN_ARGS
                }
                # Extrai ícone
                icon_data = self._extract_icon_data(path / 'genexus.exe')
                if icon_data:
                    item['icon_data'] = icon_data
                
                self.store.add(item)
                added_count += 1
        
        if added_count > 0:
            self._load_installations()
            messagebox.showinfo(APP_TITLE, f"Sucesso! {added_count} instalações foram adicionadas.")
        else:
            messagebox.showinfo(APP_TITLE, "Nenhuma nova instalação foi encontrada.")


    def start_update_process(self):

        self.show_loading("Baixando atualização (0%)...")
        thread = threading.Thread(target=self._download_update_worker, daemon=True)
        thread.start()

    def _download_update_worker(self):
        try:
            target_path = Path("last_version.zip")
            
            def progress(count, block_size, total_size):
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    self.after(0, lambda: self.loading.message_var.set(f"Baixando atualização ({percent}%)..."))

            urllib.request.urlretrieve(self.update_url, str(target_path), reporthook=progress)
            
            self.after(0, lambda: self.loading.message_var.set("Finalizando..."))
            self._apply_update()
        except Exception as e:
            self.after(0, self.hide_loading)
            self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Erro no download: {e}"))

    def _apply_update(self):
        try:
            exe_path = sys.executable
            # Script batch para substituir arquivos. Removido o 'start' para evitar erro de DLL.
            bat_content = f"""@echo off
set EXE_NAME={Path(exe_path).name}
timeout /t 2 /nobreak > nul
taskkill /f /im "%EXE_NAME%" > nul 2>&1
powershell -Command "Expand-Archive -Path 'last_version.zip' -DestinationPath '.' -Force"
if exist "last_version.zip" del "last_version.zip"
powershell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Atualizacao concluida com sucesso!' + [char]10 + [char]10 + 'Voce ja pode iniciar o aplicativo novamente.', 'GeneXus Launcher')"

del "%~f0"
"""

            bat_path = Path("update_gx.bat")
            bat_path.write_text(bat_content, encoding='ansi')
            
            # Executa e fecha
            self._safe_popen([str(bat_path)], shell=True)
            self.after(0, self.on_closing)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(APP_TITLE, f"Erro ao aplicar: {e}"))
            self.after(0, self.hide_loading)


    def _create_fallback_icon(self):

        img = tk.PhotoImage(width=24, height=24)
        img.put(THEME_COLORS['common']['accent'], to=(0, 0, 23, 23))
        img.put(THEME_COLORS['common']['fallback_white'], to=(4, 4, 19, 19))
        img.put(THEME_COLORS['common']['accent'], to=(8, 8, 15, 15))
        return img

    def _icon_for_item(self, item):
        key = item['path']
        if key in self.installation_icons:
            return self.installation_icons[key]
        
        if 'icon_data' in item:
            try:
                img = tk.PhotoImage(width=32, height=32)
                for y, row_colors in enumerate(item['icon_data']):
                    # row_colors é uma lista de cores (ex: ["#ffffff", null, "#000000"])
                    for x, color in enumerate(row_colors):
                        if color:
                            # Preenche o pixel se não for transparente (null)
                            img.put(color, to=(x, y))
                self.installation_icons[key] = img
                return img
            except Exception:
                pass

        # Fallback se não houver dados ou falhar
        exe_path = Path(item['path']) / 'genexus.exe'
        if exe_path.exists():
            icon_data = self._extract_icon_data(exe_path)
            if icon_data:
                img = tk.PhotoImage(width=32, height=32)
                for y, row_data in enumerate(icon_data):
                    img.put(row_data, to=(0, y))
                self.installation_icons[key] = img
                return img

        return self.fallback_icon

    def _extract_icon_data(self, exe_path):
        """Extrai os dados de cor do ícone como uma lista de strings (uma por linha)"""
        try:
            if os.name != 'nt':
                return None
            import ctypes
            from ctypes import wintypes

            SHGFI_ICON = 0x100
            BI_RGB = 0
            DIB_RGB_COLORS = 0

            class SHFILEINFO(ctypes.Structure):
                _fields_ = [
                    ('hIcon', wintypes.HANDLE),
                    ('iIcon', ctypes.c_int),
                    ('dwAttributes', wintypes.DWORD),
                    ('szDisplayName', wintypes.WCHAR * 260),
                    ('szTypeName', wintypes.WCHAR * 80),
                ]

            class ICONINFO(ctypes.Structure):
                _fields_ = [
                    ('fIcon', wintypes.BOOL),
                    ('xHotspot', wintypes.DWORD),
                    ('yHotspot', wintypes.DWORD),
                    ('hbmMask', wintypes.HBITMAP),
                    ('hbmColor', wintypes.HBITMAP),
                ]

            class BITMAP(ctypes.Structure):
                _fields_ = [
                    ('bmType', ctypes.c_long),
                    ('bmWidth', ctypes.c_long),
                    ('bmHeight', ctypes.c_long),
                    ('bmWidthBytes', ctypes.c_long),
                    ('bmPlanes', ctypes.c_ushort),
                    ('bmBitsPixel', ctypes.c_ushort),
                    ('bmBits', ctypes.c_void_p),
                ]

            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ('biSize', wintypes.DWORD),
                    ('biWidth', ctypes.c_long),
                    ('biHeight', ctypes.c_long),
                    ('biPlanes', ctypes.c_ushort),
                    ('biBitCount', ctypes.c_ushort),
                    ('biCompression', wintypes.DWORD),
                    ('biSizeImage', wintypes.DWORD),
                    ('biXPelsPerMeter', ctypes.c_long),
                    ('biYPelsPerMeter', ctypes.c_long),
                    ('biClrUsed', wintypes.DWORD),
                    ('biClrImportant', wintypes.DWORD),
                ]

            class BITMAPINFO(ctypes.Structure):
                _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wintypes.DWORD * 3)]

            shell32 = ctypes.windll.shell32
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            shinfo = SHFILEINFO()
            res = shell32.SHGetFileInfoW(str(exe_path), 0, ctypes.byref(shinfo), ctypes.sizeof(shinfo), SHGFI_ICON)
            if not res or not shinfo.hIcon:
                return None

            hicon = shinfo.hIcon
            iconinfo = ICONINFO()
            
            hdc = None
            memdc = None
            rows = []
            try:
                if not user32.GetIconInfo(hicon, ctypes.byref(iconinfo)):
                    return None

                bmp = BITMAP()
                gdi32.GetObjectW(iconinfo.hbmColor, ctypes.sizeof(bmp), ctypes.byref(bmp))
                width, height = int(bmp.bmWidth), int(bmp.bmHeight)
                if width <= 0 or height <= 0:
                    width, height = 32, 32

                header = BITMAPINFOHEADER()
                header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
                header.biWidth = width
                header.biHeight = -height
                header.biPlanes = 1
                header.biBitCount = 32
                header.biCompression = BI_RGB

                bmi = BITMAPINFO()
                bmi.bmiHeader = header

                hdc = user32.GetDC(None)
                memdc = gdi32.CreateCompatibleDC(hdc)
                bits = (ctypes.c_ubyte * (width * height * 4))()
                copied = gdi32.GetDIBits(memdc, iconinfo.hbmColor, 0, height, ctypes.byref(bits), ctypes.byref(bmi), DIB_RGB_COLORS)

                if copied:
                    for y in range(height):
                        row = []
                        for x in range(width):
                            i = (y * width + x) * 4
                            b, g, r, a = bits[i], bits[i + 1], bits[i + 2], bits[i + 3]
                            if a == 0:
                                row.append(None)
                            else:
                                row.append(f'#{r:02x}{g:02x}{b:02x}')
                        rows.append(row)
                    return rows
                return None
            finally:
                if memdc:
                    gdi32.DeleteDC(memdc)
                if hdc:
                    user32.ReleaseDC(None, hdc)
                if iconinfo.hbmColor:
                    gdi32.DeleteObject(iconinfo.hbmColor)
                if iconinfo.hbmMask:
                    gdi32.DeleteObject(iconinfo.hbmMask)
                if hicon:
                    user32.DestroyIcon(hicon)
        except Exception:
            return None

    def _load_installations(self):
        for node in self.tree.get_children():
            self.tree.delete(node)
        
        items = self.store.get_all()
        needs_save = False
        last_hash = self.store.get_last_selected_hash()
        target_iid = None
        
        for idx, item in enumerate(items):
            # Migração: se não tem hash, gera e salva
            if 'hash' not in item:
                item['hash'] = self.store._generate_hash(item['name'], item['path'])
                needs_save = True

            # Migração: se não tem icon_data, tenta extrair e salvar
            if 'icon_data' not in item:
                exe_path = Path(item['path']) / 'genexus.exe'
                if exe_path.exists():
                    data = self._extract_icon_data(exe_path)
                    if data:
                        item['icon_data'] = data
                        needs_save = True
            
            iid = str(idx)
            self.tree.insert('', 'end', iid=iid, text=item['name'], image=self._icon_for_item(item))
            
            if last_hash and item.get('hash') == last_hash:
                target_iid = iid
        
        if needs_save:
            self.store.save()
            
        all_items = self.tree.get_children()
        if all_items:
            # Seleciona o alvo do hash, ou o primeiro se não encontrado
            selection = target_iid if target_iid and target_iid in all_items else all_items[0]
            self.tree.selection_set(selection)
            self.on_select()
        else:
            self.on_select()


    def _ask_initial_scan(self):
        if not self.store.get_all():
            if messagebox.askyesno(APP_TITLE, "Nenhuma instalação foi encontrada.\nDeseja realizar uma varredura automática no computador?"):
                self.start_auto_scan()


    def _set_buttons_state(self, state):
        self.clean_open_btn.config(state=state)
        self.open_btn.config(state=state)
        self.open_folder_btn.config(state=state)
        self.lmgr_btn.config(state=state)
        self.check_btn.config(state=state)
        self.edit_btn.config(state=state)
        self.remove_btn.config(state=state)
        self.move_up_btn.config(state=state)
        self.move_down_btn.config(state=state)

    def _selected_index(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def _selected_item(self):
        idx = self._selected_index()
        if idx is None:
            return None, None
        items = self.store.get_all()
        if idx < 0 or idx >= len(items):
            return None, None
        return idx, items[idx]

    def on_select(self, event=None):
        idx, item = self._selected_item()
        if not item:
            self.name_value.set('')
            self.path_value.set('')
            self.exe_value.set('')
            self.com_value.set('')
            self.lmgr_path_value.set('')
            self._set_buttons_state('disabled')
            return

        gx_path = Path(item['path'])
        self.name_value.set(item['name'])
        self.path_value.set(str(gx_path))
        self.exe_value.set(str(gx_path / 'genexus.exe'))
        self.com_value.set(str(gx_path / 'genexus.com'))
        self.lmgr_path_value.set(str(gx_path / 'GxLMgr.exe'))
        self._set_buttons_state('normal' if not self.running else 'disabled')
        
        # Ajuste fino dos botões de movimento
        if not self.running:
            self.move_up_btn.config(state='normal' if idx > 0 else 'disabled')
            self.move_down_btn.config(state='normal' if idx < len(self.tree.get_children()) - 1 else 'disabled')

    def add_installation(self):
        dialog = InstallationDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.store.add(dialog.result)
            self.installation_icons.pop(dialog.result['path'], None)
            self._load_installations()
            items = self.tree.get_children()
            if items:
                self.tree.selection_set(items[-1])
                self.on_select()
            self.log(f'Instalação "{dialog.result["name"]}" cadastrada.')

    def edit_installation(self):
        idx, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        old_path = item['path']
        dialog = InstallationDialog(self, initial=item, edit_index=idx)
        self.wait_window(dialog)
        if dialog.result:
            self.store.update(idx, dialog.result)
            self.installation_icons.pop(old_path, None)
            self.installation_icons.pop(dialog.result['path'], None)
            self._load_installations()
            self.tree.selection_set(str(idx))
            self.on_select()
            self.log(f'Instalação "{dialog.result["name"]}" atualizada.')

    def remove_installation(self):
        idx, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        if messagebox.askyesno(APP_TITLE, f'Remover a instalação "{item["name"]}"?'):
            self.installation_icons.pop(item['path'], None)
            self.store.delete(idx)
            self._load_installations()
            self.log('Instalação removida.')

    def move_up_installation(self):
        idx = self._selected_index()
        if idx is not None and idx > 0:
            if self.store.move(idx, -1):
                self._load_installations()
                self.tree.selection_set(str(idx - 1))
                self.on_select()

    def move_down_installation(self):
        idx = self._selected_index()
        if idx is not None and idx < len(self.tree.get_children()) - 1:
            if self.store.move(idx, 1):
                self._load_installations()
                self.tree.selection_set(str(idx + 1))
                self.on_select()

    def open_selected(self):
        _, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        
        self.show_loading("Iniciando GeneXus...")
        thread = threading.Thread(target=self._open_selected_worker, args=(item,), daemon=True)
        thread.start()

    def _open_selected_worker(self, item):
        try:
            self.log(f"--- Iniciando GeneXus: {item['name']} ---")
            
            # Validação de segurança: não permite abrir versões diferentes simultaneamente
            running_paths = self._get_running_genexus_paths()
            if running_paths:
                target_path = os.path.realpath(os.path.normpath(item['path'])).lower()
                for p in running_paths:
                    if p != target_path:
                        self.after(0, lambda: messagebox.showerror(APP_TITLE,
                            "Conflito de Versões!\n\n"
                            "Já existe uma instância de uma VERSÃO DIFERENTE do GeneXus rodando.\n"
                            "Feche a versão atual e inicie pelo botão de Limpar e Iniciar Genexus."))
                        return

            self._open_genexus(item)
            self.store.set_last_selected_hash(item.get('hash'))
            self.log(f'Aberto: {item["name"]}')
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror(APP_TITLE, str(exc)))
            self.log(f'Erro ao abrir GeneXus: {exc}')
        finally:
            # Pequeno delay para o feedback visual não sumir instantaneamente
            self.after(1500, self.hide_loading)


    def check_selected_instance(self):
        _, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return

        self.show_loading("Validando Instância...")
        thread = threading.Thread(target=self._check_selected_worker, args=(item,), daemon=True)
        thread.start()

    def _check_selected_worker(self, item):
        try:
            self.log(f"--- Validando Instância: {item['name']} ---")
            target_path = os.path.realpath(os.path.normpath(item['path'])).lower()
            self.log(f"Caminho esperado: {target_path}")
            
            running_paths = self._get_running_genexus_paths()
            if not running_paths:
                self.log("Nenhuma instância de GeneXus detectada rodando.")
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, "Nenhuma instância do GeneXus está rodando no momento."))
                return

            conflicts = []
            for p in running_paths:
                if p != target_path:
                    conflicts.append(p)
            
            if conflicts:
                self.log(f"CONFLITO DETECTADO! Instâncias diferentes: {', '.join(conflicts)}")
                self.after(0, lambda: messagebox.showerror(APP_TITLE, 
                    f"Conflito Detectado!\n\n"
                    f"Você selecionou: {item['name']}\n"
                    f"Mas existem instâncias de OUTRAS pastas rodando:\n\n" + "\n".join(conflicts)))
            else:
                self.log("Instância validada. Apenas versões compatíveis estão rodando.")
                self.after(0, lambda: messagebox.showinfo(APP_TITLE, "Tudo certo! As instâncias abertas pertencem à mesma pasta desta instalação."))
        finally:
            self.after(0, self.hide_loading)


    def open_license_manager(self):
        _, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        try:
            gx_path = Path(item['path'])
            gxlmgr_exe = gx_path / 'GxLMgr.exe'
            if not gxlmgr_exe.exists():
                raise FileNotFoundError(f'Arquivo não encontrado: {gxlmgr_exe}')
            
            self._safe_popen([str(gxlmgr_exe)], cwd=str(gx_path), shell=False)
            self.log(f'Aberto: License Manager ({item["name"]})')
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            self.log(f'Erro ao abrir License Manager: {exc}')

    def open_folder_selected(self):
        _, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        try:
            gx_path = Path(item['path'])
            if not gx_path.exists():
                raise FileNotFoundError(f'Pasta não encontrada: {gx_path}')
            
            os.startfile(str(gx_path))
            self.log(f'Pasta aberta: {gx_path}')
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            self.log(f'Erro ao abrir pasta: {exc}')

    def prepare_and_open_selected(self):
        _, item = self._selected_item()
        if item is None:
            messagebox.showwarning(APP_TITLE, 'Selecione uma instalação.')
            return
        if self.running:
            return

        self.log(f"--- Limpando e Iniciando: {item['name']} ---")
            
        # Validação de segurança: não permite limpar se houver qualquer GeneXus aberto
        running_paths = self._get_running_genexus_paths()
        if running_paths:
            messagebox.showwarning(APP_TITLE, 
                "Ação Bloqueada!\n\n"
                "Já existe uma instância do GeneXus em execução.\n"
                "Para evitar danos à instância atual, a funcionalidade de limpeza não será executada.")
            return

        self.running = True
        self._set_buttons_state('disabled')
        self.show_loading("Limpando e Iniciando...")
        thread = threading.Thread(target=self._prepare_worker, args=(item,), daemon=True)
        thread.start()


    def _prepare_worker(self, item):
        try:
            gx_path = Path(item['path'])
            genexus_com = gx_path / 'genexus.com'
            if not genexus_com.exists():
                raise FileNotFoundError(f'Arquivo não encontrado: {genexus_com}')

            self.log('---------------------')
            self.log(f'Preparando instalação: {item["name"]}')
            self.log('---------------------')
            self.log(f'Excluindo pasta {GXMODULES_PATH}')
            shutil.rmtree(GXMODULES_PATH, ignore_errors=True)

            self.log('')
            self.log('---------------------')
            self.log('Genexus Install...')
            self.log('---------------------')
            self.log('')

            command = [str(genexus_com), '/install']
            self._stream_process(command, cwd=str(gx_path))

            self.log('')
            self.log('---------------------')
            self.log('Running Genexus')
            self.log('---------------------')
            self.log('')
            self._open_genexus(item)
            self.store.set_last_selected_hash(item.get('hash'))
            self.log('GeneXus iniciado com sucesso.')
        except Exception as exc:
            self.log(f'ERRO: {exc}')
            self.after(0, lambda: messagebox.showerror(APP_TITLE, str(exc)))
        finally:
            self.running = False
            self.after(0, self.hide_loading)
            self.after(0, self.on_select)


    def _safe_popen(self, command, **kwargs):
        """Spawns a subprocess with a cleaned environment and DLL search path to prevent
        the child process from locking the PyInstaller temporary directory (_MEIPASS)."""
        import ctypes
        
        env = kwargs.get("env")
        if env is None:
            env = os.environ.copy()
        else:
            env = env.copy()
            
        if "_MEIPASS" in env:
            del env["_MEIPASS"]
            
        is_frozen = getattr(sys, 'frozen', False)
        if is_frozen and hasattr(sys, '_MEIPASS'):
            bundle_dir = sys._MEIPASS
            if "PATH" in env:
                paths = env["PATH"].split(os.pathsep)
                env["PATH"] = os.pathsep.join(
                    [p for p in paths if p.lower() != bundle_dir.lower()]
                )
                
        kwargs["env"] = env
        kwargs["close_fds"] = True
        
        if is_frozen and os.name == "nt":
            try:
                ctypes.windll.kernel32.SetDllDirectoryW(None)
            except Exception:
                pass
                
        try:
            return subprocess.Popen(command, **kwargs)
        finally:
            if is_frozen and os.name == "nt" and hasattr(sys, '_MEIPASS'):
                try:
                    ctypes.windll.kernel32.SetDllDirectoryW(sys._MEIPASS)
                except Exception:
                    pass

    def _open_genexus(self, item):
        gx_path = Path(item['path'])
        genexus_exe = gx_path / 'genexus.exe'
        if not genexus_exe.exists():
            raise FileNotFoundError(f'Arquivo não encontrado: {genexus_exe}')
        args = item.get('open_args') or DEFAULT_OPEN_ARGS
        
        self._safe_popen([str(genexus_exe), *args], cwd=str(gx_path), shell=False)

    def _stream_process(self, command, cwd=None):
        kwargs = {
            "cwd": cwd,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "universal_newlines": True,
            "shell": False,
        }

        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        self.current_process = self._safe_popen(command, **kwargs)
        process = self.current_process

        assert process.stdout is not None
        for line in process.stdout:
            self.log(line.rstrip())

        code = process.wait()
        if code != 0:
            raise RuntimeError(f'Comando falhou com código {code}: {" ".join(command)}')

    def _get_running_genexus_paths(self):
        """Retorna uma lista de pastas únicas onde o genexus.exe está rodando no momento"""
        try:
            # Usa PowerShell que é mais confiável e insensível a maiúsculas/minúsculas
            cmd = 'powershell -NoProfile -Command "Get-Process | Where-Object { $_.ProcessName -eq \'GeneXus\' } | Where-Object { $_.Path -ne $null } | ForEach-Object { $_.Path }"'
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
            paths = []
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Normalização rigorosa do caminho
                    full_path = os.path.realpath(os.path.normpath(line))
                    folder = os.path.dirname(full_path).lower()
                    paths.append(folder)
                except Exception:
                    continue
            
            detected = list(set(paths))
            if detected:
                # Log silencioso ou informativo sobre o que foi encontrado
                self.log(f"[Info] Instâncias ativas detectadas em: {', '.join(detected)}")
            return detected
        except Exception as e:
            self.log(f"[Erro] Falha ao verificar processos: {e}")
            return []

    def log(self, message):
        self.log_queue.put(message)

    def _drain_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.config(state='disabled')
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.after(150, self._drain_log_queue)


if __name__ == '__main__':
    app = App()
    app.mainloop()