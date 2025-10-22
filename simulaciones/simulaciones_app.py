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

from game_of_life_2d import GameOfLife2D
from game_of_life_1d import GameOfLife1D
from covid_simulation import CovidSimulation

class SimulacionesApp:
    def __init__(self, root):
        self.root = root
        root.title('Simulaciones: Juego de la Vida + COVID')
        root.geometry('1100x700')

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill='both', expand=True)

        self._build_gameoflife_tab()
        self._build_gameoflife1d_tab()
        self._build_covid_tab()

    # ---------------- Game of Life 2D ----------------
    def _build_gameoflife_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='Juego de la Vida 2D')

        left = ttk.Frame(tab)
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(tab)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left, text='Filas:').pack(anchor='w')
        self.g2_rows = tk.IntVar(value=50)
        ttk.Entry(left, textvariable=self.g2_rows).pack(fill='x')
        ttk.Label(left, text='Columnas:').pack(anchor='w')
        self.g2_cols = tk.IntVar(value=50)
        ttk.Entry(left, textvariable=self.g2_cols).pack(fill='x')
        ttk.Label(left, text='Prob. vivo inicial:').pack(anchor='w')
        self.g2_p = tk.DoubleVar(value=0.2)
        ttk.Entry(left, textvariable=self.g2_p).pack(fill='x')

        ttk.Button(left, text='Crear aleatorio', command=self._g2_create_random).pack(fill='x', pady=5)
        ttk.Button(left, text='Paso', command=self._g2_step).pack(fill='x')
        ttk.Button(left, text='Ejecutar/Parar', command=self._g2_toggle_run).pack(fill='x', pady=5)
        ttk.Button(left, text='Limpiar', command=self._g2_clear).pack(fill='x')

        fig = Figure(figsize=(6,6))
        self.g2_ax = fig.add_subplot(111)
        self.g2_canvas = FigureCanvasTkAgg(fig, master=right)
        self.g2_canvas.get_tk_widget().pack(fill='both', expand=True)

        self.g2 = None
        self.g2_running = False

    def _g2_create_random(self):
        rows = max(5, int(self.g2_rows.get()))
        cols = max(5, int(self.g2_cols.get()))
        p = float(self.g2_p.get())
        self.g2 = GameOfLife2D(rows=rows, cols=cols)
        self.g2.randomize(p=p)
        self._g2_draw()

    def _g2_draw(self):
        self.g2_ax.clear()
        self.g2_ax.imshow(self.g2.grid, interpolation='nearest')
        self.g2_ax.set_title('Juego de la Vida 2D')
        self.g2_canvas.draw()

    def _g2_step(self):
        if self.g2 is None:
            self._g2_create_random()
        self.g2.step()
        self._g2_draw()

    def _g2_toggle_run(self):
        self.g2_running = not self.g2_running
        if self.g2_running:
            self._g2_run_loop()

    def _g2_run_loop(self):
        def loop():
            while self.g2_running:
                time.sleep(0.1)
                try:
                    self._g2_step()
                except Exception as e:
                    print('Error en loop GOL2D:', e)
                    self.g2_running = False
        threading.Thread(target=loop, daemon=True).start()

    def _g2_clear(self):
        if self.g2 is None:
            self._g2_create_random()
        self.g2.grid = np.zeros_like(self.g2.grid)
        self._g2_draw()

    # ---------------- Game of Life 1D ----------------
    # ---------------- Game of Life 1D ----------------
def _build_gameoflife1d_tab(self):
    tab = ttk.Frame(self.nb)
    self.nb.add(tab, text='Juego de la Vida 1D')

    left = ttk.Frame(tab)
    left.pack(side='left', fill='y', padx=10, pady=10)
    right = ttk.Frame(tab)
    right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

    ttk.Label(left, text='Longitud:').pack(anchor='w')
    self.g1_length = tk.IntVar(value=300)
    ttk.Entry(left, textvariable=self.g1_length).pack(fill='x')

    # Menú desplegable para reglas
    ttk.Label(left, text='Regla:').pack(anchor='w')
    self.g1_rule_var = tk.StringVar(value='30')  # Valor por defecto
    rules = ['30', '110', '90', '50', 'Regla personalizada']
    self.g1_rule_combo = ttk.Combobox(left, values=rules, textvariable=self.g1_rule_var, state='readonly')
    self.g1_rule_combo.pack(fill='x')
    self.g1_rule_combo.bind('<<ComboboxSelected>>', self._update_rule_field)

    # Campo para regla personalizada (oculto inicialmente)
    self.custom_rule_frame = ttk.Frame(left)
    self.custom_rule_frame.pack(fill='x', pady=5)
    ttk.Label(self.custom_rule_frame, text='Regla personalizada (0-255):').pack(anchor='w')
    self.custom_rule_var = tk.IntVar(value=30)
    self.custom_rule_entry = ttk.Entry(self.custom_rule_frame, textvariable=self.custom_rule_var, state='disabled')
    self.custom_rule_entry.pack(fill='x')
    self.custom_rule_var.trace('w', lambda *args: self._validate_custom_rule())

    ttk.Button(left, text='Crear', command=self._g1_create).pack(fill='x', pady=5)
    ttk.Button(left, text='Siguiente', command=self._g1_step).pack(fill='x')
    ttk.Button(left, text='Ejecutar', command=self._g1_run).pack(fill='x', pady=5)

    fig = Figure(figsize=(7,6))
    self.g1_ax = fig.add_subplot(111)
    self.g1_canvas = FigureCanvasTkAgg(fig, master=right)
    self.g1_canvas.get_tk_widget().pack(fill='both', expand=True)

    self.g1 = None
    self.g1_history = []

