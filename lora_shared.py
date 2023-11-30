# lora_shared.py
def init():
    global update_j
    get_update_j = False
    global global_city
    global_city = "Roswell"

def set_update_j(value):
    update_j = value

# Function to update global_city
def set_global_city(city):
    global_city = city

    # Function to get the value of update_j
def get_update_j():
    return update_j

# Function to get the value of global_city
def get_global_city():
    return global_city
