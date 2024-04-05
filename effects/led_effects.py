# Author: Yentl Hendrickx
# Last modified: 2023-07-09
# Description: Run LED effects

import time
import multiprocessing
from threading import Thread

def handle_data(data):
    print(data)

events_emitted = 12
def run_effect():
    global events_emitted
    if events_emitted >= 10:
        print("\nRunning Effect", end='', flush=True)
        events_emitted = 0
    else:
        print(".", end='', flush=True)
        events_emitted += 1
    time.sleep(0.5)

def effects_worker(queue, termination_event):
    while not termination_event.is_set():
        if not queue.empty():
            data = queue.get()
            handle_data(data)
        
        run_effect()

def start_effects(queue, termination_event):
    thread = Thread(target=effects_worker, args=(queue, termination_event,))
    print("\nRunning Effect", end='', flush=True)
    thread.start()

    while not termination_event.is_set():
        time.sleep(0.1)  # add a small delay to reduce CPU usage

    thread.join()  # wait for the effects_worker thread to finish
