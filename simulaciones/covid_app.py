# covid_app.py
import tkinter as tk
from tkinter import font, messagebox
import threading
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from covid_simulation import CovidSimulation


BG_COLOR = "#f0f5ff"
PLOT_BG = "#e6eeff"


class CovidApp:
    def __init__(self, root):
        self.root = root
        root.title("🦠 Simulación de Propagación de Enfermedades")
        root.geometry("950x720")
        root.configure(bg=BG_COLOR)

        self.base_font = font.Font(family="Segoe UI", size=10)
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")

        control_frame = tk.Frame(root, bg="white", width=280)
        control_frame.pack(side='left', fill='y', padx=15, pady=15)
        control_frame.pack_propagate(False)

        title = tk.Label(control_frame, text="Parámetros de Simulación",
                         bg="white", fg="#212529", font=("Segoe UI", 13, "bold"))
        title.pack(pady=(20, 25))

        self.rows = tk.IntVar(value=60)
        self.cols = tk.IntVar(value=60)
        self.init_inf = tk.IntVar(value=5)
        self.p_infect = tk.DoubleVar(value=0.25)
        self.p_recover = tk.DoubleVar(value=0.02)
        self.p_die = tk.DoubleVar(value=0.005)

        self._add_param(control_frame, "Filas:", self.rows)
        self._add_param(control_frame, "Columnas:", self.cols)
        self._add_param(control_frame, "Infectados iniciales:", self.init_inf)
        self._add_param(control_frame, "P(infectar por vecino):", self.p_infect)
        self._add_param(control_frame, "P(recuperar por paso):", self.p_recover)
        self._add_param(control_frame, "P(morir por paso):", self.p_die)

        self._add_button(control_frame, "Crear simulación", self.create_sim, "#4361ee")
        self._add_button(control_frame, "Paso", self.step, "#6c757d")
        self._add_button(control_frame, "Ejecutar / Parar", self.toggle_run, "#2ecc71")
        self._add_button(control_frame, "Cerrar ventana", root.destroy, "#e63946")

        plot_frame = tk.Frame(root, bg=BG_COLOR)
        plot_frame.pack(side='right', fill='both', expand=True, padx=(0,15), pady=15)

        fig = Figure(figsize=(7, 6), facecolor=BG_COLOR)
        self.ax_grid = fig.add_subplot(211)
        self.ax_grid.set_facecolor(PLOT_BG)
        self.ax_chart = fig.add_subplot(212)
        self.ax_chart.set_facecolor(PLOT_BG)
        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.sim = None
        self.history = []
        self.running = False

    def _add_param(self, parent, label_text, var):
        lbl = tk.Label(parent, text=label_text, bg="white", fg="#495057",
                       font=self.base_font, anchor="w")
        lbl.pack(fill='x', padx=20, pady=(10, 2))
        entry = tk.Entry(parent, textvariable=var, font=self.base_font,
                         relief="solid", bd=1)
        entry.pack(fill='x', padx=20, pady=(0, 12))

    def _add_button(self, parent, text, cmd, bg):
        btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg="white",
                        font=self.base_font, relief="flat", cursor="hand2",
                        height=2)
        btn.pack(fill='x', padx=20, pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._darken(bg)))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _darken(self, hex_color, factor=0.85):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_sim(self):
        try:
            rows = max(5, int(self.rows.get()))
            cols = max(5, int(self.cols.get()))
            init = max(1, int(self.init_inf.get()))
            pinf = float(self.p_infect.get())
            prec = float(self.p_recover.get())
            pdie = float(self.p_die.get())
            self.sim = CovidSimulation(rows, cols, init, pinf, prec, pdie)
            self.history = [self.sim.counts()]
            self.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Parámetros inválidos:\n{e}")

    def draw(self):
        if self.sim is None:
            return
        self.ax_grid.clear()
        cmap = ListedColormap(['white', 'lightgreen', 'red', 'lightblue', 'black'])
        self.ax_grid.imshow(self.sim.grid, cmap=cmap, vmin=0, vmax=4, interpolation='nearest')
        self.ax_grid.set_title(f'Simulación COVID-19 — Paso {self.sim.t}', fontsize=11)
        self.ax_grid.axis('off')

        self.ax_chart.clear()
        t = list(range(len(self.history)))
        s = [h[1] for h in self.history]
        i = [h[2] for h in self.history]
        r = [h[3] for h in self.history]
        d = [h[4] for h in self.history]
        self.ax_chart.plot(t, s, label='Susceptibles', color='#4CAF50')
        self.ax_chart.plot(t, i, label='Infectados', color='#F44336')
        self.ax_chart.plot(t, r, label='Recuperados', color='#2196F3')
        self.ax_chart.plot(t, d, label='Muertos', color='#000000')
        self.ax_chart.legend(loc='upper right', fontsize=9)
        self.ax_chart.set_xlabel('Tiempo (pasos)')
        self.ax_chart.set_ylabel('Población')
        self.ax_chart.grid(True, linestyle='--', alpha=0.5)

        self.canvas.draw()

    def step(self):
        if self.sim is None:
            self.create_sim()
        self.sim.step()
        self.history.append(self.sim.counts())
        self.draw()

    def toggle_run(self):
        self.running = not self.running
        if self.running:
            self.run_loop()

    def run_loop(self):
        def loop():
            while self.running:
                time.sleep(0.15)
                try:
                    self.step()
                except Exception as e:
                    print("Error en simulación COVID:", e)
                    self.running = False
        threading.Thread(target=loop, daemon=True).start()


def main():
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()