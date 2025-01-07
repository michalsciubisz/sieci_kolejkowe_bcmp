import simpy as sp
import numpy as np
import random

class Client: 
    def __init__(self, client_id, issue_type, arrival_time, priority=0):
        self.client_id = client_id
        self.client_name = f"Client {client_id}"
        self.issue_type = issue_type  # 'normal', 'medium', 'complicated'
        self.arrival_time = arrival_time # env.now()
        self.current_department = None # keeping track of current department
        self.priority = priority # in range 0 to inf, at start max value 10 for complicated cases increase with each convertion of class

class Department: 
    def __init__(self, env, name):
        self.env = env
        self.department_name = name

        self.queue = sp.Store(env) # created for each department not used by IS
        self.processing_time = {}  # {'issue_type': mu_value}
        self.consultants = []
        self.route = None

    def _fill_processing_time(self, process_time_dict):
        """Initialize processing times for different issue types."""
        self.processing_time = process_time_dict

    def _init_route(self, given_route):
        """Init route based on created Route instance in simulation."""
        self.route = given_route

    def _create_consultants(self, number_of_consultants):
        """Create consultants for the department."""
        for idx in range(1, number_of_consultants+1):
            consultant_name = f"Consultant {idx}"
            consultant = Consultant(self.env, consultant_name, self.department_name, self.processing_time)
            self.consultants.append(consultant)

    def _add_client(self, client):
        """Add a client to the department queue."""
        client.current_department = self.department_name
        self.queue.put(client)

    def _get_available_consultant(self):
        """Find the first available consultant."""
        while True:
            for consultant in self.consultants:
                if not consultant.busy:
                    return consultant
            yield self.env.timeout(0.1)  # small delay between checks

class DepartmentFIFO(Department):
    """Department with FIFO (First In, First Out) processing."""
    def __init__(self, env, name):
        super().__init__(env, name)

    def _process_clients(self):
        """Process clients in FIFO order."""
        while True:
            client = yield self.queue.get()

            consultant = yield from self._get_available_consultant()

            if consultant:
                self.env.process(consultant._handle_call(client, self.env.now - client.arrival_time))
                self.env.process(self.route._route_client(client))  # reroute client after processing
            else:
                print(f"No available consultant for {client.client_name}, please wait.")

class DepartmentIS(Department):
    """Department with Immediate Service (IS) processing."""
    def __init__(self, env, name):
        super().__init__(env, name)

    def _process_clients(self, client):
        """Directly handle the client or reroute/remove them."""
        consultant = yield from self._get_available_consultant()

        if consultant:
            self.env.process(self._simulate_processing(client, consultant))
        else:
            print(f"No consultant available for Client {client.client_id} in {self.department_name}. Deciding next step...")
            self._reroute_or_remove_client(client)

    def _simulate_processing(self, client, consultant):
        """Simulate processing of a client by a consultant."""
        consultant.busy = True
        service_time = np.random.exponential(1 / self.processing_time[client.issue_type])
        print(
            f"{client.client_name} is being processed by {consultant.consultant_name} "
            f"in {self.department_name} with service time {service_time:.2f}."
        )
        yield self.env.timeout(service_time)
        consultant.busy = False
        print(f"{client.client_name} finished processing by {consultant.consultant_name}.")

    def _reroute_or_remove_client(self, client):
        """Reroute the client or remove them from the system using the Route class."""
        action = 'stay_medium'
        self.route._process_action(client, action) # trying to be serviced by is department

class DepartmentLIFOPR(Department):
    """Department with lifo with priorities."""
    def __init__(self, env, name):
        super().__init__(env, name)

    def _process_clients(self):
        """Process clients with LIFO and priority preemption."""
        while True:
            if len(self.queue.items) > 0:
                self.queue.items.sort(key=lambda c: c.priority, reverse=True)  # sort by priority
                client = self.queue.items.pop()

                consultant = yield from self._get_available_consultant()

                if consultant: 
                    self.env.process(
                        consultant._handle_call(client, self.env.now - client.arrival_time)
                    )
                    self.env.process(self.route._route_client(client))  # Re-route the client after processing
                else:
                    print(f"No available consultant for client {client.client_id}, please wait.")
            yield self.env.timeout(0.1)  # small delay before rechecking the queue

