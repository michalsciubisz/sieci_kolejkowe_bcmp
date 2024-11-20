import simpy as sp
import numpy as np

class Department: 
    def __init__(self, env, name, issue_types):
        self.env = env
        self.name = name
        self.issue_types = issue_types
        self.consultants = []

    def add_consultant(self, consultant):
        """Function which addes consultant to deparment."""
        self.consultants.append(consultant)

    def get_available_consultant(self):
        """Find first free consultant in the list."""
        while True:
            for consultant in self.consultants:
                if not consultant.busy:
                    return consultant
                yield self.env.timeout(0.1) #Adding small delay between checks

class DeparmentFIFO(Department):
    def __init__(self, env, name, issue_types):
        super().__init__(env, name, issue_types)
        self.queue_size = sp.Store(env)

class DeparmentIS(Department):
    def __init__(self, env, name, issue_types):
        super().__init__(env, name, issue_types)

class DeparmentPS(Department):
    def __init__(self, env, name, issue_types):
        super().__init__(env, name, issue_types)

class DeparmentLIFOPR(Department):
    def __init__(self, env, name, issue_types):
        super().__init__(env, name, issue_types)

class Consultant:
    def __init__(self, env, name, department, mu):
        self.env = env
        self.name = name
        self.department = department
        self.mu = mu

        self.busy = False
        self.loggs = True
        self.handled_calls = 0
        self.break_duration = 0
        self.time_on_breaks = 0
        self.time_on_calls = 0
        self.time_on_previous_call = 0

    def handle_call(self, client, wait_time):
        """Function simulates running a call by consultant."""
        self.busy = True
        self.handled_calls += 1
        service_time = np.random.exponential(1/self.mu)
        if self.loggs:
            print(f"{self.name} is handling {client} for {service_time:.2f} seconds "
                  f"(Wait time: {wait_time:.2f} seconds)")
        yield self.env.timeout(service_time)
        self.time_on_calls += service_time
        self.take_break()
        self.time_on_previous_call = service_time
        self.busy = False

    def take_break(self):
        """Function simulates break between calls."""
        self.break_duration = max(self.time_on_previous_call/3, 1) #At lesat one minute break
        if self.loggs:
            print(f"{self.name} is taking a break for {self.break_duration:.2f} seconds")
        yield self.env.timeout(self.break_duration)
        self.time_on_breaks += self.break_duration

class Client: 
    def __init__(self, client_id, issue_type, arrival_time):
        self.client_id = client_id
        self.issue_type = issue_type
        self.arrival_time = arrival_time
