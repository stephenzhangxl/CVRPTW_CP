import math
import re

import pandas as pd

from models.data_model import ProblemInstance


def load_instance(problem_path: str, time_precision_scaler: int) -> ProblemInstance:
    """
    Load instance of Solomon benchmark with defined precision scaler.

    Parameters
    ----------
    time_precision_scaler : int
        Variable defining the precision of travel and service times, e.g. 100 means precision of two decimals.
    """

    data = {}
    data["depot"] = 0
    df = pd.read_csv(
        problem_path,
        sep="\s+",
        skiprows=8,
        names=[
            "customer",
            "xcord",
            "ycord",
            "demand",
            "ready_time",
            "due_date",
            "service_time",
        ],
    )
    df["service_time"] = df["service_time"] * time_precision_scaler
    df["ready_time"] = df["ready_time"] * time_precision_scaler
    df["due_date"] = df["due_date"] * time_precision_scaler

    data["service_times"] = list(df.service_time)

    travel_times = df[["xcord", "ycord", "service_time"]].to_dict()
    time_matrix = []
    for i in df.customer:
        time_vector = []
        for j in df.customer:
            if i == j:
                time_vector.append(0)
            else:
                # time = int(
                #     time_precision_scaler
                #     * math.hypot(
                #         (travel_times["xcord"][i] - travel_times["xcord"][j]),
                #         (travel_times["ycord"][i] - travel_times["ycord"][j]),
                #     )
                # )
                x_1 =travel_times["xcord"][i]
                x_2 =travel_times["xcord"][j]
                y_1 =travel_times["ycord"][i]
                y_2 =travel_times["ycord"][j]
                time =  int( time_precision_scaler * math.sqrt( pow((x_1 - x_2),2) + pow((y_1 - y_2),2 ) ) )

                time += travel_times["service_time"][j]
                time_vector.append(time)
        time_matrix.append(time_vector)
    data["time_matrix"] = time_matrix

    with open(problem_path) as f:
        lines = f.readlines()
    data["num_vehicles"] = int(re.findall("[0-9]+", lines[4])[0])
    data["vehicle_capacities"] = [int(re.findall("[0-9]+", lines[4])[1])] * data[
        "num_vehicles"
    ]
    data["demands"] = list(df.demand)

    windows = df[["ready_time", "due_date", "service_time"]].to_dict()
    time_windows = []
    for i in df.customer:
        time_windows.append(
            (
                windows["ready_time"][i] + windows["service_time"][i],
                windows["due_date"][i] + windows["service_time"][i],
            )
        )
    data["time_windows"] = time_windows

    return data
