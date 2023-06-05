from solver.base_solver import Solver
from util.instance_loader import load_instance
import time as Time
import csv
from checker import checker_solution

def main():
    time_limit = [600,3600,18000]

    time_precision_scaler = 10

    header = ['Instance', 'Total trave time', 'Vehicle used', 'Computation time']
    csv_file= open('my_csv_file.csv', mode='w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(header)
    csv_file.close()

    path_list = ['data/size2000/R_2000.txt']
    for i in range(len(path_list)):
        for j in range(len(time_limit)):
            csv_file = open('my_csv_file.csv', mode='a', newline='')
            writer = csv.writer(csv_file)
            print(f"begin to solve {path_list[i]} with time limit {time_limit[j]}")
            current_time_in_seconds = int(Time.time())
            instance_data = load_instance(path_list[i],time_precision_scaler)

            solver = Solver(instance_data,time_precision_scaler)
            solver.create_model()

            settings={}
            settings['time_limit'] = time_limit[j]

            solver.solve_model(settings)
            total_travel_time,vehicle_used,solution_routes,_ = solver.print_solution()
            total_travel_time_second = total_travel_time/10.

            # path_list = 'data/size100/c101.txt',
            name_segments = path_list[i].split('/')
            file_name_ext = name_segments[-1]
            running_para = file_name_ext[:-4] +'_'+ str(settings['time_limit'])
            check_instance = checker_solution(solution_routes, instance_data ,running_para)
            print(check_instance)

            End_time_in_seconds = int(Time.time())
            time_spend = End_time_in_seconds - current_time_in_seconds
            row=[file_name_ext,total_travel_time_second,vehicle_used,time_limit[j]]
            writer.writerow(row)
            csv_file.close()
            print('time_spend:',time_spend)
            print(f"end to solve {path_list[i]} with time limit {time_limit[j]}\n")
if __name__ == '__main__':
    main()