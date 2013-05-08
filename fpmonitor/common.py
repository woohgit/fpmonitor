import os
import platform


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


def get_system():
    return platform.system()


def get_release():
    return platform.release()


def get_distribution():
    distribution = platform.linux_distribution()
    return "%s %s" % (distribution[0], distribution[2])


def get_memory_usage():
    return int(psutil.phymem_usage()[3])
