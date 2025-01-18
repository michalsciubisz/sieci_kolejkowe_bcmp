from datetime import datetime
import simpy as sp
import numpy as np
import random


class Results:
    def __init__(self):
        self.queue_size = [0]
        self.queue_change_time = [0]
        self.processed_clients = [0]
        self.processed_clients_time = [0]


class Client:
    def __init__(self, client_id, issue_type, arrival_time, priority=0):
        self.client_id = client_id
        self.client_name = f"Client {client_id}"
        self.issue_type = issue_type  # 'normal', 'medium', 'complicated'
        self.arrival_time = arrival_time # env.now()
        self.current_department = None # keeping track of current department
        self.priority = priority # in range 0 to inf, at start max value 10 for complicated cases increase with each convertion of class
        self.issue_history = []
        self.last_wait = arrival_time
        self.wait_times = []


class Department:
    def __init__(self, env, name):
        self.env = env
        self.department_name = name

        self.queue = sp.Store(env)  # Created for each department, not used by IS
        self.processing_time = {}  # {'issue_type': mu_value}
        self.consultants = []
        self.route = None

        # Data tracking
        self.results = Results()

    def _fill_processing_time(self, process_time_dict):
        """Initialize processing times for different issue types."""
        self.processing_time = process_time_dict

    def _init_route(self, given_route):
        """Init route based on created Route instance in simulation."""
        self.route = given_route

    def _create_consultants(self, number_of_consultants):
        """Create consultants for the department."""
        for idx in range(1, number_of_consultants + 1):
            consultant_name = f"Consultant {idx}"
            consultant = Consultant(self.env, consultant_name, self.department_name, self.processing_time)
            self.consultants.append(consultant)

    def _add_client(self, client):
        """Add a client to the department queue."""
        client.current_department = self.department_name
        self.queue.put(client)
        self._register_queue_change()

    def _get_available_consultant(self):
        """Find the first available consultant."""
        while True:
            for consultant in self.consultants:
                if not consultant.busy:
                    return consultant
            yield self.env.timeout(0.1)  # Small delay between checks

    def _register_processed_clients(self):
        self.results.processed_clients.append(len(self.results.processed_clients) + 1)  # Track queue size
        self.results.processed_clients_time.append(self.env.now)

    def _register_queue_change(self):
        self.results.queue_size.append(len(self.queue.items))  # Track queue size
        self.results.queue_change_time.append(self.env.now)

class DepartmentPS(Department):
    """Department with PS (Processor Sharring) processing."""
    def __init__(self, env, name):
        super().__init__(env, name)
        self.active_clients = []

    def _generate_cox_time(self, client):
        """Generate service time using Cox distribution."""
        cox_params = self.processing_time[client.issue_type]
        phases = cox_params['phases']
        rates = cox_params['rates']
        weights = cox_params['weights']

        phase = np.random.choice(phases, p=weights)
        return np.random.exponential(1 / rates[phase])

    def _process_clients(self):
        """Process clients using Processor Sharing."""
        while True:
            if self.active_clients:
                total_clients = len(self.active_clients)
                time_slice = 1.0 / total_clients

                for client in self.active_clients[:]:
                    consultant = yield from self._get_available_consultant()

                    if consultant:
                        remaining_service_time = self._generate_cox_time(client)
                        allocated_time = min(time_slice, remaining_service_time)

                        consultant.busy = True
                        yield self.env.timeout(allocated_time)
                        remaining_service_time -= allocated_time

                        if remaining_service_time <= 0:
                            self.active_clients.remove(client)
                            print(f"{client.client_name} processed  by PS in {self.env.now - client.last_wait} seconds.")
                            client.last_wait = self.env.now
                            self.env.process(self.route._route_client(client))
                            self._register_processed_clients()
                            self._register_queue_change()
                        consultant.busy = False

            yield self.env.timeout(0.1)  # Małe opóźnienie między iteracjami

    def _add_client(self, client):
        """Add a client to the department for processing."""
        client.current_department = self.department_name
        self.active_clients.append(client)

