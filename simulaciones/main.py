# main.py
import tkinter as tk
from tkinter import font
import threading

# Importar las apps
from game_of_life_app import main as gol_main
from covid_app import main as covid_main
from distribuciones_app import main as dist_main


def launch_app(target_func):
    """Ejecuta una aplicación en un hilo separado."""
    threading.Thread(target=target_func, daemon=True).start()


def create_modern_menu():
    root = tk.Tk()
    root.title("Simulaciones Científicas")
    root.geometry("720x500")
    root.resizable(False, False)
    root.configure(bg="#f5f7fa")

    # Centrar ventana
    root.eval('tk::PlaceWindow . center')

    # Fuente personalizada
    title_font = font.Font(family="Segoe UI", size=20, weight="bold")
    subtitle_font = font.Font(family="Segoe UI", size=11, slant="italic")
    button_font = font.Font(family="Segoe UI", size=12)

    # Encabezado
    header_frame = tk.Frame(root, bg="#f5f7fa")
    header_frame.pack(pady=(30, 10))

    title_label = tk.Label(
        header_frame,
        text="🔬 Simulaciones Científicas",
        font=title_font,
        bg="#f5f7fa",
        fg="#2c3e50"
    )
    title_label.pack()

    subtitle_label = tk.Label(
        header_frame,
        text="Selecciona una herramienta para explorar modelos computacionales",
        font=subtitle_font,
        bg="#f5f7fa",
        fg="#7f8c8d"
    )
    subtitle_label.pack()

    # Marco de botones
    button_frame = tk.Frame(root, bg="#f5f7fa")
    button_frame.pack(pady=20)

    # Estilo común para botones
    button_config = {
        "font": button_font,
        "width": 42,
        "height": 2,
        "bd": 0,
        "relief": "flat",
        "cursor": "hand2"
    }

    # Botón 1: Juego de la Vida
    btn_gol = tk.Button(
        button_frame,
        text="🧫 Juego de la Vida (1D y 2D)",
        bg="#e3f2fd",
        fg="#1976d2",
        activebackground="#bbdefb",
        activeforeground="#0d47a1",
        **button_config
    )
    btn_gol.config(command=lambda: launch_app(gol_main))
    btn_gol.pack(pady=8)

    # Botón 2: Simulación COVID
    btn_covid = tk.Button(
        button_frame,
        text="🦠 Simulación de Propagación de Enfermedades",
        bg="#f3e5f5",
        fg="#7b1fa2",
        activebackground="#e1bee7",
        activeforeground="#4a148c",
        **button_config
    )
    btn_covid.config(command=lambda: launch_app(covid_main))
    btn_covid.pack(pady=8)

    # Botón 3: Distribuciones
    btn_dist = tk.Button(
        button_frame,
        text="📊 Generador de Distribuciones Aleatorias",
        bg="#e8f5e9",
        fg="#388e3c",
        activebackground="#c8e6c9",
        activeforeground="#1b5e20",
        **button_config
    )
    btn_dist.config(command=lambda: launch_app(dist_main))
    btn_dist.pack(pady=8)

    # Botón de salida
    exit_button = tk.Button(
        root,
        text="Salir",
        command=root.destroy,
        font=("Segoe UI", 10),
        bg="#ffcdd2",
        fg="#c62828",
        activebackground="#ef9a9a",
        activeforeground="#b71c1c",
        width=15,
        height=1,
        bd=0,
        relief="flat",
        cursor="hand2"
    )
    exit_button.pack(pady=(10, 20))

    # Efecto hover (opcional, básico)
    def on_enter(event, color):
        event.widget.config(bg=color)

    def on_leave(event, color):
        event.widget.config(bg=color)

    # Hover para botones (simulado con colores cercanos)
    btn_gol.bind("<Enter>", lambda e: on_enter(e, "#d0eaff"))
    btn_gol.bind("<Leave>", lambda e: on_leave(e, "#e3f2fd"))

    btn_covid.bind("<Enter>", lambda e: on_enter(e, "#e9d7f2"))
    btn_covid.bind("<Leave>", lambda e: on_leave(e, "#f3e5f5"))

    btn_dist.bind("<Enter>", lambda e: on_enter(e, "#d9f0dc"))
    btn_dist.bind("<Leave>", lambda e: on_leave(e, "#e8f5e9"))

    exit_button.bind("<Enter>", lambda e: on_enter(e, "#ff9ea3"))
    exit_button.bind("<Leave>", lambda e: on_leave(e, "#ffcdd2"))

    return root


if __name__ == "__main__":
    app = create_modern_menu()
    app.mainloop()