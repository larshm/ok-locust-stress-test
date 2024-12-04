from lib.charging_station_simulator import *
from locust import task, run_single_user, events
from locust.runners import LocalRunner, MasterRunner, WorkerRunner

def seed_users(environment, msg, **_kwargs):
    charging_station_simulator.ChargingStations.extend(map(lambda u: u["name"], msg.data))
    print("Received charging station list: " + ", ".join(charging_station_simulator.ChargingStations))
    
@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not environment.runner is None and not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message("seed_users", seed_users)

@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    if environment.runner is None:
        environment.runner = environment.create_local_runner()
        environment.runner.target_user_count = 1
        
    if not isinstance(environment.runner, WorkerRunner):
        users = []
        for i in range(environment.runner.target_user_count):
            users.append({"name": f"LOCUST-CS-{i}"})

        worker_count = environment.runner.worker_count
        chunk_size = int(len(users) / worker_count)

        if isinstance(environment.runner, LocalRunner):
            workers = [environment.runner]
        else:
            workers = environment.runner.clients

        for i, worker in enumerate(workers):
            start_index = i * chunk_size

            if i + 1 < worker_count:
                end_index = start_index + chunk_size
            else:
                end_index = len(users)

            data = users[start_index:end_index]
            
            if isinstance(environment.runner, LocalRunner):
                charging_station_simulator.ChargingStations.extend(map(lambda u: u["name"], data))
            else:
                environment.runner.send_message("seed_users", data, worker)

if __name__ == "__main__":
    run_single_user(ChargingStationFlowTest)
    #ChargingStationFlowTest(environment="test").charging_station_connect()