def _update_rule_field(self, event):
    if self.g1_rule_var.get() == 'Regla personalizada':
        self.custom_rule_entry.configure(state='normal')
    else:
        self.custom_rule_entry.configure(state='disabled')
        self.custom_rule_var.set(int(self.g1_rule_var.get()))  # Usa la regla seleccionada

def _validate_custom_rule(self):
    value = self.custom_rule_var.get()
    if not (0 <= value <= 255):
        self.custom_rule_var.set(max(0, min(255, value)))  # Limita entre 0 y 255

def _g1_create(self):
    length = max(10, int(self.g1_length.get()))
    rule = int(self.g1_rule_var.get()) if self.g1_rule_var.get() != 'Regla personalizada' else self.custom_rule_var.get()
    self.g1 = GameOfLife1D(length, rule)
    self.g1_history = [self.g1.state.copy()]
    self._g1_draw()

def _g1_draw(self):
    self.g1_ax.clear()
    img = np.array(self.g1_history)
    self.g1_ax.imshow(img, aspect='auto', interpolation='nearest')
    self.g1_ax.set_title(f'Autómata 1D (Regla {self.g1.rule})')
    self.g1_canvas.draw()

def _g1_step(self):
    if self.g1 is None:
        self._g1_create()
    self.g1.step()
    self.g1_history.append(self.g1.state.copy())
    if len(self.g1_history) > 200:
        self.g1_history.pop(0)
    self._g1_draw()

def _g1_run(self):
    def run_loop():
        for _ in range(200):
            time.sleep(0.05)
            self._g1_step()
    threading.Thread(target=run_loop, daemon=True).start()

    # ---------------- COVID Tab ----------------
    def _build_covid_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text='Simulación COVID (grid)')

        left = ttk.Frame(tab)
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(tab)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left, text='Filas:').pack(anchor='w')
        self.cv_rows = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.cv_rows).pack(fill='x')
        ttk.Label(left, text='Columnas:').pack(anchor='w')
        self.cv_cols = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.cv_cols).pack(fill='x')
        ttk.Label(left, text='Inicial infectados:').pack(anchor='w')
        self.cv_init = tk.IntVar(value=5)
        ttk.Entry(left, textvariable=self.cv_init).pack(fill='x')

        ttk.Label(left, text='P(infect) por vecino:').pack(anchor='w')
        self.cv_pinf = tk.DoubleVar(value=0.25)
        ttk.Entry(left, textvariable=self.cv_pinf).pack(fill='x')
        ttk.Label(left, text='P(recover) por paso:').pack(anchor='w')
        self.cv_prec = tk.DoubleVar(value=0.02)
        ttk.Entry(left, textvariable=self.cv_prec).pack(fill='x')
        ttk.Label(left, text='P(die) por paso:').pack(anchor='w')
        self.cv_pdie = tk.DoubleVar(value=0.005)
        ttk.Entry(left, textvariable=self.cv_pdie).pack(fill='x')

        ttk.Button(left, text='Crear simulación', command=self._cv_create).pack(fill='x', pady=5)
        ttk.Button(left, text='Paso', command=self._cv_step).pack(fill='x')
        ttk.Button(left, text='Ejecutar/Parar', command=self._cv_toggle_run).pack(fill='x', pady=5)

        fig = Figure(figsize=(7,6))
        self.cv_ax_grid = fig.add_subplot(211)
        self.cv_ax_chart = fig.add_subplot(212)
        self.cv_canvas = FigureCanvasTkAgg(fig, master=right)
        self.cv_canvas.get_tk_widget().pack(fill='both', expand=True)

        self.cv = None
        self.cv_running = False
        self.cv_history = []

    def _cv_create(self):
        rows = max(5, int(self.cv_rows.get()))
        cols = max(5, int(self.cv_cols.get()))
        init = max(1, int(self.cv_init.get()))
        pinf = float(self.cv_pinf.get())
        prec = float(self.cv_prec.get())
        pdie = float(self.cv_pdie.get())
        self.cv = CovidSimulation(rows=rows, cols=cols, init_infected=init, p_infect=pinf, p_recover=prec, p_die=pdie)
        self.cv_history = [self.cv.counts()]
        self._cv_draw()

    def _cv_draw(self):
        self.cv_ax_grid.clear()
        cmap = ListedColormap(['white','lightgreen','red','lightblue','black'])
        self.cv_ax_grid.imshow(self.cv.grid, interpolation='nearest', cmap=cmap, vmin=0, vmax=4)
        self.cv_ax_grid.set_title(f'COVID Sim t={self.cv.t}')

        self.cv_ax_chart.clear()
        times = list(range(len(self.cv_history)))
        s = [h[1] for h in self.cv_history]
        i = [h[2] for h in self.cv_history]
        r = [h[3] for h in self.cv_history]
        d = [h[4] for h in self.cv_history]
        self.cv_ax_chart.plot(times, s, label='Susceptibles')
        self.cv_ax_chart.plot(times, i, label='Infectados')
        self.cv_ax_chart.plot(times, r, label='Recuperados')
        self.cv_ax_chart.plot(times, d, label='Muertos')
        self.cv_ax_chart.legend()

        self.cv_canvas.draw()

    def _cv_step(self):
        if self.cv is None:
            self._cv_create()
        self.cv.step()
        self.cv_history.append(self.cv.counts())
        self._cv_draw()

    def _cv_toggle_run(self):
        self.cv_running = not self.cv_running
        if self.cv_running:
            self._cv_run_loop()

    def _cv_run_loop(self):
        def loop():
            while self.cv_running:
                time.sleep(0.1)
                try:
                    self._cv_step()
                except Exception as e:
                    print('Error en loop COVID:', e)
                    self.cv_running = False
        threading.Thread(target=loop, daemon=True).start()

def main():
    root = tk.Tk()
    app = SimulacionesApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()