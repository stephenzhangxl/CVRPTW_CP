from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from models.data_model import ProblemInstance
from models.solver_model import SolverSetting

class Solver:
    """
    Solver object that takes a problem instance as input, creates and solves a capacitated vehicle routing problem with time
    windows. Objective of the optimization are hierarchical: 1) Minimize number of vehicles 2) Minimize total distance.
    Distance is Euclidean, and the value of travel time is equal to the value of distance between two nodes.

    Parameters
    ----------
    data : ProblemInstance
        Problem data according to ProblemInstance model.
    time_precision_scaler : int
        Variable defining the precision of travel and service times, e.g. 100 means precision of two decimals.
    """

    def __init__(self, data: ProblemInstance, time_precision_scaler: int):
        self.data = data
        self.time_precision_scaler = time_precision_scaler
        self.manager = None
        self.routing = None
        self.solution = None

    def create_model(self):
        """
        Create vehicle routing model for Solomon instance.
        """
        # Create the routing index manager, i.e. number of nodes, vehicles and depot
        self.manager = pywrapcp.RoutingIndexManager(
            len(self.data["time_matrix"]), self.data["num_vehicles"], self.data["depot"]
        )

        # Create routing model
        self.routing = pywrapcp.RoutingModel(self.manager)

        # Create and register a transit callback
        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from solver internal routing variable Index to time matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.data["time_matrix"][from_node][to_node]

        transit_callback_index = self.routing.RegisterTransitCallback(time_callback)

        # Define cost of each arc and fixed vehicle cost
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        # Make sure to first minimize number of vehicles
        self.routing.SetFixedCostOfAllVehicles(0)

        # Create and register demand callback
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            return self.data["demands"][from_node]

        demand_callback_index = self.routing.RegisterUnaryTransitCallback(
            demand_callback
        )

        # Register vehicle capacitites
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Add Time Windows constraint.
        self.routing.AddDimension(
            transit_callback_index,
            10 ** 10,  # allow waiting time at nodes
            10 ** 10,  # maximum time per vehicle route
            False,  # Don't force start cumul to zero, i.e. vehicles can start after time 0 from depot
            "Time",
        )

        time_dimension = self.routing.GetDimensionOrDie("Time")

        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(self.data["time_windows"]):
            if location_idx == self.data["depot"]:
                continue
            index = self.manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add time window constraints for each vehicle start node.
        depot_idx = self.data["depot"]
        for vehicle_id in range(self.data["num_vehicles"]):
            index = self.routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                self.data["time_windows"][depot_idx][0],
                self.data["time_windows"][depot_idx][1],
            )
        # The solution finalizer is called each time a solution is found during search
        # and tries to optimize (min/max) variables values
        for i in range(self.data["num_vehicles"]):
            self.routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self.routing.Start(i))
            )
            self.routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self.routing.End(i))
            )

    def solve_model(self, settings: SolverSetting):
        """
        Solver model with solver settings.
        Parameters
        ----------
        settings : SolverSetting
            Solver settings according to SolverSetting model.
        """
        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = settings["time_limit"]

        # Solve the problem.
        self.solution = self.routing.SolveWithParameters(search_parameters)
        print(f'type of solution:{ type(self.solution) }')

    def print_solution(self):
        """
        Print solution to console.
        """
        route_solution={}
        total_service_time = sum(self.data["service_times"])
        print(f"Solution status: {self.routing.status()}")
        print(f"get all dimension:",self.routing.GetAllDimensionNames())
        if self.routing.status() == 1:
            print( f"Objective: {self.solution.ObjectiveValue()/self.time_precision_scaler}" )
            time_dimension = self.routing.GetDimensionOrDie("Time")
            cap_dimension = self.routing.GetDimensionOrDie("Capacity")
            total_time = 0
            total_vehicles = 0
            travel_time_all_routes=[]
            for vehicle_id in range(self.data["num_vehicles"]):
                route_list=[]
                # print(f"Information for vehicle {vehicle_id}")
                plan_output = f"Route for vehicle {vehicle_id}.\n"
                plan_output_2 = f"Route for vehicle {vehicle_id}:\n"

                index = self.routing.Start(vehicle_id)
                time_var = time_dimension.CumulVar(index)
                # print(f'CumulVar: {time_var} of index:{index}')
                cap_var = cap_dimension.CumulVar(index)
                travel_time_per_route = []

                route_list.append(self.manager.IndexToNode(index))

                plan_output_2 += f"{self.manager.IndexToNode(index)} ({time_var},{cap_var})"
                while not self.routing.IsEnd(index):
                    # time_var = time_dimension.CumulVar(index)
                    # cap_var = cap_dimension.CumulVar(index)
                    index_next = self.solution.Value(self.routing.NextVar(index))

                    time_var = time_dimension.CumulVar(index_next)
                    cap_var = cap_dimension.CumulVar(index_next)
                    Node_cur = self.manager.IndexToNode(index)
                    Node_next = self.manager.IndexToNode(index_next)
                    travle_time = self.data["time_matrix"][Node_cur][Node_next]
                    travel_time_per_route.append(travle_time)
                    route_list.append(Node_next)
                    #print(f'CumulVar: {time_var} of index:{index_next}')
                    plan_output += f"{self.manager.IndexToNode(index)} -> "
                    index=index_next
                    # print(f'from Node {Node_cur} to Node {Node_next}: travel time:{travle_time}')
                    plan_output_2 += f"->{Node_next}({travle_time},{time_var},{cap_var})"
                time_var = time_dimension.CumulVar(index)
                # print(plan_output_2)
                # print(f'travel_time_per_route:{travel_time_per_route}')
                travel_time_all_routes.append(travel_time_per_route)
                route_solution[vehicle_id] = route_list
                total_time += self.solution.Min(time_var) / self.time_precision_scaler
                if self.solution.Min(time_var) > 0:
                    total_vehicles += 1

            print(f'travel_time_all_routes:{travel_time_all_routes}')
            flat_list = [item for sublist in travel_time_all_routes for item in sublist]

            total_travle_time_1 = int( sum(flat_list) *10) /10 - total_service_time
            print(f'Total time of all routes:{total_travle_time_1}')

            total_travel_time = ( total_time - sum(self.data["service_times"]) \
                                  / self.time_precision_scaler )
            print(f"Total vehicles used: {total_vehicles}")

        return total_travle_time_1,total_vehicles,route_solution,total_time
