#solution: {0: [0, 20, 24, 25, 27, 29, 30, 28, 26, 23, 22, 21, 0],
# 1: [0, 67, 65, 63, 62, 74, 72, 61, 64, 66, 0],
# 2: [0, 5, 3, 7, 8, 10, 11, 9, 6, 4, 2, 75, 0],
# 3: [0, 43, 42, 57, 41, 40, 44, 46, 45, 48, 51, 50, 52, 49, 47, 0],
# 4: [0, 90, 87, 86, 83, 82, 84, 85, 88, 89, 91, 0],
# 5: [0, 13, 17, 18, 19, 15, 16, 14, 12, 0],
# 6: [0, 32, 33, 31, 35, 37, 38, 39, 36, 34, 0],
# 7: [0, 98, 96, 95, 94, 92, 93, 97, 100, 99, 1, 0],
# 8: [0, 55, 54, 53, 56, 58, 60, 59, 68, 69, 0],
# 9: [0, 81, 78, 76, 71, 70, 73, 77, 79, 80, 0],
# 10: [0, 0], 11: [0, 0], 12: [0, 0], 13: [0, 0],
# 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [0, 0],
# 18: [0, 0], 19: [0, 0], 20: [0, 0], 21: [0, 0],
# 22: [0, 0], 23: [0, 0], 24: [0, 0]}


