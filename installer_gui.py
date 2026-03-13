import os
import sys
import subprocess
import ctypes
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32com.client
import shutil

if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MineControlInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("MineControl Bot - Master Installer")
        self.root.geometry("500x580")
        self.root.resizable(False, False)

        # --- УСТАНОВКА ИКОНКИ ОКНА ---
        try:
            # Ищем файл icon.ico внутри ресурсов
            icon_file = resource_path("icon.ico")
            if os.path.exists(icon_file):
                self.root.iconbitmap(icon_file)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")

        self.server_dir = tk.StringVar(value="C:\\MineControlBot")
        self.mc_server_path = tk.StringVar(value="C:\\Server")
        self.bot_token = tk.StringVar(value="")
        self.admin_id = tk.StringVar(value="")
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.add_to_startup = tk.BooleanVar(value=False)

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=5)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Установка MineControl Bot", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        ttk.Label(main_frame, text="Токен бота (от @BotFather):").pack(anchor=tk.W)
        ttk.Entry(main_frame, textvariable=self.bot_token, show="*").pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Ваш Telegram ID (ID админа):").pack(anchor=tk.W)
        ttk.Entry(main_frame, textvariable=self.admin_id).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Куда установить файлы бота:").pack(anchor=tk.W)
        path_bot_frame = ttk.Frame(main_frame)
        path_bot_frame.pack(fill=tk.X, pady=(5, 10))
        ttk.Entry(path_bot_frame, textvariable=self.server_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_bot_frame, text="Обзор...", command=lambda: self.browse_folder(self.server_dir)).pack(
            side=tk.RIGHT)

        ttk.Label(main_frame, text="Папка с сервером Minecraft:").pack(anchor=tk.W)
        path_mc_frame = ttk.Frame(main_frame)
        path_mc_frame.pack(fill=tk.X, pady=(5, 15))
        ttk.Entry(path_mc_frame, textvariable=self.mc_server_path).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                        padx=(0, 5))
        ttk.Button(path_mc_frame, text="Обзор...", command=lambda: self.browse_folder(self.mc_server_path)).pack(
            side=tk.RIGHT)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Checkbutton(main_frame, text="Создать ярлык на рабочем столе", variable=self.create_desktop_shortcut).pack(
            anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Добавить в автозагрузку Windows", variable=self.add_to_startup).pack(
            anchor=tk.W, pady=2)

        ttk.Label(main_frame, text="Статус:", font=("Arial", 8, "italic")).pack(anchor=tk.W, pady=(15, 0))
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.install_btn = ttk.Button(main_frame, text="УСТАНОВИТЬ", command=self.run_installation)
        self.install_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    def browse_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(os.path.normpath(folder))

    def create_shortcut(self, target_path, shortcut_path, description):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.Description = description
            shortcut.IconLocation = target_path
            shortcut.save()
        except Exception as e:
            print(f"Shortcut error: {e}")

    def run_installation(self):
        if not self.bot_token.get().strip():
            if not messagebox.askyesno("Внимание", "Вы не указали токен бота. Уверены, что хотите продолжить?"):
                return

        self.install_btn.config(state=tk.DISABLED)
        self.root.update()

        target_dir = self.server_dir.get()
        mc_dir = self.mc_server_path.get()

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

            self.progress['value'] = 20
            self.root.update()

            rcon_password = ""
            rcon_port = 25575
            server_props_path = os.path.join(mc_dir, "server.properties")

            if os.path.exists(server_props_path):
                with open(server_props_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("rcon.password="):
                            rcon_password = line.strip().split("=", 1)[1]
                        elif line.startswith("rcon.port="):
                            rcon_port = int(line.strip().split("=", 1)[1])

            config_data = {
                "bot_token": self.bot_token.get().strip(),
                "admin_id": self.admin_id.get().strip(),
                "server_dir": mc_dir,
                "install_path": target_dir,
                "rcon_password": rcon_password,
                "rcon_port": rcon_port,
                "bot_version": "1.0.0"
            }
            with open(os.path.join(target_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            self.progress['value'] = 40
            self.root.update()

            internal_bot_exe = resource_path("control.exe")
            final_bot_path = os.path.join(target_dir, "control.exe")

            if os.path.exists(internal_bot_exe):
                shutil.copy2(internal_bot_exe, final_bot_path)
            else:
                ext_bot = os.path.join(os.path.dirname(sys.argv[0]), "control.exe")
                if os.path.exists(ext_bot):
                    shutil.copy2(ext_bot, final_bot_path)
                else:
                    raise FileNotFoundError("Файл control.exe не найден.")

            self.progress['value'] = 80
            self.root.update()

            if self.create_desktop_shortcut.get():
                desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
                self.create_shortcut(final_bot_path, os.path.join(desktop, "MineControl Bot.lnk"),
                                     "Управление сервером Minecraft")

            if self.add_to_startup.get():
                startup = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows',
                                       'Start Menu', 'Programs', 'Startup')
                self.create_shortcut(final_bot_path, os.path.join(startup, "MineControlBot.lnk"), "Автозапуск бота")

            self.progress['value'] = 100
            messagebox.showinfo("Успех", f"Установка завершена!\nБот установлен в: {target_dir}")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить установку: {e}")
            self.install_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = MineControlInstaller(root)
    root.mainloop()