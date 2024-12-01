import simpy as sp
import numpy as np
import pandas as pd
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

NUM_CLIENTS = 20
ARRIVAL_RATE = 2 # lambda aka arrival rate in system


# simulation
env = sp.Environment()

# creating departments
fifo_department = DepartmentFIFO(env, 'fifo', 'normal')
is_department = DepartmentIS(env, 'is', 'medium')
lifopr_department = DepartmentLIFOPR(env, 'lifopr', 'complicated')

# filling mu in departments
fifo_department._fill_processing_time(FIFO_PROCESSING_TIME)
is_department._fill_processing_time(IS_PROCESSING_TIME)
lifopr_department._fill_processing_time(LIFOPR_PROCESSING_TIME)

# adding consultant
fifo_department._create_consultants(FIFO_CONSULTANTS)
is_department._create_consultants(IS_CONSULTANTS)
lifopr_department._create_consultants(LIFOPR_CONSULTANTS)

# creating routes
routes = Route(fifo_department, is_department, lifopr_department)

# simulation parameters (num_clients and lambda)


for ticket_id in range(1, NUM_CLIENTS+1): 
    env.process(client_arrival(env, ticket_id, ARRIVAL_RATE, fifo_department, is_department, lifopr_department))

env.run() # run simulation