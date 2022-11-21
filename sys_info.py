import cpuinfo
import platform
import discord
import psutil

cpu = cpuinfo.get_cpu_info()

cpu_model = cpu['brand_raw']
cpu_speed = cpu['hz_actual_friendly']
thread_count = cpu['count']
arch = cpu['arch']
os = platform.system()
ver = platform.python_version()
discord_py = discord.__version__
cpu_usage = (f"{(psutil.cpu_percent())} %")
mem_total = (f"{(psutil.virtual_memory().total)/1.064e+9:.2f} GB")
mem_used = (f"{(psutil.virtual_memory().used)/1.064e+9:.2f} GB")
mem_usage = (f"{(psutil.virtual_memory().percent)} %")