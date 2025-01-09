import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Funkcja symulacji
def run_simulation():
    # Placeholder dla symulacji - należy dodać logikę symulacji
    print(f"Symulacja uruchomiona z {num_clients.get()} klientami i {arrival_rate.get()} tempem przybycia.")
    print("Parametry PS_PROCESSING_TIME:", ps_processing_time)
    print("Parametry FIFO_PROCESSING_TIME:", fifo_processing_time)
    print("Parametry LIFOPR_PROCESSING_TIME:", lifopr_processing_time)
    print("Consultanci: PS =", ps_consultants.get(), "FIFO =", fifo_consultants.get(), "LIFO =", lifopr_consultants.get())

    # Generowanie przykładowego wykresu (można zastąpić wynikami symulacji)
    ax.clear()
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.set_title("Wyniki symulacji")
    canvas.draw()

# Główne okno aplikacji
root = tk.Tk()
root.title("Symulacja Sieci Kolejkowej BCMP")

# Panel parametrów
params_frame = tk.Frame(root)
params_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

# Liczba klientów
tk.Label(params_frame, text="Liczba klientów:").pack(anchor=tk.W)
num_clients = tk.IntVar(value=20)
tk.Entry(params_frame, textvariable=num_clients).pack(fill=tk.X)

# Tempo przybycia klientów
tk.Label(params_frame, text="Tempo przybycia klientów (ARRIVAL_RATE):").pack(anchor=tk.W)
arrival_rate = tk.DoubleVar(value=2.0)
tk.Entry(params_frame, textvariable=arrival_rate).pack(fill=tk.X)

# Parametry PS_PROCESSING_TIME
tk.Label(params_frame, text="PS_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
ps_processing_time = {
    "normal": tk.StringVar(value="4.0, 2.0"),
    "medium": tk.StringVar(value="3.0, 1.5, 1.0"),
    "complicated": tk.StringVar(value="2.5, 1.2, 0.8, 0.5")
}
for key, var in ps_processing_time.items():
    tk.Label(params_frame, text=f"{key}:").pack(anchor=tk.W)
    tk.Entry(params_frame, textvariable=var).pack(fill=tk.X)

# Parametry FIFO_PROCESSING_TIME
tk.Label(params_frame, text="FIFO_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
fifo_processing_time = {
    "normal": tk.DoubleVar(value=0.2),
    "medium": tk.DoubleVar(value=0.5),
    "complicated": tk.DoubleVar(value=1.0)
}
for key, var in fifo_processing_time.items():
    tk.Label(params_frame, text=f"{key}:").pack(anchor=tk.W)
    tk.Entry(params_frame, textvariable=var).pack(fill=tk.X)

# Parametry LIFOPR_PROCESSING_TIME
tk.Label(params_frame, text="LIFOPR_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
lifopr_processing_time = {
    "normal": tk.DoubleVar(value=1.0),
    "medium": tk.DoubleVar(value=0.5),
    "complicated": tk.DoubleVar(value=0.2)
}
for key, var in lifopr_processing_time.items():
    tk.Label(params_frame, text=f"{key}:").pack(anchor=tk.W)
    tk.Entry(params_frame, textvariable=var).pack(fill=tk.X)

# Liczba konsultantów
tk.Label(params_frame, text="Liczba konsultantów (PS/FIFO/LIFO):").pack(anchor=tk.W)
ps_consultants = tk.IntVar(value=5)
fifo_consultants = tk.IntVar(value=5)
lifopr_consultants = tk.IntVar(value=3)
tk.Label(params_frame, text="PS:").pack(anchor=tk.W)
tk.Entry(params_frame, textvariable=ps_consultants).pack(fill=tk.X)
tk.Label(params_frame, text="FIFO:").pack(anchor=tk.W)
tk.Entry(params_frame, textvariable=fifo_consultants).pack(fill=tk.X)
tk.Label(params_frame, text="LIFO:").pack(anchor=tk.W)
tk.Entry(params_frame, textvariable=lifopr_consultants).pack(fill=tk.X)

# Przycisk uruchamiania symulacji
run_button = tk.Button(params_frame, text="Uruchom symulację", command=run_simulation)
run_button.pack(pady=10)

# Obszar wykresu
fig_frame = tk.Frame(root)
fig_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Wyniki symulacji")

canvas = FigureCanvasTkAgg(fig, master=fig_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Uruchomienie aplikacji
root.mainloop()
