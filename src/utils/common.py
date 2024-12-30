import os

def get_env_int(var_name, default):
    value = os.getenv(var_name)
    return int(value) if value else default
