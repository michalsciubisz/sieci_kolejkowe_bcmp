import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulation import run_simulation
from propability_function import compute_propability_of_state

ps_processing_time_values = {}
# Main application window
root = tk.Tk()
root.geometry("1100x600")
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

# PS Processing Time Section
ps_processing_time_section = CollapsibleSection(params_frame, "PS Processing Time")
ps_processing_time_section.pack(fill=tk.X)

# PS Processing Time - Rates
tk.Label(ps_processing_time_section.content, text="PS_PROCESSING_TIME - Rates:").pack(anchor=tk.W)
ps_processing_time_rates = {
    "normal": tk.StringVar(value="0.035, 0.1"),
    "medium": tk.StringVar(value="0.018, 0.036, 0.054"),
    "complicated": tk.StringVar(value="0.008, 0.016, 0.024, 0.032")
}
for key, var in ps_processing_time_rates.items():
    tk.Label(ps_processing_time_section.content, text=f"{key.capitalize()} Rates:").pack(anchor=tk.W)
    tk.Entry(ps_processing_time_section.content, textvariable=var).pack(fill=tk.X)

# PS Processing Time - Weights
tk.Label(ps_processing_time_section.content, text="PS_PROCESSING_TIME - Weights:").pack(anchor=tk.W)
ps_processing_time_weights = {
    "normal": tk.StringVar(value="0.8, 0.2"),
    "medium": tk.StringVar(value="0.2, 0.5, 0.3"),
    "complicated": tk.StringVar(value="0.1, 0.2, 0.3, 0.4")
}
for key, var in ps_processing_time_weights.items():
    tk.Label(ps_processing_time_section.content, text=f"{key.capitalize()} Weights:").pack(anchor=tk.W)
    tk.Entry(ps_processing_time_section.content, textvariable=var).pack(fill=tk.X)

# FIFO Processing Time Section
fifo_processing_time_section = CollapsibleSection(params_frame, "FIFO Processing Time")
fifo_processing_time_section.pack(fill=tk.X)

tk.Label(fifo_processing_time_section.content, text="FIFO_PROCESSING_TIME:").pack(anchor=tk.W)
fifo_processing_time = {
    "medium": tk.StringVar(value="0.05")
}
for key, var in fifo_processing_time.items():
    tk.Label(fifo_processing_time_section.content, text=f"{key.capitalize()}:").pack(anchor=tk.W)
    tk.Entry(fifo_processing_time_section.content, textvariable=var).pack(fill=tk.X)

# LIFO Processing Time Section
lifopr_processing_time_section = CollapsibleSection(params_frame, "LIFO Processing Time")
lifopr_processing_time_section.pack(fill=tk.X)

