# game_of_life_app.py
import tkinter as tk
from tkinter import font
import threading
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from game_of_life_2d import GameOfLife2D
from game_of_life_1d import GameOfLife1D


BG_COLOR = "#f0f5ff"
PLOT_BG = "#e6eeff"


class GameOfLifeApp:
    def __init__(self, root):
        self.root = root
        root.title("🧫 Juego de la Vida - Autómatas Celulares")
        root.geometry("1050x680")
        root.configure(bg=BG_COLOR)

        self.base_font = font.Font(family="Segoe UI", size=10)
        self.title_font = font.Font(family="Segoe UI", size=11, weight="bold")

        # Notebook
        self.nb = tk.Frame(root, bg=BG_COLOR)
        self.nb.pack(fill='both', expand=True, padx=15, pady=15)

        self._build_2d_tab()
        self._build_1d_tab()

    def _create_control_panel(self, parent, title):
        panel = tk.Frame(parent, bg="white", relief="flat", bd=0)
        panel.pack(side='left', fill='y', padx=(0, 15), pady=10)
        
        title_label = tk.Label(panel, text=title, bg="white", fg="#212529",
                               font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=(15, 20))
        
        return panel

    def _styled_label(self, parent, text):
        label = tk.Label(parent, text=text, bg="white", fg="#495057",
                         font=self.base_font, anchor="w")
        label.pack(fill='x', padx=15, pady=(12, 2))
        return label

    def _styled_entry(self, parent, text_var):
        entry = tk.Entry(parent, textvariable=text_var, font=self.base_font,
                         relief="solid", bd=1, width=10)
        entry.pack(fill='x', padx=15, pady=(0, 12))
        return entry

    def _styled_button(self, parent, text, cmd, bg="#4361ee", fg="white", width=20):
        btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                        font=self.base_font, relief="flat", cursor="hand2",
                        height=2, width=width)
        btn.pack(fill='x', padx=15, pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._darken(bg)))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _darken(self, hex_color, factor=0.85):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_2d_tab(self):
        tab = tk.Frame(self.nb, bg=BG_COLOR)
        tab.pack(fill='both', expand=True)

        left = self._create_control_panel(tab, "Configuración 2D")
        right = tk.Frame(tab, bg=BG_COLOR)
        right.pack(side='right', fill='both', expand=True)

        self.g2_rows = tk.IntVar(value=50)
        self.g2_cols = tk.IntVar(value=50)
        self.g2_p = tk.DoubleVar(value=0.2)

        self._styled_label(left, "Filas:")
        self._styled_entry(left, self.g2_rows)
        self._styled_label(left, "Columnas:")
        self._styled_entry(left, self.g2_cols)
        self._styled_label(left, "Probabilidad inicial:")
        self._styled_entry(left, self.g2_p)

        self._styled_button(left, "Crear aleatorio", self._g2_create, "#4361ee")
        self._styled_button(left, "Paso", self._g2_step, "#6c757d")
        self._styled_button(left, "Ejecutar / Parar", self._g2_toggle, "#2ecc71")
        self._styled_button(left, "Limpiar", self._g2_clear, "#e63946")

        fig = Figure(figsize=(6, 6), facecolor=BG_COLOR)
        self.g2_ax = fig.add_subplot(111)
        self.g2_ax.set_facecolor(PLOT_BG)
        self.g2_canvas = FigureCanvasTkAgg(fig, master=right)
        self.g2_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

        self.g2 = None
        self.g2_running = False

    def _g2_create(self):
        rows = max(5, int(self.g2_rows.get()))
        cols = max(5, int(self.g2_cols.get()))
        p = float(self.g2_p.get())
        self.g2 = GameOfLife2D(rows, cols)
        self.g2.randomize(p)
        self._g2_draw()

    def _g2_draw(self):
        self.g2_ax.clear()
        self.g2_ax.imshow(self.g2.grid, interpolation='nearest', cmap='gray_r')
        self.g2_ax.set_title('Juego de la Vida 2D', fontsize=12, pad=10)
        self.g2_ax.axis('off')
        self.g2_canvas.draw()

    def _g2_step(self):
        if self.g2 is None:
            self._g2_create()
        self.g2.step()
        self._g2_draw()

    def _g2_toggle(self):
        self.g2_running = not self.g2_running
        if self.g2_running:
            self._g2_run_loop()

    def _g2_run_loop(self):
        def loop():
            while self.g2_running:
                time.sleep(0.1)
                try:
                    self._g2_step()
                except:
                    self.g2_running = False
        threading.Thread(target=loop, daemon=True).start()

    def _g2_clear(self):
        if self.g2 is not None:
            self.g2.grid = np.zeros_like(self.g2.grid)
            self._g2_draw()

    def _build_1d_tab(self):
        tab = tk.Frame(self.nb, bg=BG_COLOR)
        tab.pack(fill='both', expand=True)

        left = self._create_control_panel(tab, "Configuración 1D")
        right = tk.Frame(tab, bg=BG_COLOR)
        right.pack(side='right', fill='both', expand=True)

        self.g1_len = tk.IntVar(value=300)
        self.g1_rule = tk.IntVar(value=30)

        self._styled_label(left, "Longitud del autómata:")
        self._styled_entry(left, self.g1_len)
        self._styled_label(left, "Regla (0–255):")
        self._styled_entry(left, self.g1_rule)

        self._styled_button(left, "Crear patrón inicial", self._g1_create, "#4361ee")
        self._styled_button(left, "Siguiente paso", self._g1_step, "#6c757d")
        self._styled_button(left, "Ejecutar 200 pasos", self._g1_run, "#2ecc71")

        fig = Figure(figsize=(8, 5), facecolor=BG_COLOR)
        self.g1_ax = fig.add_subplot(111)
        self.g1_ax.set_facecolor(PLOT_BG)
        self.g1_canvas = FigureCanvasTkAgg(fig, master=right)
        self.g1_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

        self.g1 = None
        self.g1_hist = []

    def _g1_create(self):
        length = max(10, int(self.g1_len.get()))
        rule = max(0, min(255, int(self.g1_rule.get())))
        self.g1 = GameOfLife1D(length, rule)
        self.g1.reset()
        self.g1_hist = [self.g1.state.copy()]
        self._g1_draw()

    def _g1_step(self):
        if self.g1 is None:
            self._g1_create()
        self.g1.step()
        self.g1_hist.append(self.g1.state.copy())
        if len(self.g1_hist) > 200:
            self.g1_hist.pop(0)
        self._g1_draw()

    def _g1_draw(self):
        self.g1_ax.clear()
        if self.g1_hist:
            img = np.array(self.g1_hist)
            self.g1_ax.imshow(img, aspect='auto', interpolation='nearest', cmap='gray_r')
        self.g1_ax.set_title(f'Autómata 1D - Regla {self.g1.rule}', fontsize=12)
        self.g1_ax.axis('off')
        self.g1_canvas.draw()

    def _g1_run(self):
        def run():
            for _ in range(200):
                time.sleep(0.03)
                self._g1_step()
        threading.Thread(target=run, daemon=True).start()


def main():
    root = tk.Tk()
    app = GameOfLifeApp(root)
    root.mainloop()