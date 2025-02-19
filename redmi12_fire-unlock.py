import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import queue
from pathlib import Path

# Get the script's directory
SCRIPT_DIR = Path(__file__).parent.absolute()

def check_required_files():
    required = ['mtk.py', 'requirements.txt']
    missing = []
    for f in required:
        if not (SCRIPT_DIR / f).exists():
            missing.append(f)
    if missing:
        messagebox.showerror("Error", f"Missing required files: {', '.join(missing)}")
        sys.exit(1)

check_required_files()

script_path = SCRIPT_DIR / "mtk.py"
requirements_path = SCRIPT_DIR / "requirements.txt"

class ModernScrollbar(ttk.Scrollbar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(style="Modern.Vertical.TScrollbar")

class UnlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Redmi 12 Unlock Tool")
        self.root.configure(bg="#0A0A0A")
        self.current_stage = 1
        self.running_process = None
        self.output_queue = queue.Queue()
        self.setup_styles()
        self.setup_ui()
        self.center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        self.style.configure("TButton", 
                            foreground="#FFFFFF",
                            background="#2A2A2A",
                            padding=12,
                            font=("Segoe UI", 11),
                            borderwidth=0,
                            relief="flat")
        self.style.map("TButton",
                    background=[('active', '#3A3A3A'), ('disabled', '#1A1A1A')],
                    foreground=[('active', '#00FF88'), ('disabled', '#505050')])
        
        self.style.configure("Modern.TFrame", background="#0A0A0A")
        self.style.configure("Terminal.TFrame", background="#000000")
        self.style.configure("Stage.TLabel", 
                           font=("Segoe UI", 12, "bold"),
                           foreground="#00FF88",
                           background="#0A0A0A")
        
        self.style.configure("Modern.Vertical.TScrollbar",
                           gripcount=0,
                           background="#404040",
                           troughcolor="#0A0A0A",
                           bordercolor="#0A0A0A",
                           arrowcolor="#00FF88",
                           lightcolor="#0A0A0A",
                           darkcolor="#0A0A0A")

        self.style.configure("Status.TLabel",
                           font=("Segoe UI", 9),
                           foreground="#00FF88",
                           background="#0A0A0A")

    def center_window(self):
        self.root.update_idletasks()
        window_width = 1000
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, style="Modern.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = ttk.Frame(main_container, style="Modern.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.header = ttk.Label(header_frame, 
                              text="REDMI 12 UNLOCK TOOL",
                              style="Stage.TLabel")
        self.header.pack(side=tk.LEFT)

        # Progress indicator
        self.stage_label = ttk.Label(header_frame, 
                                   text=f"Stage {self.current_stage}/4",
                                   style="Stage.TLabel")
        self.stage_label.pack(side=tk.RIGHT)

        # Content area
        content_frame = ttk.Frame(main_container, style="Modern.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel (Controls)
        control_frame = ttk.Frame(content_frame, width=250, style="Modern.TFrame")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        self.install_btn = ttk.Button(control_frame, 
                                    text="INSTALL DEPENDENCIES",
                                    command=self.install_dependencies)
        self.install_btn.pack(fill=tk.X, pady=5)

        self.unlock_btn = ttk.Button(control_frame, 
                                   text="START UNLOCK PROCESS",
                                   command=self.start_unlock_process)
        self.unlock_btn.pack(fill=tk.X, pady=5)

        # Right panel (Terminal)
        terminal_frame = ttk.Frame(content_frame, style="Terminal.TFrame")
        terminal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.cmd_output = tk.Text(terminal_frame, 
                                height=25,
                                width=80,
                                font=("Consolas", 10),
                                bg="#000000",
                                fg="#00FF88",
                                insertbackground="#00FF88",
                                selectbackground="#005500",
                                borderwidth=2,
                                relief="flat")
        scrollbar = ModernScrollbar(terminal_frame, 
                                  command=self.cmd_output.yview)
        self.cmd_output.configure(yscrollcommand=scrollbar.set)

        self.cmd_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar
        self.status_bar = ttk.Label(self.root, 
                                  text="Ready",
                                  style="Status.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

    def start_unlock_process(self):
        self.unlock_stage(1)

    def unlock_stage(self, stage):
        self.current_stage = stage
        self.stage_label.config(text=f"Stage {stage}/4")

        commands = {
            1: [sys.executable, str(script_path), "w", "lk_a", "lk.img"],
            2: [sys.executable, str(script_path), "w", "lk_b", "lk.img"],
            3: [sys.executable, str(script_path), "xflash", "seccfg", "unlock"],
            4: [sys.executable, str(script_path), "e", "userdata,metadata,md_udc,frp"]
        }

        messages = {
            1: "Writing lk_a partition...",
            2: "Writing lk_b partition...",
            3: "Unlocking security configuration...",
            4: "Formatting partitions..."
        }

        self.append_output(f"\n=== STAGE {stage}/4 ===\n", "stage")
        self.append_output(messages[stage] + "\n", "info")
        self.run_command(commands[stage], self.handle_stage_complete)

        btn_text = "CONTINUE" if stage < 4 else "COMPLETE"
        self.unlock_btn.config(text=f"{btn_text} ({stage}/4)", state=tk.DISABLED)

    def handle_stage_complete(self, success):
        if not success:
            self.append_output("Operation failed!\n", "error")
            self.unlock_btn.config(state=tk.NORMAL)
            return

        if self.current_stage < 4:
            self.current_stage += 1
            self.unlock_btn.config(
                text=f"CONTINUE ({self.current_stage}/4)",
                command=lambda: self.unlock_stage(self.current_stage),
                state=tk.NORMAL
            )
        else:
            self.append_output("Unlock process completed successfully!\n", "success")
            self.unlock_btn.config(state=tk.DISABLED)
            self.status_bar.config(text="Ready - Process completed")

    def install_dependencies(self):
        self.append_output("\n=== INSTALLING DEPENDENCIES ===\n", "stage")
        commands = [
            [sys.executable, "-m", "pip", "install", "-U", "pip"],
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        ]
        self.run_command(commands, self.handle_install_complete)

    def handle_install_complete(self, success):
        if success:
            self.append_output("Dependencies installed successfully!\n", "success")
            self.status_bar.config(text="Dependencies installed")
        else:
            self.append_output("Installation failed!\n", "error")
        self.install_btn.config(state=tk.NORMAL)

    def run_command(self, commands, callback):
        def worker():
            success = True
            for cmd in (commands if isinstance(commands[0], list) else [commands]):
                self.append_output(f"$ {' '.join(cmd)}\n", "command")
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True
                )
                self.running_process = process

                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.output_queue.put(('stdout', output))

                    err = process.stderr.readline()
                    if err:
                        self.output_queue.put(('stderr', err))

                process.wait()
                if process.returncode != 0:
                    success = False
                    break

            self.output_queue.put(('done', success))
            self.running_process = None

        self.toggle_buttons(False)
        threading.Thread(target=worker, daemon=True).start()
        self.poll_output_queue(callback)

    def poll_output_queue(self, callback):
        while not self.output_queue.empty():
            stream, output = self.output_queue.get()
            if stream == 'stderr':
                self.append_output(output, "error")
            else:
                self.append_output(output, "output")

        if self.running_process:
            self.root.after(100, lambda: self.poll_output_queue(callback))
        else:
            success = self.output_queue.get()[1] if not self.output_queue.empty() else False
            self.toggle_buttons(True)
            if callback:
                callback(success)

    def append_output(self, text, tag_type="output"):
        tag_config = {
            "error": {"foreground": "#FF4444", "font": ("Consolas", 10, "bold")},
            "success": {"foreground": "#00FF88", "font": ("Consolas", 10, "bold")},
            "stage": {"foreground": "#00FF88", "font": ("Consolas", 10, "bold")},
            "info": {"foreground": "#FFFFFF", "font": ("Consolas", 10)},
            "command": {"foreground": "#888888", "font": ("Consolas", 10)},
            "output": {"foreground": "#00FF88", "font": ("Consolas", 10)}
        }

        if tag_type not in self.cmd_output.tag_names():
            self.cmd_output.tag_configure(tag_type, **tag_config[tag_type])

        self.cmd_output.configure(state=tk.NORMAL)
        self.cmd_output.insert(tk.END, text, tag_type)
        self.cmd_output.see(tk.END)
        self.cmd_output.configure(state=tk.DISABLED)

    def toggle_buttons(self, enable):
        state = tk.NORMAL if enable else tk.DISABLED
        self.install_btn.config(state=state)
        self.unlock_btn.config(state=state)

    def on_close(self):
        if self.running_process:
            self.running_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnlockApp(root)
    root.mainloop()