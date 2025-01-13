import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulation import run_simulation
from theoretical_funcitions import compute_state_probabilities

# Main application window
root = tk.Tk()
root.title("Symulacja Sieci Kolejkowej BCMP")

# Expandable Section with Toggle
class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.is_expanded = tk.BooleanVar(value=False)

        # Header with toggle button
        self.header = tk.Frame(self)
        self.header.pack(fill=tk.X)
        self.toggle_button = tk.Button(self.header, text=f"► {title}", command=self.toggle, relief=tk.FLAT)
        self.toggle_button.pack(side=tk.LEFT, anchor=tk.W)
        self.content = tk.Frame(self)
        self.content.pack(fill=tk.X, padx=10, pady=5)
        self.content.pack_forget()  # Initially hidden

    def toggle(self):
        """Expand or collapse the section."""
        if self.is_expanded.get():
            self.content.pack_forget()
            self.toggle_button.config(text=f"► {self.title}")
        else:
            self.content.pack(fill=tk.X, padx=10, pady=5)
            self.toggle_button.config(text=f"▼ {self.title}")
        self.is_expanded.set(not self.is_expanded.get())

# Panel for parameters
params_frame = tk.Frame(root)
params_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# === Parameters ===

# General Parameters Section
general_section = CollapsibleSection(params_frame, "General Parameters")
general_section.pack(fill=tk.X)
tk.Label(general_section.content, text="Liczba klientów:").pack(anchor=tk.W)
num_clients = tk.IntVar(value=20)
tk.Entry(general_section.content, textvariable=num_clients).pack(fill=tk.X)

tk.Label(general_section.content, text="Tempo przybycia klientów (ARRIVAL_RATE):").pack(anchor=tk.W)
arrival_rate = tk.DoubleVar(value=2.0)
tk.Entry(general_section.content, textvariable=arrival_rate).pack(fill=tk.X)

# PS_Probabilities Section
ps_probs_section = CollapsibleSection(params_frame, "PS_Probabilities")
ps_probs_section.pack(fill=tk.X)
ps_probability = {
    "normal": tk.StringVar(value="0.05, 0.15, 0.8"),
    "medium": tk.StringVar(value="0.7, 0.3"),
    "complicated": tk.StringVar(value="0.8, 0.2")
}
for key, var in ps_probability.items():
    tk.Label(ps_probs_section.content, text=f"{key.capitalize()} Probabilities:").pack(anchor=tk.W)
    tk.Entry(ps_probs_section.content, textvariable=var).pack(fill=tk.X)

# FIFO_Probabilities Section
fifo_probs_section = CollapsibleSection(params_frame, "FIFO_Probabilities")
fifo_probs_section.pack(fill=tk.X)
fifo_probability = {
    "medium": tk.StringVar(value="0.3, 0.3, 0.4")
}
for key, var in fifo_probability.items():
    tk.Label(fifo_probs_section.content, text=f"{key.capitalize()} Probabilities:").pack(anchor=tk.W)
    tk.Entry(fifo_probs_section.content, textvariable=var).pack(fill=tk.X)

# LIFO_Probabilities Section
lifo_probs_section = CollapsibleSection(params_frame, "LIFO_Probabilities")
lifo_probs_section.pack(fill=tk.X)
lifopr_probability = {
    "complicated": tk.StringVar(value="0.4, 0.6")
}
for key, var in lifopr_probability.items():
    tk.Label(lifo_probs_section.content, text=f"{key.capitalize()} Probabilities:").pack(anchor=tk.W)
    tk.Entry(lifo_probs_section.content, textvariable=var).pack(fill=tk.X)

# Processing Times Section
processing_time_section = CollapsibleSection(params_frame, "Processing Times")
processing_time_section.pack(fill=tk.X)

