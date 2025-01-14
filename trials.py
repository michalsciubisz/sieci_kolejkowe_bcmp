from simulation import *
import numpy as np

def compute_propability_of_state(ps_values, ps_values_medium, ps_values_comp, fifo_values, lifopr_values, service_rates, arrival_rate, given_state):

    P_0_11 = P_0_12 = P_0_13 = 1
    P_11_33, P_11_22, P_11_0 = ps_values
    P_12_22, P_12_33 = ps_values_medium
    P_13_33, P_13_22 = ps_values_comp

    P_22_33, P_22_11, P_22_0 = fifo_values

    P_33_22, P_33_0 = lifopr_values
    
    # mu_11, mu_12, mu_13, mu_22, mu_33 = service_rates
    mu_11, mu_12, mu_13, mu_22, mu_33 = (24, 32, 48, 20, 44)
    # mu_11, mu_12, mu_13, mu_22, mu_33 = (8, 10, 14, 12, 18)

    A = np.array([
        [1, 0, 0, -P_22_11, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [-P_11_22, -P_12_22, -P_13_22, 1, -P_33_22],
        [-P_11_33, -P_12_33, -P_13_33, -P_22_33, 1]
    ])

    b = np.array([P_0_11, P_0_12, P_0_13, 0, 0])

    e_values = np.linalg.solve(A, b)

    e_11, e_12, e_13, e_22, e_33 = e_values

    arrival_rate = arrival_rate[0]

    p_1 = arrival_rate * e_11 / mu_11 + arrival_rate * e_12 / mu_12 + arrival_rate * e_13 / mu_13
    p_2 = arrival_rate * e_22 / mu_22
    p_3 = arrival_rate * e_33 / mu_33 

    pi_1 = (1-p_1) * (p_1 ** given_state[0])
    pi_2 = (1-p_2) * (p_2 ** given_state[1])
    pi_3 = (1-p_3) * (p_3 ** given_state[2])

    state_propability = pi_1 * pi_2 * pi_3
    return state_propability