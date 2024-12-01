import simpy as sp
import numpy as np
import random

class Client: 
    def __init__(self, client_id, issue_type, arrival_time, priority=0):
        self.client_id = client_id
        self.issue_type = issue_type  # 'normal', 'medium', 'complicated'
        self.arrival_time = arrival_time
        self.current_department = None # keeping track of current department
        self.priority = priority # in range 0 to 10

class Department: 
    def __init__(self, env, name, covered_issue):
        self.env = env
        self.name = name
        self.covered_issue = covered_issue
        self.queue = sp.Store(env)
        self.processing_time = {}  # {'issue_type': mu_value}
        self.consultants = []

    def _fill_processing_time(self, process_time_dict):
        """Initialize processing times for different issue types."""
        self.processing_time = process_time_dict

    def _create_consultants(self, number_of_consultants):
        """Create consultants for the department."""
        for idx in range(number_of_consultants):
            consultant_name = f"Consultant {idx+1}"
            consultant = Consultant(self.env, consultant_name, self.name, self.processing_time)
            self.consultants.append(consultant)

    def _add_client(self, client):
        """Add a client to the department queue."""
        client.current_department = self.name
        self.queue.put(client)

    def _get_available_consultant(self):
        """Find the first available consultant."""
        while True:
            for consultant in self.consultants:
                if not consultant.busy:
                    return consultant
            yield self.env.timeout(0.1)  # Small delay between checks

    def _process_clients(self):
        """Coninously processing clients in the department queue."""
        while True:
            client = yield self.queue.get()
            
            consultant = yield self._get_available_consultant()

            self.env.process(consultant._handle_call(client, self.env.now - client.arrival_time))


class DepartmentFIFO(Department):
    """Department with FIFO (First In, First Out) processing."""
    def __init__(self, env, name, covered_issue):
        super().__init__(env, name, covered_issue)

    def _process_clients(self):
        """Process clients in FIFO order."""
        while True:
            client = yield self.queue.get()

            consultant = yield self._get_available_consultant()

            self.env.process(consultant._handle_call(client, self.env.now - client.arrival_time))


class DepartmentIS(Department):
    """Department with IS processing."""
    def __init__(self, env, name, covered_issue):
        super().__init__(env, name, covered_issue)

    def _process_clients(self):
        """Process clients using consultants, rejecting them if none are available."""
        while True:
            client = yield self.queue.get()

            # Try to find an available consultant
            consultant = yield self._get_available_consultant_or_reject(client)

            if consultant:
                # If a consultant is available, process the client
                self.env.process(self._simulate_processing(client, consultant))
            else:
                # If no consultant is available, reject the client
                print(f"Client {client.client_id} rejected due to no available consultants.")

    def _get_available_consultant_or_reject(self, client):
        """Find an available consultant or reject the client after a timeout."""
        timeout = 1 
        start_time = self.env.now
        while self.env.now - start_time < timeout:
            for consultant in self.consultants:
                if not consultant.busy:
                    return consultant
            yield self.env.timeout(0.1)  
        return None # rejecting because of lack of queue
    
    def _simulate_processing(self, client, consultant):
        """Simulate processing of a client by a consultant."""
        consultant.busy = True
        service_time = np.random.exponential(1 / self.processing_time[client.issue_type])
        print(
            f"Client {client.client_id} is being processed by {consultant.name} "
            f"in {self.name} with service time {service_time:.2f}."
        )
        yield self.env.timeout(service_time)
        consultant.busy = False
        print(f"Client {client.client_id} finished processing by {consultant.name}.")


class DepartmentLIFOPR(Department):
    """Department with Last In, First Out with Preemption (LIFOPR)."""
    def __init__(self, env, name, covered_issue):
        super().__init__(env, name, covered_issue)
        self.current_process = None

    def _process_clients(self):
        """Process clients with LIFO and priority preemption."""
        while True:

            if len(self.queue.items) > 0:
                self.queue.items.sort(key=lambda c: c.priority, reverse=True)  # Sort by priority
                client = self.queue.items.pop()

                if self.current_process:
                    self.current_process.interrupt()

                consultant = yield self._get_available_consultant()

                self.current_process = self.env.process(
                    consultant._handle_call(client, self.env.now - client.arrival_time)
                )
            yield self.env.timeout(0.1)


class Consultant:
    def __init__(self, env, name, department, processing_time):
        self.env = env
        self.name = name
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
            print(f"{self.name} is handling Client {client.client_id} for {service_time:.2f} seconds "
                  f"(Wait time: {wait_time:.2f} seconds)")
        
        yield self.env.timeout(service_time)
        self.time_on_calls += service_time
        self.time_on_previous_call = service_time
        self._take_break()
        self.busy = False

    def _take_break(self):
        """Simulates a break between calls."""
        self.break_duration = max(self.time_on_previous_call / 3, 1)  # At least one-minute break
        if self.loggs:
            print(f"{self.name} is taking a break for {self.break_duration:.2f} seconds")
        yield self.env.timeout(self.break_duration)
        self.time_on_breaks += self.break_duration


class Route:
    def __init__(self, fifo_department, is_department, lifopr_department):
        self.fifo_department = fifo_department
        self.is_department = is_department
        self.lifopr_department = lifopr_department

    def _first_arrival(self, client):
        """Route new clients to the FIFO department."""
        if client.issue_type == 'complicated':
            client.priority = 10 # if client start as complicated it gets high priority in lifopr

        client.current_department = self.fifo_department.name
        self.fifo_department._add_client(client)

    def _route_client(self, client):
        """Reroute clients based on their issue type."""
        if client.issue_type == 'normal':
            pass
        elif client.issue_type == 'medium':
            pass
        elif client.issue_type == 'complicated':
            pass


def client_arrival(env, client_id, arrival_rate, route, logging=False):
    """Simulate client arrival and routing."""
    issue_types = ['normal', 'medium', 'complicated']
    issue_type = random.choice(issue_types)
    client = Client(client_id, issue_type, env.now)

    if logging:
        print(f"Client {client_id} arrives with a {issue_type} issue at time {env.now:.2f}.")

    route._first_arrival(client)
    yield env.timeout(arrival_rate)