tk.Label(lifopr_processing_time_section.content, text="LIFO_PROCESSING_TIME:").pack(anchor=tk.W)
lifopr_processing_time = {
    "complicated": tk.StringVar(value="0.0227")
}
for key, var in lifopr_processing_time.items():
    tk.Label(lifopr_processing_time_section.content, text=f"{key.capitalize()}:").pack(anchor=tk.W)
    tk.Entry(lifopr_processing_time_section.content, textvariable=var).pack(fill=tk.X)

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
    ps_processing_time_values = {
        key: {
            "phases": list(range(len(parse_string_var_to_list(ps_processing_time_rates[key])))),
            "rates": parse_string_var_to_list(ps_processing_time_rates[key]),
            "weights": parse_string_var_to_list(ps_processing_time_weights[key])
        }
        for key in ps_processing_time_rates
    }

    # FIFO Processing Time
    fifo_processing_time_values = {
        key: float(fifo_processing_time[key].get())
        for key in fifo_processing_time
    }

    # LIFO Processing Time
    lifopr_processing_time_values = {
        key: float(lifopr_processing_time[key].get())
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

    try:
        fifo_results, lifopr_results, ps_results, wait_times, consultant_averages = run_simulation(
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
        update_chart(fifo_results, lifopr_results, ps_results)
        update_results(fifo_results, lifopr_results, wait_times[0], wait_times[1], consultant_averages)

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

def extend_data(fifo_data, lifopr_data, ps_data):
    max_time = max(
        max(fifo_data.processed_clients_time),
        max(lifopr_data.processed_clients_time),
        max(ps_data.processed_clients_time),
        max(fifo_data.queue_change_time),
        max(lifopr_data.queue_change_time),
        max(ps_data.queue_change_time)
    )

    def extend_to_max_time(time_list, value_list, max_time):
        if time_list[-1] < max_time:
            # Add the last value at max_time
            time_list.append(max_time)
            value_list.append(value_list[-1])

    # Extend the queue data
    extend_to_max_time(fifo_data.queue_change_time, fifo_data.queue_size, max_time)
    extend_to_max_time(lifopr_data.queue_change_time, lifopr_data.queue_size, max_time)
    extend_to_max_time(ps_data.queue_change_time, ps_data.queue_size, max_time)

    # Extend the processed clients data
    extend_to_max_time(fifo_data.processed_clients_time, fifo_data.processed_clients, max_time)
    extend_to_max_time(lifopr_data.processed_clients_time, lifopr_data.processed_clients, max_time)
    extend_to_max_time(ps_data.processed_clients_time, ps_data.processed_clients, max_time)

def update_chart(fifo_data, lifopr_data, ps_data):
    extend_data(fifo_data, lifopr_data, ps_data)

    ax.clear()  # Clear the chart
    # Plot queue size
    ax.plot(fifo_data.queue_change_time, fifo_data.queue_size, label="FIFO Queue Size", color="red", linestyle="--")
    ax.plot(lifopr_data.queue_change_time, lifopr_data.queue_size, label="LIFOPR Queue Size", color="green", linestyle="--")
    # ax.plot(ps_data.queue_change_time, ps_data.queue_size, label="PS Queue Size", color="orange")

    # Plot processed clients
    ax.plot(fifo_data.processed_clients_time, fifo_data.processed_clients, label="FIFO Processed Clients", color="red")
    ax.plot(lifopr_data.processed_clients_time, lifopr_data.processed_clients, label="LIFOPR Processed Clients", color="green")
    ax.plot(ps_data.processed_clients_time, ps_data.processed_clients, label="PS Processed Clients", color="orange")

    ax.set_title("Wyniki symulacji")
    ax.set_xlabel("Simulation Time")
    ax.set_ylabel("Count")
    ax.legend()

    canvas.draw()

# Panel wyników
results_frame = tk.Frame(root)
results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

tk.Label(results_frame, text="Wyniki Symulacji", font=("Arial", 14)).pack(anchor=tk.N)


def calculate_mean_queue(queue_change_time, queue_size):
    durations = [queue_change_time[i + 1] - queue_change_time[i] for i in range(len(queue_change_time) - 1)]
    weighted_sum = sum(size * duration for size, duration in zip(queue_size[:-1], durations))
    total_time = queue_change_time[-1] - queue_change_time[0]
    return weighted_sum / total_time if total_time > 0 else 0

def update_results(fifo_data, lifopr_data, lifo_wait_times, fifo_wait_times, averages):
    # Clear previous results
    for widget in results_frame.winfo_children():
        widget.destroy()

    fifo_mean_queue = calculate_mean_queue(fifo_data.queue_change_time, fifo_data.queue_size)
    lifopr_mean_queue = calculate_mean_queue(lifopr_data.queue_change_time, lifopr_data.queue_size)

    tk.Label(results_frame, text="Wyniki Symulacji", font=("Arial", 14)).pack(anchor=tk.N, pady=5)
    tk.Label(results_frame, text=f"FIFO Mean Queue: {fifo_mean_queue:.2f}", font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"LIFOPR Mean Queue: {lifopr_mean_queue:.2f}", font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"FIFO Mean Wait Time For Clients: {fifo_wait_times:.2f}",
             font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"LIFOPR Mean Wait Time For Clients: {lifo_wait_times:.2f}", font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"FIFO Mean Consultant Call Time: {averages['fifo']['avg_call_time']:.2f}",
             font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"LIFOPR Mean Consultant Call Time: {averages['lifopr']['avg_call_time']:.2f}",
             font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"FIFO Mean Consultant Break Time: {averages['fifo']['avg_break_time']:.2f}",
             font=("Arial", 10)).pack(anchor=tk.W)
    tk.Label(results_frame, text=f"LIFOPR Mean Consultant Break Time: {averages['lifopr']['avg_break_time']:.2f}",
             font=("Arial", 10)).pack(anchor=tk.W)

# Add Section for Probability Computation
probability_section = tk.Frame(params_frame)
probability_section.pack(fill=tk.X, pady=10)

tk.Label(probability_section, text="Oblicz Prawdopodobieństwo Stanu", font=("Arial", 12, "bold")).pack(anchor=tk.W)

# State Input Fields
state_frame = tk.Frame(probability_section)
state_frame.pack(fill=tk.X, pady=5)

tk.Label(state_frame, text="Stan (PS, FIFO, LIFO):").pack(side=tk.LEFT)

state_ps = tk.IntVar(value=0)
state_fifo = tk.IntVar(value=0)
state_lifo = tk.IntVar(value=0)

tk.Entry(state_frame, textvariable=state_ps, width=5).pack(side=tk.LEFT, padx=2)
tk.Entry(state_frame, textvariable=state_fifo, width=5).pack(side=tk.LEFT, padx=2)
tk.Entry(state_frame, textvariable=state_lifo, width=5).pack(side=tk.LEFT, padx=2)

# Result Label
probability_result = tk.StringVar(value="Prawdopodobieństwo: N/A")
tk.Label(probability_section, textvariable=probability_result, font=("Arial", 10)).pack(anchor=tk.W)

# Probability Computation Function
def compute_probability():
    state = (state_ps.get(), state_fifo.get(), state_lifo.get())

    try:
        # Collect parameters for computation
        arrival_rates = [float(arrival_rate.get())]
        service_rates = [
            float(fifo_processing_time['medium'].get()),
            float(lifopr_processing_time['complicated'].get())
        ]
        ps_processing_time_values = {
            key: {
                "phases": list(range(len(parse_string_var_to_list(ps_processing_time_rates[key])))),
                "rates": parse_string_var_to_list(ps_processing_time_rates[key]),
                "weights": parse_string_var_to_list(ps_processing_time_weights[key])
            }
            for key in ps_processing_time_rates}

        ps_values = [float(x.strip()) for x in ps_probability["normal"].get().split(",")]
        ps_values_medium = [float(x.strip()) for x in ps_probability["medium"].get().split(",")]
        ps_values_comp = [float(x.strip()) for x in ps_probability["complicated"].get().split(",")]
        fifo_values = [float(x.strip()) for x in fifo_probability["medium"].get().split(",")]
        lifopr_values = [float(x.strip()) for x in lifopr_probability["complicated"].get().split(",")]

        # Compute probability
        probability = compute_propability_of_state(
            ps_values, ps_values_medium, ps_values_comp,
            fifo_values, lifopr_values,
            service_rates, arrival_rates,
            state, ps_processing_time_values
        )

        probability_result.set(f"Prawdopodobieństwo: {probability:.12f}")
    except Exception as e:
        probability_result.set(f"Error: {e}")

# Add Button to Trigger Probability Computation
tk.Button(probability_section, text="Oblicz Prawdopodobieństwo", command=compute_probability).pack(pady=5)


# Wywołanie aktualizacji przy starcie
compute_probability()


# Run the application
root.mainloop()
