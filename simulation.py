import simpy as sp
from network import *

# Adjustable parameters
FIFO_PROCESSING_TIME = {
            'normal'        : 0.2,
            'medium'        : 0.5,
            'complicated'   : 1
        }

IS_PROCESSING_TIME = {
            'normal'        : 0.5,
            'medium'        : 0.5,
            'complicated'   : 0.5
        }

LIFOPR_PROCESSING_TIME = {
            'normal'        : 1,
            'medium'        : 0.5,
            'complicated'   : 0.2
        }

FIFO_CONSULTANTS = 10
IS_CONSULTANTS = 5
LIFOPR_CONSULTANTS = 2

FIFO_PROPABILITIES = {
    'normal' : [0.05, 0.15, 0.8], #convert_to_complicated, convert_to_medium, quit_system
    'medium' : [0.7, 0.3], #stay_medium, convert_to_complicated
    'complicated' : [0.8, 0.2] #stay_complicated, convert_to_medium -> not sure if convert_to_medium makes sense here
}
IS_PROPABILITIES = {
    'medium' : [0.3, 0.3, 0.4] #convert_to_complicated, convert_to_normal, quit_system
}
LIFOPR_PROPABILITIES = {
    'complicated' : [0.4, 0.6] #convert_to_medium, quit_system
}

NUM_CLIENTS = 20
ARRIVAL_RATE = 2 # lambda aka arrival rate in system

# simulation
env = sp.Environment()

# creating departments
fifo_department = DepartmentFIFO(env, 'fifo') #covers only normal issues and every other at start
is_department = DepartmentIS(env, 'is') #covers only medium issues
lifopr_department = DepartmentLIFOPR(env, 'lifopr') #covers only complicated issues

# filling mu in departments
fifo_department._fill_processing_time(FIFO_PROCESSING_TIME)
is_department._fill_processing_time(IS_PROCESSING_TIME)
lifopr_department._fill_processing_time(LIFOPR_PROCESSING_TIME)

# adding consultant
fifo_department._create_consultants(FIFO_CONSULTANTS)
is_department._create_consultants(IS_CONSULTANTS)
lifopr_department._create_consultants(LIFOPR_CONSULTANTS)

# creating routes
route = Route(fifo_department, is_department, lifopr_department)

route._fill_propabilities(FIFO_PROPABILITIES, IS_PROPABILITIES, LIFOPR_PROPABILITIES)

fifo_department._init_route(route)
is_department._init_route(route)
lifopr_department._init_route(route)

env.process(fifo_department._process_clients())
# env.process(is_department._add_client())
env.process(lifopr_department._process_clients())

for client_did in range(1, NUM_CLIENTS+1): 
    env.process(client_arrival(env, client_did, ARRIVAL_RATE, route, logging=True))

env.run() # run simulation