class Consultant:
    def __init__(self, env, name, department, processing_time):
        self.env = env
        self.consultant_name = name
        self.department = department
        self.processing_time = processing_time  # {'issue_type': mu_value}

        self.busy = False
        self.loggs = True
        self.handled_calls = 0
        self.break_duration = 0
        self.time_on_breaks = 0
        self.time_on_calls = 0
        self.time_on_previous_call = 0

    def _handle_call(self, client, wait_time):
        """Simulates handling a call by the consultant."""
        self.busy = True
        self.handled_calls += 1

        service_time = np.random.exponential(1 / self.processing_time[client.issue_type])
        if self.loggs:
            print(f"{self.consultant_name} is handling {client.client_name} for {service_time:.2f} seconds "
                  f"(Wait time: {wait_time:.2f} seconds)")
        
        yield self.env.timeout(service_time)
        self.time_on_calls += service_time
        self.time_on_previous_call = service_time
        self._take_break()
        self.busy = False

    def _take_break(self):
        """Simulates a break between calls."""
        self.break_duration = max(self.time_on_previous_call / 3, 1)  # at least one-minute break
        if self.loggs:
            print(f"{self.consultant_name} is taking a break for {self.break_duration:.2f} seconds")
        yield self.env.timeout(self.break_duration)
        self.time_on_breaks += self.break_duration

class Route:
    def __init__(self, fifo_department, is_department, lifopr_department):
        self.fifo_department = fifo_department
        self.is_department = is_department
        self.lifopr_department = lifopr_department

        self.fifo_propabilites = {}
        self.is_propabilites = {}
        self.lifopr_propabilites = {}

    def _fill_propabilities(self, fifo_prop, is_prop, lifopr_prop):
        """Filling propabilites for routes in the system."""
        self.fifo_propabilites = fifo_prop
        self.is_propabilites = is_prop
        self.lifopr_propabilites = lifopr_prop

    def _first_arrival(self, client):
        """Route new clients to the FIFO department."""
        if client.issue_type == 'complicated': # addressing higher priority to clients with more complicated problem at start
            client.priority = 10
        elif client.issue_type == 'medium':
            client.priority = 5
        elif client.issue_type == 'normal':
            client.priority = 1

        client.current_department = self.fifo_department.department_name
        self.fifo_department._add_client(client)

    def _route_client(self, client):
        """Reroute clients based on their issue type and current department."""
        current_department = client.current_department

        if current_department == 'fifo':
            probabilities = self.fifo_propabilites.get(client.issue_type)
            if client.issue_type == 'normal':
                outcomes = ['convert_to_complicated', 'convert_to_medium', 'quit_system']
                action = random.choices(outcomes, weights=probabilities, k=1)[0]
                self._process_action(client, action)
            elif client.issue_type == 'medium':
                outcomes = ['stay_medium', 'convert_to_complicated']
                action = random.choices(outcomes, weights=probabilities, k=1)[0]
                self._process_action(client, action)
            elif client.issue_type == 'complicated':
                outcomes = ['stay_complicated', 'convert_to_medium']
                action = random.choices(outcomes, weights=probabilities, k=1)[0]
                self._process_action(client, action)

        elif current_department == 'is':
                probabilities = self.is_propabilites.get(client.issue_type)
                outcomes = ['convert_to_complicated', 'convert_to_normal', 'quit_system']
                action = random.choices(outcomes, weights=probabilities, k=1)[0]
                self._process_action(client, action)

        elif current_department == 'lifopr':
            probabilities = self.lifopr_propabilites.get(client.issue_type)
            outcomes = ['convert_to_medium', 'quit_system']
            action = random.choices(outcomes, weights=probabilities, k=1)[0]
            self._process_action(client, action)

        # Add a small timeout to make this function a generator
        yield self.fifo_department.env.timeout(0)

    def _process_action(self, client, action):
        """Process the selected action based on probabilities."""
        if action == 'convert_to_complicated':
            client.issue_type = 'complicated'
            client.priority += 5 # increasing priority for tickets being longer in system in case they end up in lifopr
            self.lifopr_department._add_client(client)
        elif action == 'convert_to_medium':
            client.issue_type = 'medium'
            client.priority += 5
            self.is_department._process_clients(client)
        elif action == 'convert_to_normal':
            client.priority += 5
            client.issue_type = 'normal'
            self.fifo_department._add_client(client)
        elif action == 'stay_complicated':
            self.lifopr_department._add_client(client)
        elif action == 'stay_medium':
            client.issue_type = 'medium'
            self.is_department._process_clients(client)
        elif action == 'quit_system':
            print("Client processed succesfully!") #TODO there should be sth more about it, like tracking overall time of client in the server

def client_arrival(env, client_id, arrival_rate, route, logging=False):
    """Simulate client arrival and routing."""
    issue_types = ['normal', 'medium', 'complicated']
    issue_type = random.choice(issue_types)
    client = Client(client_id, issue_type, env.now)

    if logging:
        print(f"Client {client_id} arrives with a {issue_type} issue at time {env.now:.2f}.")

    route._first_arrival(client)
    yield env.timeout(arrival_rate)