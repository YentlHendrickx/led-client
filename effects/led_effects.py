# Author: Yentl Hendrickx
# Last modified: 2024-06-04
# Description: Run LED effects


from threading import Thread
import multiprocessing
import neopixel
import board
import time

current_effect = None
current_color = (255, 0, 0)
parameters = {}

NUM_PIXELS = 180
LED_PIN = board.D18
pixels = [0] * NUM_PIXELS

class EffectsBase:
    def __init__(self, pixels, parameters={}):
        self.pixels = pixels
        self.parameters = parameters
        self.last_update_time = 0
        self.speed = int(parameters.get('animation speed', 100)) / 1000
        
    def ready_for_update(self):
        current_time = time.time()
        if current_time - self.last_update_time > self.speed:
            self.last_update_time = current_time
            return True
        return False
    
    def run(self):
        raise NotImplementedError("Subclasses must implement this method")
    
class SaticColorEffect(EffectsBase):
    def __init__(self, pixels, parameters={}, color=(255, 0, 0)):
        super().__init__(pixels, parameters)
        self.color = color
        self.previous_color = None
        
    def run(self):
        if self.color != self.previous_color:
            self.pixels.fill(self.color)
            self.pixels.show()
            self.previous_color = self.color

class ColorTrainEffect(EffectsBase):
    def __init__(self, pixels, parameters={}, color=(255, 0, 0)):
        super().__init__(pixels, parameters)
        self.color = color
        self.train_offset = 0
    
    def run(self):
        if self.ready_for_update():
            duty_cycle = float(self.parameters.get('train duty cycle', 0.5))

            num_pixels_on = int(len(self.pixels) * duty_cycle)
            new_pixels = [(0, 0, 0)] * len(self.pixels)
            
            for i in range(num_pixels_on):
                new_pixels[(i + self.train_offset) % len(self.pixels)] = self.color
            
            self.train_offset = (self.train_offset + 1) % len(self.pixels)
            
            for i, color in enumerate(new_pixels):
                self.pixels[i] = color
            
            self.pixels.show()

class RainbowEffect(EffectsBase):
    def __init__(self, pixels, parameters={}):
        super().__init__(pixels, parameters)
        self.initizalied = False

    def run(self):
        if not self.initizalied:
            for i in range(NUM_PIXELS):
                self.pixels[i] = wheel((i * 256 // NUM_PIXELS) & 255)
            self.pixels.show()
            self.initizalied = True
        
class MovingRainbowEffect(EffectsBase):
    def __init__(self, pixels, parameters={}):
        super().__init__(pixels, parameters)
        self.initizalied = False
        self.rainbow_offset = 0

    def run(self):
        if not self.initizalied:
            for i in range(NUM_PIXELS):
                self.pixels[i] = wheel(((i + self.rainbow_offset) * 256 // NUM_PIXELS) & 255)
            self.pixels.show()
            self.initizalied = True
        
        if self.ready_for_update():
            self.rainbow_offset = (self.rainbow_offset + 1) % NUM_PIXELS
            for i in range(NUM_PIXELS):
                self.pixels[i] = wheel(((i + self.rainbow_offset) * 256 // NUM_PIXELS) & 255)
            self.pixels.show()
    


def setup_strip():
    global pixels
    pixels = neopixel.NeoPixel(LED_PIN, NUM_PIXELS, auto_write=False)

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

def handle_data(data):
    global parameters
    
    try:
        print(data)
        effect_name = str.lower(data["effect_name"])
        color_name = data["color_name"]
        
        if color_name == "EFFECT":
            color = (0, 0, 0)
        else:
            color = data["color_value"].split(",")
            color = (int(color[0]), int(color[1]), int(color[2]))
        
        parameters = {k: v for k, v in (param.split(":") for param in data["parameters"].split(","))}
        
        effect_classes = {
            'rainbow': RainbowEffect,
            'moving rainbow': MovingRainbowEffect,
            'static color': SaticColorEffect,
            'color train': ColorTrainEffect
        }
        
        if effect_name in effect_classes:
            if color_name == "EFFECT":
                effect = effect_classes[effect_name](pixels, parameters)
            else:
                effect = effect_classes[effect_name](pixels, parameters, color)
            return effect
    except Exception as e:
        # If keyboardinterrupt, rethrow
        if isinstance(e, KeyboardInterrupt):
            raise e
        print("Error parsing data:", data, "\nError:", e)
    
    return None

def effects_worker(queue, termination_event):
    setup_strip()
    current_effect = None

    while not termination_event.is_set():
        if not queue.empty():
            data = queue.get()
            effect = handle_data(data[0])
            if effect:
                current_effect = effect
        
        if current_effect:
            current_effect.run()

def start_effects(queue, termination_event):
    thread = Thread(target=effects_worker, args=(queue, termination_event,))
    thread.start()

    while not termination_event.is_set():
        #time.sleep(0.1)  # add a small delay to reduce CPU usage
        pass

    thread.join()  # wait for the effects_worker thread to finish
