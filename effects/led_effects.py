import time
import multiprocessing
from threading import Thread

def handle_data(data):
    print("Handling Data!" + data)

def run_effect():
    print("Running Effect!")
    time.sleep(1)

def effects_worker(queue, termination_event):
    while not termination_event.is_set():
        if not queue.empty():
            data = queue.get()
            handle_data(data)
        
        run_effect()

def start_effects(queue, termination_event):
    thread = Thread(target=effects_worker, args=(queue, termination_event,))
    thread.start()

    while not termination_event.is_set():
        try:
            time.sleep(0.1)  # add a small delay to reduce CPU usage
        except KeyboardInterrupt:
            termination_event.set()

    thread.join()  # wait for the effects_worker thread to finish
