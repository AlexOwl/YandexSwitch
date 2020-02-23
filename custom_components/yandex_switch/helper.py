import threading
import json
from itertools import islice

def create_task(target, daemon=True):
    task = threading.Thread(target=target)
    task.setDaemon(daemon)
    task.start()
    return task

def proccess_reply(reply):
    try:
        return json.loads(reply)
    except:
        return reply

def dps_to_value(schema, dps):
    schema_dict = schema_to_dict(schema)

    def value_convert(dp, value):
        property = schema_dict[int(dp)]
        info = property.get("property", {})
        if info.get("type") == "value":
            value /= 10 ** info.get("scale", 0)

        return value

    return { schema_dict[int(dp)]["code"]: value_convert(dp, value) for dp, value in dps.items() if int(dp) in schema_dict and "code" in schema_dict[int(dp)] }

def find_switch_dp(schema):
    for property in schema:
        if "switch" in property.get("code", ""):
            return str(property.get("id"))

def generate_set_control(schema, data):
    schema_dict = schema_to_dict(schema)
    return { str(dp): value for dp, value in data.items() if int(dp) in schema_dict and "w" in schema_dict[int(dp)].get("mode", "") }

def generate_get_control(schema):
    return { property["id"]: None for property in schema if "id" in property and "r" in property.get("mode", "") }

def schema_to_dict(schema):
    return { property["id"]: property for property in schema if "id" in property }

def chunks_dict(data, size):
    it = iter(data)
    for _ in range(0, len(data), size):
        yield { k:data[k] for k in islice(it, size) }