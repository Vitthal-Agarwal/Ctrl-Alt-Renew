# scripts/simulation.py

import datetime
import threading
import time

# Use a dictionary to track computation status and intensity
computation_status = {'running': False, 'intensity': None}

def mock_computation_task(intensity):
    while computation_status['running']:
        # Simulate computation work
        print(f"Computation ({intensity}) running at {datetime.datetime.now()}")
        # Simulate different workloads based on intensity
        if intensity == 'HIGH':
            time.sleep(1)  # Simulate high workload
        elif intensity == 'MEDIUM':
            time.sleep(2)  # Simulate medium workload
        elif intensity == 'LOW':
            time.sleep(3)  # Simulate low workload
        else:
            time.sleep(4)  # Default case
    print("Computation task ended.")

def start_high_intensity_computation():
    if not computation_status['running']:
        computation_status['running'] = True
        computation_status['intensity'] = 'HIGH'
        print(f"High-intensity computation started at {datetime.datetime.now()}")
        # Start a mock computation task
        computation_thread = threading.Thread(target=mock_computation_task, args=('HIGH',))
        computation_thread.start()
    else:
        print("Computation is already running.")

def start_medium_intensity_computation():
    if not computation_status['running']:
        computation_status['running'] = True
        computation_status['intensity'] = 'MEDIUM'
        print(f"Medium-intensity computation started at {datetime.datetime.now()}")
        # Start a mock computation task
        computation_thread = threading.Thread(target=mock_computation_task, args=('MEDIUM',))
        computation_thread.start()
    else:
        print("Computation is already running.")

def start_low_intensity_computation():
    if not computation_status['running']:
        computation_status['running'] = True
        computation_status['intensity'] = 'LOW'
        print(f"Low-intensity computation started at {datetime.datetime.now()}")
        # Start a mock computation task
        computation_thread = threading.Thread(target=mock_computation_task, args=('LOW',))
        computation_thread.start()
    else:
        print("Computation is already running.")

def stop_computation():
    if computation_status['running']:
        computation_status['running'] = False
        print(f"Computation stopped at {datetime.datetime.now()}")
    else:
        print("No computation is running.")
