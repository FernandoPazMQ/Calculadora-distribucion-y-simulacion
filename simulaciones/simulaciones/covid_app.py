# covid_app.py
import tkinter as tk
from tkinter import font, messagebox
import threading
import time
import numpy as np
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import matplotlib
matplotlib.use('TkAgg')


class CovidSimulation:
    """
    Simulación de propagación de enfermedades
    Estados: 0=vacío, 1=susceptible, 2=infectado, 3=recuperado, 4=muerto
    """
    def __init__(self, rows=60, cols=60, init_infected=5, p_infect=0.3, p_recover=0.02, p_die=0.005):
        self.rows = rows
        self.cols = cols
        self.grid = np.ones((rows, cols), dtype=int)  # Todos susceptibles
        self.t = 0
        self.p_infect = p_infect
        self.p_recover = p_recover
        self.p_die = p_die

        # Infectados iniciales
        for _ in range(init_infected):
            r = random.randrange(rows)
            c = random.randrange(cols)
            self.grid[r, c] = 2

    def step(self):
        new_grid = self.grid.copy()
        for r in range(self.rows):
            for c in range(self.cols):
                state = self.grid[r, c]
                if state == 1:  # Susceptible
                    neighbors = self.grid[max(0, r-1):r+2, max(0, c-1):c+2]
                    infected_neighbors = np.sum(neighbors == 2)
                    if infected_neighbors > 0:
                        p = 1 - ((1 - self.p_infect) ** infected_neighbors)
                        if random.random() < p:
                            new_grid[r, c] = 2
                elif state == 2:  # Infectado
                    if random.random() < self.p_die:
                        new_grid[r, c] = 4
                    elif random.random() < self.p_recover:
                        new_grid[r, c] = 3
        self.grid = new_grid
        self.t += 1

    def counts(self):
        """
        Retorna un diccionario con el conteo de cada estado
        """
        unique, counts = np.unique(self.grid, return_counts=True)
        d = {k: 0 for k in range(5)}
        for u, c in zip(unique, counts):
            d[int(u)] = int(c)
        return d


class CovidApp:
    """
    Aplicación de simulación de propagación de COVID-19 con interfaz Tkinter y matplotlib
    """
    BG_COLOR = "#6890DF"
    PLOT_BG = "#e6eeff"

    def __init__(self, root):
        self.root = root
        root.title("🦠 Simulación de Propagación de Enfermedades")
        root.geometry("1000x700")
        root.configure(bg=self.BG_COLOR)

        self.base_font = font.Font(family="Segoe UI", size=10)
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")

        self.sim = None
        self.history = []
        self.running = False

        self._setup_controls()
        self._setup_plots()

    # ------------------- Controles -------------------
    def _setup_controls(self):
        frame = tk.Frame(self.root, bg="white", width=280)
        frame.pack(side='left', fill='y', padx=15, pady=15)
        frame.pack_propagate(False)

        tk.Label(frame, text="Parámetros de Simulación", bg="white", fg="#212529",
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 25))

        # Variables de simulación
        self.rows = tk.IntVar(value=60)
        self.cols = tk.IntVar(value=60)
        self.init_inf = tk.IntVar(value=5)
        self.p_infect = tk.DoubleVar(value=0.25)
        self.p_recover = tk.DoubleVar(value=0.02)
        self.p_die = tk.DoubleVar(value=0.005)

        self._add_param(frame, "Filas:", self.rows)
        self._add_param(frame, "Columnas:", self.cols)
        self._add_param(frame, "Infectados iniciales:", self.init_inf)
        self._add_param(frame, "P(infectar por vecino):", self.p_infect)
        self._add_param(frame, "P(recuperar por paso):", self.p_recover)
        self._add_param(frame, "P(morir por paso):", self.p_die)

        self._add_button(frame, "Crear simulación", self.create_sim, "#4361ee")
        self._add_button(frame, "Paso", self.step, "#6c757d")
        self._add_button(frame, "Ejecutar / Parar", self.toggle_run, "#84efb1")
        self._add_button(frame, "Cerrar ventana", self.root.destroy, "#e63946")

    def _add_param(self, parent, label_text, var):
        tk.Label(parent, text=label_text, bg="white", fg="#495057",
                 font=self.base_font, anchor="w").pack(fill='x', padx=20, pady=(10, 2))
        tk.Entry(parent, textvariable=var, font=self.base_font, relief="solid", bd=1).pack(fill='x', padx=20, pady=(0, 12))

    def _add_button(self, parent, text, cmd, bg):
        btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg="white",
                        font=self.base_font, relief="flat", cursor="hand2", height=2)
        btn.pack(fill='x', padx=20, pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._darken(bg)))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _darken(self, hex_color, factor=0.85):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, min(255, int(r * factor))), max(0, min(255, int(g * factor))), max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ------------------- Plots -------------------
    def _setup_plots(self):
        frame = tk.Frame(self.root, bg=self.BG_COLOR)
        frame.pack(side='right', fill='both', expand=True, padx=(0, 15), pady=15)

        fig = Figure(figsize=(12, 6), facecolor=self.BG_COLOR)
        self.ax_grid = fig.add_subplot(121)
        self.ax_chart = fig.add_subplot(122)
        self.ax_grid.set_facecolor(self.PLOT_BG)
        self.ax_chart.set_facecolor(self.PLOT_BG)

        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # ------------------- Simulación -------------------
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
        if not self.sim:
            return

        self.ax_grid.clear()
        self.ax_chart.clear()

        # --- Cuadrícula ---
        cmap = ListedColormap(['white', 'green', 'red', 'blue', 'black'])
        self.ax_grid.imshow(self.sim.grid, cmap=cmap, vmin=0, vmax=4, interpolation='nearest')
        self.ax_grid.set_title(f'Simulación COVID-19 — Paso {self.sim.t}', fontsize=11)
        self.ax_grid.axis('off')

        # --- Gráfica de barras apiladas ---
        t = list(range(len(self.history)))
        s = [h[1] for h in self.history]  # Susceptibles
        i = [h[2] for h in self.history]  # Infectados
        r = [h[3] for h in self.history]  # Recuperados
        d = [h[4] for h in self.history]  # Muertos

        self.ax_chart.bar(t, s, color='green', label='Susceptibles')
        self.ax_chart.bar(t, i, bottom=s, color='red', label='Infectados')
        self.ax_chart.bar(t, r, bottom=np.array(s)+np.array(i), color='blue', label='Recuperados')
        self.ax_chart.bar(t, d, bottom=np.array(s)+np.array(i)+np.array(r), color='black', label='Muertos')

        self.ax_chart.set_xlabel('Tiempo (pasos)')
        self.ax_chart.set_ylabel('Población')
        self.ax_chart.set_title('Evolución de la población')
        self.ax_chart.grid(True, linestyle='--', alpha=0.3)
        self.ax_chart.legend(loc='upper right', fontsize=9)

        self.canvas.draw()

    def step(self):
        if not self.sim:
            self.create_sim()
        self.sim.step()
        self.history.append(self.sim.counts())
        self.draw()

    def toggle_run(self):
        if not self.sim:
            self.create_sim()
        self.running = not self.running
        if self.running:
            threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        while self.running:
            time.sleep(0.15)
            try:
                self.step()
            except Exception as e:
                print("Error en simulación COVID:", e)
                self.running = False


# ------------------- Main -------------------
def main():
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
