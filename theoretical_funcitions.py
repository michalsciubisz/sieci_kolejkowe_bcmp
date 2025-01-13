import math
from itertools import product


def compute_state_probabilities(lambda_r, e_ir, mu_i, m_i, max_clients, station_types):
    """
    Compute probabilities of each state in a BCMP network.

    Parameters:
    - lambda_r: List of arrival rates for each class (R).
    - e_ir: Matrix of visit ratios (R x N).
    - mu_i: List of service rates for each station (N).
    - m_i: List of number of servers for each station (N).
    - max_clients: Maximum number of clients in the system.
    - station_types: List of station types (FIFO, PS, LIFOPR) for each station.

    Returns:
    - probabilities: Dictionary with states as keys and probabilities as values.
    """
    R = len(lambda_r)  # Number of classes
    N = len(mu_i)  # Number of stations

    # Step 1: Compute rho_ir and rho_i for each station
    rho_ir = [
        [
            (lambda_r[r] * e_ir[r][i - 1]) / (
                    mu_i[i - 1] * (m_i[i - 1] if station_types[i - 1] == "FIFO" and m_i[i - 1] > 1 else 1)
            )
            for i in range(1, N + 1)
        ]
        for r in range(R)
    ]
    rho_i = [sum(rho_ir[r][i - 1] for r in range(R)) for i in range(1, N + 1)]

    # Step 2: Compute pi_i(k_i) for each station
    def pi_i_ki(k, i):
        """
        Compute the probability pi_i(k_i) for station i and state k_i.
        """
        ro = rho_i[i-1]
        m = m_i[i-1]
        station_type = station_types[i-1]

        if station_type in ["PS", "LIFOPR"] or (station_type == "FIFO" and m == 1):
            # Single-server PS, LIFOPR, or FIFO
            return (1 - ro) * (ro ** k)
        elif station_type == "FIFO" and m > 1:
            # Multi-server FIFO
            if k < m:
                # Case: k < m
                normalization_constant = sum(
                    ((m * ro) ** j) / math.factorial(j) for j in range(m)
                ) + ((m * ro) ** m) / (math.factorial(m) * (1 - ro))
                return (((m * ro) ** k) / math.factorial(k)) / normalization_constant
            else:
                # Case: k >= m
                normalization_constant = sum(
                    ((m * ro) ** j) / math.factorial(j) for j in range(m)
                ) + ((m * ro) ** m) / (math.factorial(m) * (1 - ro))
                return ((m ** m * ro ** k) / (math.factorial(m))) / normalization_constant
        else:
            raise ValueError("Unsupported station type")

    # Step 3: Compute pi(k1, ..., kN) for all states
    def generate_valid_states(N, max_clients):
        """
        Generate all valid states (k1, ..., kN) such that the total number
        of clients in the network does not exceed `max_clients`.
        """
        states = []
        for state in product(range(max_clients + 1), repeat=N):
            if sum(state) <= max_clients:
                states.append(state)
        return states

    valid_states = generate_valid_states(N, max_clients)

    # Step 4: Compute pi(k1, ..., kN) for all valid states
    probabilities = {}
    for state in valid_states:
        prob = 1
        for i, k in enumerate(state, start=1):
            prob *= pi_i_ki(k, i)
        probabilities[state] = prob

    return probabilities


# Example inputs
lambda_r = [2.0, 1.5, 1.0]  # Arrival rates for 3 classes
e_ir = [
    [0.5, 0.3, 0.2],  # Visit ratios for class 1
    [0.4, 0.4, 0.2],  # Visit ratios for class 2
    [0.3, 0.3, 0.4]   # Visit ratios for class 3
]
mu_i = [1.0, 1.5, 2.0]  # Service rates for 3 stations
m_i = [1, 2, 1]  # Number of servers at each station
max_clients = 2  # Max clients in the system
station_types = ["FIFO", "PS", "LIFOPR"]  # Station types

# Compute probabilities
probabilities = compute_state_probabilities(lambda_r, e_ir, mu_i, m_i, max_clients, station_types)

# Print results
for state, prob in probabilities.items():
    print(f"p{state} = {prob:.4f}")