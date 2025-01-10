import simpy as sp
from network import *

# Adjustable parameters
PS_PROCESSING_TIME = {
    'normal': {
    'phases': [0, 1],
    'rates': [4.0, 2.0],  # Faza 0 jest szybsza
    'weights': [0.8, 0.2]  # 80% czasu weryfikacja, 20% rozwiązanie problemu
    },

    'medium': {
    'phases': [0, 1, 2],
    'rates': [3.0, 1.5, 1.0],  # Szybkość obsługi maleje w późniejszych fazach
    'weights': [0.2, 0.5, 0.3]  # 50% czasu analiza, 20% weryfikacja, 30% rozwiązanie
    },

    'complicated': {
    'phases': [0, 1, 2, 3],
    'rates': [2.5, 1.2, 0.8, 0.5],  # Szybkość obsługi maleje wraz z fazą
    'weights': [0.1, 0.2, 0.3, 0.4]  # Najwięcej czasu spędza na rozwiązaniu problemu
    }
}

FIFO_PROCESSING_TIME = {
            'normal'        : 0.2,
            'medium'        : 0.5,
            'complicated'   : 1
        }

# IS_PROCESSING_TIME = {
#             'normal'        : 0.5,
#             'medium'        : 0.5,
#             'complicated'   : 0.5
#         }

LIFOPR_PROCESSING_TIME = {
            'normal'        : 1,
            'medium'        : 0.5,
            'complicated'   : 0.2
        }

PS_CONSULTANTS = 5
FIFO_CONSULTANTS = 5
LIFOPR_CONSULTANTS = 3


PS_PROPABILITIES = {
    'normal' : [0.05, 0.15, 0.8], #convert_to_complicated, convert_to_medium, quit_system
    'medium' : [0.7, 0.3], #stay_medium, convert_to_complicated
    'complicated' : [0.8, 0.2] #stay_complicated, convert_to_medium -> not sure if convert_to_medium makes sense here
}

FIFO_PROPABILITIES = {
    'medium' : [0.3, 0.3, 0.4] #convert_to_complicated, convert_to_normal, quit_system
}

LIFOPR_PROPABILITIES = {
    'complicated' : [0.4, 0.6] #convert_to_medium, quit_system
}

NUM_CLIENTS = 20
ARRIVAL_RATE = 2 # lambda aka arrival rate in system

# simulation
def run_simulation(ps_pt, fifo_pt, lifopr_pt, ps_co, fifo_co, lifopr_co, ps_prob, fifo_prob, lifopr_prob, clients, arrival_rate):
    env = sp.Environment()

    # creating departments
    ps_department = DepartmentPS(env, 'ps') #covers only medium issues
    fifo_department = DepartmentFIFO(env, 'fifo') #covers only normal issues and every other at start
    lifopr_department = DepartmentLIFOPR(env, 'lifopr') #covers only complicated issues

    # filling mu in departments
    ps_department._fill_processing_time(ps_pt)
    fifo_department._fill_processing_time(fifo_pt)
    lifopr_department._fill_processing_time(lifopr_pt)

    # adding consultant
    ps_department._create_consultants(ps_co)
    fifo_department._create_consultants(fifo_co)
    lifopr_department._create_consultants(lifopr_co)

    # creating routes
    route = Route(ps_department, fifo_department, lifopr_department)

    route._fill_propabilities(ps_prob, fifo_prob, lifopr_prob)

    ps_department._init_route(route)
    fifo_department._init_route(route)
    lifopr_department._init_route(route)

    env.process(ps_department._process_clients())
    env.process(fifo_department._process_clients())
    env.process(lifopr_department._process_clients())

    # Adjust simulation setup
    env.process(generate_clients(env, clients, arrival_rate, route, logging=True))
    env.run()


# run_simulation(PS_PROCESSING_TIME, FIFO_PROCESSING_TIME, LIFOPR_PROCESSING_TIME, PS_CONSULTANTS, FIFO_CONSULTANTS, LIFOPR_CONSULTANTS, PS_PROPABILITIES, FIFO_PROPABILITIES, LIFOPR_PROPABILITIES, NUM_CLIENTS, ARRIVAL_RATE)
