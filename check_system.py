"""Checks your computer and suggests an Ollama model that should run well on it.

Run:  python check_system.py
"""
import os
import platform
import shutil
import subprocess

# (minimum RAM in GB, model name, approximate download size in GB, comment)
TIERS = [
    (0,  "qwen2.5:1.5b", 1.0,  "Very small. Fast, but the writing quality is weak."),
    (6,  "qwen2.5:3b",   1.9,  "Small. This is the default of the project."),
    (12, "qwen2.5:7b",   4.7,  "Medium. Noticeably better writing and structure."),
    (24, "qwen2.5:14b",  9.0,  "Large. Needs a strong machine, much slower on CPU only."),
    (48, "qwen2.5:32b",  20.0, "Very large. Best quality here, needs a workstation or big GPU."),
]


def total_ram_gb():
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes

            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            s = MemStatus()
            s.dwLength = ctypes.sizeof(s)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
            return s.ullTotalPhys / 1024 ** 3
        if system == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(out.strip()) / 1024 ** 3
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    return int(line.split()[1]) / 1024 ** 2
    except Exception:
        pass
    return None


def nvidia_gpu():
    """Returns (name, vram_gb) for the first NVIDIA GPU, or None."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            text=True, timeout=10)
        name, mem = out.strip().splitlines()[0].rsplit(",", 1)
        return name.strip(), int(mem) / 1024
    except Exception:
        return None


def installed_models():
    if not shutil.which("ollama"):
        return None
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=15)
        return [l.split()[0] for l in out.strip().splitlines()[1:] if l.strip()]
    except Exception:
        return []


def pick(gb):
    chosen = TIERS[0]
    for tier in TIERS:
        if gb >= tier[0]:
            chosen = tier
    return chosen


def main():
    ram = total_ram_gb()
    gpu = nvidia_gpu()
    models = installed_models()

    print("Your system")
    print("-----------")
    print(f"OS        : {platform.system()} {platform.release()}")
    print(f"CPU cores : {os.cpu_count()}")
    print(f"RAM       : {ram:.1f} GB" if ram else "RAM       : could not detect")
    print(f"GPU       : {gpu[0]} ({gpu[1]:.1f} GB VRAM)" if gpu else "GPU       : no NVIDIA GPU detected (the model will run on the CPU)")
    print()

    if models is None:
        print("Ollama was not found. Install it from https://ollama.com first, then run this again.\n")
    elif models:
        print("Models you already have: " + ", ".join(models) + "\n")

    if not ram:
        print("Could not read your RAM. Check it manually and use the table in the README.")
        return

    name, size, note = pick(ram)[1:]
    print("Recommended model")
    print("-----------------")
    print(f"{name}  (download about {size:g} GB)")
    print(note)
    if gpu:
        gpu_name = pick(gpu[1] * 2)[1]  # the RAM tiers leave about half the memory free, so double the VRAM to compare
        if gpu_name != name:
            print(f"Note: your GPU memory fits about {gpu_name} fully. Anything larger will spill into system RAM and run slower.")
    print()
    print("To use it")
    print("---------")
    print(f"  ollama pull {name}")
    print(f'  python test_run.py "Create a project report for an attendance system" --model {name}')
    print()
    print("Tip: leave a few GB of RAM free for Windows and your other programs.")


if __name__ == "__main__":
    main()
