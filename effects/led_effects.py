# Author: Yentl Hendrickx
# Last modified: 2024-06-04
# Description: Run LED effects


from threading import Thread
import multiprocessing
import time

# TODO: Add more effects, make more manageballe (maybe each effect should be a class with a run method?)
import neopixel
import board

current_effect = None
current_color = (255, 0, 0)
parameters = {}

NUM_PIXELS = 180
LED_PIN = board.D18
pixels = [0] * NUM_PIXELS

def setup_strip():
    global pixels
    pixels = neopixel.NeoPixel(LED_PIN, NUM_PIXELS, auto_write=False)

train_offset = 0
previous_time = time.time()
def color_train():
    global pixels, parameters, train_offset, previous_time, train_offset, NUM_PIXELS, current_color
    color = current_color
    # Get animation speed and duty cycle parameters
    speed = int(parameters.get('animation speed', 50))
    duty_cycle = float(parameters.get('train duty cycle', 0.5))


    if time.time() - previous_time < speed / 1000:
        return
    
    previous_time = time.time()
    # Calculate the number of pixels that should be on
    num_pixels_on = int(NUM_PIXELS * duty_cycle)
    pixels.fill((0, 0, 0))
    
    # Now we need to fill in the pixels that should be on
    for i in range(num_pixels_on):
        pixels[(i + train_offset) % NUM_PIXELS] = color
    
    train_offset = (train_offset + 1) % NUM_PIXELS
    pixels.show()
    

def static_color(color):
    global pixels
    pixels.fill(color)
    pixels.show()

def wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    elif pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow():
    global pixels
    for i in range(NUM_PIXELS):
        pixels[i] = wheel((i * 256 // NUM_PIXELS) & 255)

def run_effect():
    global current_color, current_effect
    
    if current_effect == 'rainbow':
        rainbow()
    elif current_effect == 'static color':
        static_color(current_color)
    elif current_effect == 'color train':
        color_train()
    # elif current_effect == 'colorwipe':
    #     colorwipe()
    # elif current_effect == 'theaterchase':
    #     theaterchase()
    

def handle_data(data):
    global current_effect, current_color, parameters
    
    try:
        print(data)
        data = data[0]
        current_effect = str.lower(data["effect_name"]) or current_effect
        color = data["color_value"]
        
        # Color has to be in the format (r, g, b), currentl is RRR,GGG,BBB,A
        color = color.split(",")
        current_color = (int(color[0]), int(color[1]), int(color[2]))
        
        for parameter in (data["parameters"].split(",")):
            key, value = parameter.split(":")
            parameters[str.lower(key.strip())] = value.strip()
    except:
        print("Error parsing data:", data)

def effects_worker(queue, termination_event):
    setup_strip()
    while not termination_event.is_set():
        if not queue.empty():
            data = queue.get()
            handle_data(data)
        
        run_effect()

def start_effects(queue, termination_event):
    thread = Thread(target=effects_worker, args=(queue, termination_event,))
    thread.start()

    while not termination_event.is_set():
        #time.sleep(0.1)  # add a small delay to reduce CPU usage
        pass

    print("STOPPING!")
    thread.join()  # wait for the effects_worker thread to finish
