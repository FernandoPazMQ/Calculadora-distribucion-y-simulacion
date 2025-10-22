# distribuciones_app.py
import tkinter as tk
from tkinter import font, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from random_generators import RandomGenerators


BG_COLOR = "#f0f5ff"
PLOT_BG = "#e6eeff"


def plot_histogram(data, ax, bins=50, title='', xlabel='Valor'):
    ax.clear()
    ax.hist(data, bins=bins, density=True, alpha=0.75, color="#4361ee")
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Densidad')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_facecolor(PLOT_BG)


class DistribucionesApp:
    def __init__(self, root):
        self.root = root
        root.title("📊 Generador de Distribuciones Aleatorias")
        root.geometry("1000x620")
        root.configure(bg=BG_COLOR)

        self.base_font = font.Font(family="Segoe UI", size=10)

        left = tk.Frame(root, bg="white", width=300)
        left.pack(side='left', fill='y', padx=15, pady=15)
        left.pack_propagate(False)

        title = tk.Label(left, text="Configuración", bg="white",
                         font=("Segoe UI", 13, "bold"), fg="#212529")
        title.pack(pady=(20, 25))

        tk.Label(left, text="Distribución:", bg="white", fg="#495057",
                 font=self.base_font, anchor="w").pack(fill='x', padx=20, pady=(10, 2))
        self.dist_var = tk.StringVar(value='normal')
        dists = ['uniform','exponential','erlang','gamma','normal','weibull','bernoulli','binomial','poisson']
        self.dist_combo = tk.OptionMenu(left, self.dist_var, *dists)
        self.dist_combo.config(font=self.base_font, bg="white", width=18, anchor="w")
        self.dist_combo.pack(fill='x', padx=20, pady=(0, 15))

        tk.Label(left, text="Tamaño de la muestra (n):", bg="white", fg="#495057",
                 font=self.base_font, anchor="w").pack(fill='x', padx=20, pady=(10, 2))
        self.dist_size = tk.IntVar(value=1000)
        tk.Entry(left, textvariable=self.dist_size, font=self.base_font,
                 relief="solid", bd=1).pack(fill='x', padx=20, pady=(0, 15))

        tk.Label(left, text="Parámetros (ej: mu=0,sigma=1):", bg="white", fg="#495057",
                 font=self.base_font, anchor="w").pack(fill='x', padx=20, pady=(10, 2))
        self.params_entry = tk.Entry(left, font=self.base_font, relief="solid", bd=1)
        self.params_entry.insert(0, 'mu=0,sigma=1')
        self.params_entry.pack(fill='x', padx=20, pady=(0, 20))

        self.btn = tk.Button(left, text="Generar y graficar", command=self._generate_and_plot,
                             bg="#4361ee", fg="white", font=self.base_font,
                             relief="flat", cursor="hand2", height=2)
        self.btn.pack(fill='x', padx=20, pady=10)
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg="#3a56e4"))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg="#4361ee"))

        right = tk.Frame(root, bg=BG_COLOR)
        right.pack(side='right', fill='both', expand=True, padx=(0,15), pady=15)

        fig = Figure(figsize=(7,5), facecolor=BG_COLOR)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(PLOT_BG)
        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def _parse_params(self, text):
        d = {}
        if not text.strip():
            return d
        parts = [p.strip() for p in text.split(',') if p.strip()]
        for p in parts:
            if '=' in p:
                k, v = p.split('=', 1)
                try:
                    d[k.strip()] = float(v)
                except:
                    try:
                        d[k.strip()] = int(v)
                    except:
                        d[k.strip()] = v
        return d

    def _generate_and_plot(self):
        dist = self.dist_var.get()
        n = max(1, int(self.dist_size.get()))
        params = self._parse_params(self.params_entry.get())
        try:
            if dist == 'uniform':
                a = params.get('a', 0.0)
                b = params.get('b', 1.0)
                data = RandomGenerators.uniform(a=a, b=b, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Uniforme U({a}, {b})')
            elif dist == 'exponential':
                lam = params.get('lam', params.get('lambda', 1.0))
                data = RandomGenerators.exponential(lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Exponencial (λ = {lam})')
            elif dist == 'erlang':
                k = int(params.get('k', 2))
                lam = params.get('lam', 1.0)
                data = RandomGenerators.erlang(k=k, lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Erlang (k = {k}, λ = {lam})')
            elif dist == 'gamma':
                shape = params.get('shape', 2.0)
                scale = params.get('scale', 1.0)
                data = RandomGenerators.gamma(shape=shape, scale=scale, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Gamma (shape = {shape}, scale = {scale})')
            elif dist == 'normal':
                mu = params.get('mu', 0.0)
                sigma = params.get('sigma', 1.0)
                data = RandomGenerators.normal(mu=mu, sigma=sigma, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Normal N({mu}, {sigma**2})')
            elif dist == 'weibull':
                k = params.get('k', 1.5)
                lam = params.get('lam', 1.0)
                data = RandomGenerators.weibull(k=k, lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Weibull (k = {k}, λ = {lam})')
            elif dist == 'bernoulli':
                p = params.get('p', 0.5)
                data = RandomGenerators.bernoulli(p=p, size=n)
                plot_histogram(data, self.ax, bins=2, title=f'Bernoulli (p = {p})')
            elif dist == 'binomial':
                nn = int(params.get('n', 10))
                p = params.get('p', 0.5)
                data = RandomGenerators.binomial(n=nn, p=p, size=n)
                plot_histogram(data, self.ax, bins=range(0, nn+2), title=f'Binomial (n = {nn}, p = {p})')
            elif dist == 'poisson':
                lam = params.get('lam', 1.0)
                data = RandomGenerators.poisson(lam=lam, size=n)
                bins = range(0, int(max(data)) + 2) if len(data) > 0 else 2
                plot_histogram(data, self.ax, bins=bins, title=f'Poisson (λ = {lam})')
            else:
                raise ValueError('Distribución no soportada')

            self.canvas.draw()
        except Exception as e:
            messagebox.showerror('Error', f'Error generando la distribución:\n{e}')


def main():
    root = tk.Tk()
    app = DistribucionesApp(root)
    root.mainloop()