class DepartmentFIFO(Department):
    def __init__(self, env, name):
        super().__init__(env, name)

    def _process_clients(self):
        """Process clients in FIFO order."""
        while True:
            client = yield self.queue.get()  # Pobierz klienta z kolejki
            self.env.process(self._assign_consultant(client))  # Przetwarzaj osobno każdego klienta

    def _assign_consultant(self, client):
        """Find consultant and handle client separately."""
        consultant = yield from self._get_available_consultant()
        if consultant:
            yield self.env.process(consultant._handle_call(client))  # Przetwarzanie w osobnym procesie
            self.env.process(self.route._route_client(client))  # Reroute client after processing
            self._register_processed_clients()
            self._register_queue_change()


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
                    yield self.env.process(
                        consultant._handle_call(client)
                    )
                    self.env.process(self.route._route_client(client))  # Re-route the client after processing
                    self._register_processed_clients()
                    self._register_queue_change()
            yield self.env.timeout(0.01)  # small delay before rechecking the queue

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

    def _handle_call(self, client):
        """Simulates handling a call by the consultant."""
        self.busy = True
        self.handled_calls += 1

        service_time = np.random.exponential(1 / self.processing_time[client.issue_type])
        wait_time = self.env.now - client.last_wait
        client.wait_times.append(wait_time)
        if self.loggs:
            print(f"{self.department}: {self.consultant_name} is handling {client.client_name} for {service_time:.2f} seconds "
                  f"(Wait time: {wait_time:.2f} seconds). curr time {self.env.now}")

        yield self.env.timeout(service_time)
        client.last_wait = self.env.now
        self.time_on_calls += service_time
        self.time_on_previous_call = service_time
        self.env.process(self._take_break())
        self.busy = False

    def _take_break(self):
        """Simulates a break between calls."""
        self.break_duration = max(self.time_on_previous_call / 3, 1)  # at least one-minute break
        if self.loggs:
            print(f"{self.department}: {self.consultant_name} is taking a break for {self.break_duration:.2f} seconds")
        yield self.env.timeout(self.break_duration)
        self.time_on_breaks += self.break_duration


class Route:
    def __init__(self, ps_department, fifo_department, lifopr_department):
        self.ps_department = ps_department
        self.fifo_department = fifo_department
        self.lifopr_department = lifopr_department

        self.ps_propabilites = {}
        self.fifo_propabilites = {}
        self.lifopr_propabilites = {}

    def _fill_propabilities(self, ps_prop, fifo_prop, lifopr_prop):
        """Filling propabilites for routes in the system."""
        self.ps_propabilites = ps_prop
        self.fifo_propabilites = fifo_prop
        self.lifopr_propabilites = lifopr_prop

    def _first_arrival(self, client):
        """Route new clients to the FIFO department."""
        if client.issue_type == 'complicated': # addressing higher priority to clients with more complicated problem at start
            client.priority = 10
        elif client.issue_type == 'medium':
            client.priority = 5
        elif client.issue_type == 'normal':
            client.priority = 1

        client.current_department = self.ps_department.department_name
        self.ps_department._add_client(client)

    def _route_client(self, client):
        """Reroute clients based on their issue type and current department."""
        current_department = client.current_department

        if current_department == 'ps':
            probabilities = self.ps_propabilites.get(client.issue_type)
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

        elif current_department == 'fifo':
                probabilities = self.fifo_propabilites.get(client.issue_type)
                outcomes = ['convert_to_complicated', 'convert_to_normal', 'quit_system']
                action = random.choices(outcomes, weights=probabilities, k=1)[0]
                self._process_action(client, action)

        elif current_department == 'lifopr':
            probabilities = self.lifopr_propabilites.get(client.issue_type)
            outcomes = ['convert_to_medium', 'quit_system']
            action = random.choices(outcomes, weights=probabilities, k=1)[0]
            self._process_action(client, action)

        # Add a small timeout to make this function a generator
        yield self.ps_department.env.timeout(0)
        yield self.fifo_department.env.timeout(0)
        yield self.lifopr_department.env.timeout(0)

    def _process_action(self, client, action):
        """Process the selected action based on probabilities."""
        if action == 'convert_to_complicated':
            client.issue_type = 'complicated'
            client.issue_history.append('complicated') #keep track of client visits
            client.priority += 5 # increasing priority for tickets being longer in system in case they end up in lifopr
            self.lifopr_department._add_client(client)
        elif action == 'convert_to_medium':
            client.issue_type = 'medium'
            client.issue_history.append('medium')
            client.priority += 5
            self.fifo_department._add_client(client)
        elif action == 'convert_to_normal':
            client.priority += 5
            client.issue_type = 'normal'
            client.issue_history.append('normal')
            self.ps_department._add_client(client)
        elif action == 'stay_complicated':
            self.lifopr_department._add_client(client)
        elif action == 'stay_medium':
            client.issue_type = 'medium'
            self.fifo_department._add_client(client)
        elif action == 'quit_system':
            print(f"Client {client.client_id} processed succesfully! Client history: {client.issue_history}")

def client_arrival(env, client_id, route, logging=False):
    """Simulate client arrival and routing."""
    issue_types = ['normal', 'medium', 'complicated']
    issue_type = random.choice(issue_types)
    client = Client(client_id, issue_type, env.now)
    client.issue_history.append(issue_type)

    if logging:
        print(f"Client {client_id} arrives with a {issue_type} issue at time {env.now:.2f}.")

    route._first_arrival(client)

    yield env.timeout(0)

def generate_clients(env, num_clients, arrival_rate, route, logging=False):
    """Generate clients over time based on arrival rate."""
    for client_id in range(1, num_clients + 1):
        env.process(client_arrival(env, client_id, route, logging=logging))
        yield env.timeout(arrival_rate)



