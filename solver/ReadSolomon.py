import math
import os

class readsolomon(object):
    def __init__(self,file_name,speed):
        self.file_name = file_name
        self.speed = speed
        # self.time_matrix = []
        self.data = {}
        self.data['depot'] = 0
        self.calculate_time()

    def extract_data(self):
        data = []
        self.data['demands']=[]
        self.data['time_windows'] =[]
        self.data['service_time'] =[]
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if i==4:
                    num_vehicle, capacity = [ int(value) for value in line.split() ]
                    # self.num_vehicle = num_vehicle
                    capacity = [capacity for _ in range(num_vehicle)]
                    # print('capacity:', self.capacity)
                    self.data['num_vehicles'] = num_vehicle
                    # print('self.num_vehicle, self.capacity:',self.num_vehicle, self.capacity)
                    self.data['vehicle_capacity'] = capacity
                if i>8 and len(line) >0:
                    # print( 'i,line :',i, line )
                    customer = {}
                    customer['CUST_NO'],\
                    customer['X'],\
                    customer['Y'],\
                    customer['DEMAND'],\
                    customer['READY_TIME'],\
                    customer['DUE_DATE'],\
                    customer['SERVICE_TIME']  = [ int(value) for value in line.split() ]

                    self.data['demands'].append(customer['DEMAND'])
                    self.data['time_windows'].append((customer['READY_TIME'],customer['DUE_DATE']))
                    self.data['service_time'].append(customer['SERVICE_TIME'])
                    data.append(customer)
        return data

    def calculate_time(self):
        data = self.extract_data( )
        time_matrix=[]
        for i, customer in enumerate(data):
            # print( 'customer:', customer)
            x_1 = data[i]['X']
            y_1 = data[i]['Y']
            time_matrix_single = []

            for j in range(len(data)):
                x_2 = data[j]['X']
                y_2 = data[j]['Y']
                # print('x_1,y_1:', x_1, y_1)
                # print('x_2, y_2:',x_2, y_2)
                time_travel =int( math.floor( 10 * math.sqrt( pow((x_1 - x_2),2) + pow((y_1 - y_2),2 ) ) )/(10 * self.speed) + self.data['service_time'][i] )
                # print( 'time_travel:', time_travel )
                time_matrix_single.append(time_travel)
            time_matrix.append(time_matrix_single)

        self.data['time_matrix'] = time_matrix

def main():
    fil_name = os.getcwd()+'\Data\size100\c101.txt'
    # print(os.getcwd())
    file_read = readsolomon(fil_name,1)
    file_read.calculate_time()
    print('demands:', file_read.data['demands'])
    print('vehicle_capacity:', file_read.data['vehicle_capacity'])
    print('num_vehicles:', file_read.data['num_vehicles'])
    print('time_windows:', file_read.data['time_windows'])

if __name__ == '__main__':
   main()