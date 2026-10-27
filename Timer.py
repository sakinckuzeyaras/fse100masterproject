import time 
# Timer for a smart gloves 
last_reading_time =None 
def start_timer():
  global last_reading_time
  last_reading_time =time.monotonic()
def get_elapsed_time():
    global last_reading_time
    current_time= time.monotonic()
  if last_reading_time is None:
     last_reading_time= current_time
     return 0.0
    elapsed= current_time - last_reading_time
    last_reading_time= current_time
    return round(elapsed, 2)
