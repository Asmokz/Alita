import psutil
import GPUtil
import pynvml

def get_system_status():
    """
    Récupère CPU, RAM, GPU, Réseau + Températures
    Retourne une phrase adaptée pour TTS.
    """

    # --- CPU ---
    cpu = psutil.cpu_percent(interval=1)

    # --- RAM ---
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_used = round(ram.used / (1024**3), 1)
    ram_total = round(ram.total / (1024**3), 1)

    # --- Température CPU ---
    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:  # Linux/Windows certaines CM
            cpu_temp = round(temps["coretemp"][0].current, 1)
        elif "cpu-thermal" in temps:  # Autres cas
            cpu_temp = round(temps["cpu-thermal"][0].current, 1)
    except Exception:
        pass

    # --- GPU NVIDIA via NVML ---
    gpu_status = []
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
            load = round(pynvml.nvmlDeviceGetUtilizationRates(handle).gpu, 1)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_used = round(mem_info.used / (1024**2), 1)
            mem_total = round(mem_info.total / (1024**2), 1)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            gpu_status.append(
                f"GPU {i} {name}: {load}% utilisé, mémoire du GPU {mem_used} sur {mem_total} Mo, température {temp}°C"
            )

        pynvml.nvmlShutdown()
    except Exception:
        gpu_status.append("Impossible de lire les infos GPU.")

    # --- Réseau ---
    net_io = psutil.net_io_counters()
    sent_mb = round(net_io.bytes_sent / (1024*1024), 1)
    recv_mb = round(net_io.bytes_recv / (1024*1024), 1)

    # --- Résumé ---
    resume = (
        f"CPU utilisé à {cpu}%. "
        f"Mémoire {ram_used} sur {ram_total} giga, soit {ram_percent}%. "
    )

    if cpu_temp:
        resume += f"Température CPU {cpu_temp} degrés. "

    if gpu_status:
        resume += " | ".join(gpu_status) + ". "

    resume += (
        f"Réseau : {recv_mb} mégaoctets reçus, "
        f"{sent_mb} mégaoctets envoyés."
    )

    return resume