# PS Processing Time
tk.Label(processing_time_section.content, text="PS_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
ps_processing_time = {
    "normal": tk.StringVar(value="0.8, 0.2"),
    "medium": tk.StringVar(value="0.2, 0.5, 0.3"),
    "complicated": tk.StringVar(value="0.1, 0.2, 0.3, 0.4")
}
for key, var in ps_processing_time.items():
    tk.Label(processing_time_section.content, text=f"{key.capitalize()} Weights:").pack(anchor=tk.W)
    tk.Entry(processing_time_section.content, textvariable=var).pack(fill=tk.X)

# FIFO Processing Time
tk.Label(processing_time_section.content, text="FIFO_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
fifo_processing_time = {
    "normal": tk.DoubleVar(value=0.2),
    "medium": tk.DoubleVar(value=0.5),
    "complicated": tk.DoubleVar(value=1.0)
}
for key, var in fifo_processing_time.items():
    tk.Label(processing_time_section.content, text=f"{key.capitalize()}:").pack(anchor=tk.W)
    tk.Entry(processing_time_section.content, textvariable=var).pack(fill=tk.X)

# LIFO Processing Time
tk.Label(processing_time_section.content, text="LIFO_PROCESSING_TIME (normal/medium/complicated):").pack(anchor=tk.W)
lifopr_processing_time = {
    "normal": tk.DoubleVar(value=1.0),
    "medium": tk.DoubleVar(value=0.5),
    "complicated": tk.DoubleVar(value=0.2)
}
for key, var in lifopr_processing_time.items():
    tk.Label(processing_time_section.content, text=f"{key.capitalize()}:").pack(anchor=tk.W)
    tk.Entry(processing_time_section.content, textvariable=var).pack(fill=tk.X)

# Consultants Section
consultants_section = CollapsibleSection(params_frame, "Consultants")
consultants_section.pack(fill=tk.X)
tk.Label(consultants_section.content, text="Liczba konsultantów (PS/FIFO/LIFO):").pack(anchor=tk.W)
ps_consultants = tk.IntVar(value=5)
fifo_consultants = tk.IntVar(value=5)
lifopr_consultants = tk.IntVar(value=3)

tk.Label(consultants_section.content, text="PS:").pack(anchor=tk.W)
tk.Entry(consultants_section.content, textvariable=ps_consultants).pack(fill=tk.X)
tk.Label(consultants_section.content, text="FIFO:").pack(anchor=tk.W)
tk.Entry(consultants_section.content, textvariable=fifo_consultants).pack(fill=tk.X)
tk.Label(consultants_section.content, text="LIFO:").pack(anchor=tk.W)
tk.Entry(consultants_section.content, textvariable=lifopr_consultants).pack(fill=tk.X)

def parse_string_var_to_list(string_var, value_type=float):
    """Convert a comma-separated string in a StringVar to a list of values."""
    return [value_type(v.strip()) for v in string_var.get().split(',')]

def handle_simulation():
    # PS Processing Time
    ps_processing_time_values = {
        key: {
            "phases": list(range(len(parse_string_var_to_list(var)))),  # Generate phases dynamically
            "rates": parse_string_var_to_list(var),
            "weights": parse_string_var_to_list(ps_processing_time[key])  # Assumes matching weights input
        }
        for key, var in ps_processing_time.items()
    }

    # FIFO Processing Time
    fifo_processing_time_values = {
        key: fifo_processing_time[key].get()
        for key in fifo_processing_time
    }

    # LIFO Processing Time
    lifopr_processing_time_values = {
        key: lifopr_processing_time[key].get()
        for key in lifopr_processing_time
    }

    # PS Probabilities
    ps_probabilities_values = {
        key: parse_string_var_to_list(var)
        for key, var in ps_probability.items()
    }

    # FIFO Probabilities
    fifo_probabilities_values = {
        key: parse_string_var_to_list(var)
        for key, var in fifo_probability.items()
    }

    # LIFO Probabilities
    lifopr_probabilities_values = {
        key: parse_string_var_to_list(var)
        for key, var in lifopr_probability.items()
    }

    # Collect other parameters
    num_clients_value = num_clients.get()
    arrival_rate_value = arrival_rate.get()
    consultants_values = {
        "PS": ps_consultants.get(),
        "FIFO": fifo_consultants.get(),
        "LIFO": lifopr_consultants.get()
    }

    try:
        run_simulation(
            ps_processing_time_values,
            fifo_processing_time_values,
            lifopr_processing_time_values,
            ps_consultants.get(),
            fifo_consultants.get(),
            lifopr_consultants.get(),
            ps_probabilities_values,
            fifo_probabilities_values,
            lifopr_probabilities_values,
            num_clients_value,
            arrival_rate_value
        )
    except Exception as e:
        print(f"Simulation Error: {e}")

tk.Button(params_frame, text="Uruchom symulację", command=handle_simulation).pack(pady=10)

# Plot Area
fig_frame = tk.Frame(root)
fig_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Wyniki symulacji")

canvas = FigureCanvasTkAgg(fig, master=fig_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Panel wyników
results_frame = tk.Frame(root)
results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

tk.Label(results_frame, text="Wyniki Symulacji", font=("Arial", 14)).pack(anchor=tk.N)

# Add a text box for probabilities in the right-side panel
probabilities_text = tk.Text(root, height=20, width=50)
probabilities_text.pack(side=tk.RIGHT, padx=10, pady=10)

def update_probabilities():
    # Extract parameters from GUI inputs
    arrival_rates = [float(arrival_rate.get())]
    service_rates = [
        float(ps_processing_time['normal'].get().split(',')[0]),
        float(fifo_processing_time['normal'].get()),
        float(lifopr_processing_time['normal'].get())
    ]
    num_servers = [ps_consultants.get(), fifo_consultants.get(), lifopr_consultants.get()]
    max_clients = num_clients.get()

    # Compute probabilities
    probabilities = compute_state_probabilities(arrival_rates, service_rates, num_servers, max_clients)

    # Display probabilities in the text box
    probabilities_text.delete(1.0, tk.END)
    probabilities_text.insert(tk.END, "\n".join(probabilities))


# Wywołanie aktualizacji przy starcie
update_probabilities()

# Śledzenie zmian w polach
for var in [arrival_rate, ps_processing_time['normal'], fifo_processing_time['normal'], lifopr_processing_time['normal']]:
    var.trace_add('write', lambda *args: update_results())


# Run the application
root.mainloop()