class checker_solution(object):
    def __init__(self,solution,intance_data,running_para):
        self.solution = solution
        self.instance_data = intance_data
        self.log = open('./log/log_check_'+running_para+'.log', 'w')
        self.C_vehicle_num = False
        self.C_visited_once = False
        self.C_capacity = False
        self.C_time_window =False
        self.C_time_increasement = False
        self.data_assemble()
        self.check_vehicle_num()
        self.check_visit_once()
        self.check_capacities()
        self.check_time_windows()

    def data_assemble(self):
        # print('self.solution:',self.solution.items())
        solution_copy ={}
        for key, value in self.solution.items():
            # Check if the length of the value is 2
            if len(value) == 2:
                # If so, delete the item from the dictionary
                continue
            else:
                solution_copy[key] = value
        self.solution = solution_copy
        for key, value in self.solution.items():
            self.log.write(f'{key}:{value}\n' )
            self.log.flush()

    def check_vehicle_num(self):
        print('number of vehicles limit constraint check....')
        self.log.write(f'check_vehicle_num:\n')
        self.log.flush()
        route_num = len(self.solution)
        empty_vehicle_num = self.instance_data["num_vehicles"] - route_num
        if empty_vehicle_num >= 0:
            self.C_vehicle_num = True
            print('number of vehicles limit constraint check:PASS!')
        assert self.C_vehicle_num == True
        print('empty_vehicle_num',empty_vehicle_num)
        self.log.write(f'empty_vehicle_num:{empty_vehicle_num}\n')
        self.log.flush()
        return self.C_vehicle_num, empty_vehicle_num

    def check_visit_once(self):
        print('node being visit once check...')
        node_visited = []
        node_num = len(self.instance_data["time_matrix"])
        node_list = range(1,node_num)

        for key, value in self.solution.items():
            value = value[1:-1]
            node_visited.extend(value)

        node_visited_sort = sorted(node_visited)
        sublist_length = 10
        # sublists = [node_visited_sort[i:i + sublist_length] for i in range(0, len(node_visited_sort), sublist_length)]
        sublists=[]
        for i in range(0, len(node_visited_sort), sublist_length):
            sublist = node_visited_sort[i:i + sublist_length]
            sublists.append(sublist)

        self.log.write(f'node_visited:\n')
        self.log.flush()
        for sublist in sublists:
            self.log.write(f'{str(sublist)}\n' )
            self.log.flush()
        repeat_elements = set([x for x in node_visited if node_visited.count(x) > 1])
        diff_elements = set(node_list)-set(node_visited)
        if len(diff_elements) == 0 and len(repeat_elements) == 0:
            self.C_visited_once=True
            print('node being visit once check:PASS!')
        # print('node_visited:', node_visited.sort() )
        assert self.C_visited_once==True

        return self.C_visited_once, repeat_elements, diff_elements

    def check_capacities(self):
        print('capacities constraint check...')
        self.log.write('capacities constraint check:\n')
        capacity_break_sum = 0
        capacity_break_list = []
        for key, value in self.solution.items():
            load_demand = 0
            load_demand_list = []
            load_demand_list.append(load_demand)
            capacity = self.instance_data["vehicle_capacities"]
            for visit_node in value:
                load_demand += self.instance_data["demands"][visit_node]
                load_demand_list.append(load_demand)
            if load_demand > capacity[key]:
                capacity_break_sum +=1
                capacity_break_list.append(key)
            self.log.write(f'vehicle:{key},capacity:{capacity[key]},load_list:{load_demand_list}\n')
            self.log.flush()
        if capacity_break_sum == 0:
            self.C_capacity = True
            print('capacities constraint check: PASS!')
        assert self.C_capacity == True
        return self.C_capacity, capacity_break_list

    def check_time_windows(self):
        # due_per_route = self.instance_data['time_windows'][depot][1]
        print('time windows constraint check...')
        constraint_break =0
        depot = self.instance_data["depot"]
        self.log.write('time windows constraint check:\n')
        for key, value in self.solution.items():
            dept = self.instance_data['time_windows'][depot][0]
            time_window_a = self.instance_data['time_windows'][depot][0]
            time_window_b = self.instance_data['time_windows'][depot][1]
            event_log = []
            # event_log.append((0, dept),())
            event_log.append(( depot, dept, (0, dept), (time_window_a, time_window_b) ))
            pre_node = 0
            for id, node in enumerate( value[1:] ):
                cur_node = node
                arrival = dept + self.instance_data['time_matrix'][pre_node][cur_node] # arrival time

                time_window_a = self.instance_data['time_windows'][cur_node][0]
                time_window_b = self.instance_data['time_windows'][cur_node][1]

                # departure time
                if arrival <= time_window_b:     # arrival before b
                    if arrival < time_window_a: # arrival before a
                       dept = time_window_a     # wait till to a
                    else:                       # arrival between [a, b]
                       dept = arrival
                else:                           # arrival after b
                    constraint_break +=1
                    dept = arrival
                    print('time windown constraint error!')
                    self.log.write('time windown constraint error!\n')
                    print(f"pre_node:{pre_node}, cur_node:{cur_node},travel time:{self.instance_data['time_matrix'][pre_node][cur_node]}")
                    self.log.write(f"pre_node:{pre_node}, cur_node:{cur_node},travel time:{self.instance_data['time_matrix'][pre_node][cur_node]}\n")
                    print(f'node:{node},arrival:{arrival},time window:[{time_window_a},{time_window_b}]')
                    self.log.write(f'node:{node},arrival:{arrival},time window:[{time_window_a},{time_window_b}]\n')
                    print(f'vehicle:{key},load_evnets_log:{event_log}')
                    self.log.write(f'vehicle:{key},load_evnets_log:{event_log}\n')
                    # assert self.C_time_window == True

                event_log.append(( cur_node, dept,(arrival, dept),(time_window_a,time_window_b)) )
                pre_node = cur_node
            self.log.write(f'visiting times of vehicle:{key}:{event_log}\n')
            self.log.flush()
        if constraint_break==0:
            self.C_time_window = True
            print('time windows constraint check: PASS!')
        else:
            print('time windows constraint check: FAIL!')
        return  self.C_time_window

    def __str__(self):
        return f"vehicle limit: {self.C_vehicle_num}, visit once: {self.C_visited_once}, capacities: {self.C_capacity}, time windwos: {self.C_time_window}"




