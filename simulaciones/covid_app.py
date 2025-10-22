# covid_app.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from covid_simulation import CovidSimulation


class CovidApp:
    def __init__(self, root):
        self.root = root
        root.title('Simulación COVID-19')
        root.geometry('900x700')

        left = ttk.Frame(root)
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(root)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Parámetros
        ttk.Label(left, text='Filas:').pack(anchor='w')
        self.rows = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.rows).pack(fill='x')

        ttk.Label(left, text='Columnas:').pack(anchor='w')
        self.cols = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.cols).pack(fill='x')

        ttk.Label(left, text='Infectados iniciales:').pack(anchor='w')
        self.init_inf = tk.IntVar(value=5)
        ttk.Entry(left, textvariable=self.init_inf).pack(fill='x')

        ttk.Label(left, text='P(infectar por vecino):').pack(anchor='w')
        self.p_infect = tk.DoubleVar(value=0.25)
        ttk.Entry(left, textvariable=self.p_infect).pack(fill='x')

        ttk.Label(left, text='P(recuperar por paso):').pack(anchor='w')
        self.p_recover = tk.DoubleVar(value=0.02)
        ttk.Entry(left, textvariable=self.p_recover).pack(fill='x')

        ttk.Label(left, text='P(morir por paso):').pack(anchor='w')
        self.p_die = tk.DoubleVar(value=0.005)
        ttk.Entry(left, textvariable=self.p_die).pack(fill='x')

        ttk.Button(left, text='Crear simulación', command=self.create_sim).pack(fill='x', pady=(10, 5))
        ttk.Button(left, text='Paso', command=self.step).pack(fill='x')
        ttk.Button(left, text='Ejecutar/Parar', command=self.toggle_run).pack(fill='x', pady=5)
        ttk.Button(left, text='Cerrar', command=root.destroy).pack(fill='x', pady=(20, 0))

        # Gráficos
        fig = Figure(figsize=(7, 6))
        self.ax_grid = fig.add_subplot(211)
        self.ax_chart = fig.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.sim = None
        self.history = []
        self.running = False

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
        self.ax_grid.set_title(f'COVID Simulación - Paso {self.sim.t}')

        self.ax_chart.clear()
        t = list(range(len(self.history)))
        s = [h[1] for h in self.history]
        i = [h[2] for h in self.history]
        r = [h[3] for h in self.history]
        d = [h[4] for h in self.history]
        self.ax_chart.plot(t, s, label='Susceptibles')
        self.ax_chart.plot(t, i, label='Infectados')
        self.ax_chart.plot(t, r, label='Recuperados')
        self.ax_chart.plot(t, d, label='Muertos')
        self.ax_chart.legend()
        self.ax_chart.set_xlabel('Tiempo (pasos)')
        self.ax_chart.set_ylabel('Población')

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