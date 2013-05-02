import os


def get_system_uptime_in_seconds():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return int(uptime_seconds)
    except:
        return 0


def get_system_load():
    try:
        loadavg = os.getloadavg()
    except:
        loadavg = (0, 0, 0)
    return loadavg
