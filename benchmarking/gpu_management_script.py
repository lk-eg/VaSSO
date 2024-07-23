import pynvml
import os
import subprocess
import time
from multiprocessing import Process, Queue
from job_creation_benchmarking import benchmarking_experiments


def initialize_nvml():
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError as err:
        print(f"Failed to initialize NVML: {err}")
        raise


def get_free_gpu():
    try:
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu_utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

            if (
                len(processes) == 0
                and gpu_utilization.gpu == 0
                and gpu_utilization.memory == 0
            ):
                return i
    except pynvml.NVMLError as err:
        print(f"Failed to get free GPU: {err}")
        raise
    return None


def run_script(script_path, gpu_id):
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    print(f"Running script {script_path} on GPU {gpu_id}")
    subprocess.run(["python3", "../train.py", *script_path.split()], env=env)


def worker(queue):
    initialize_nvml()
    while True:
        script_path = queue.get()
        if script_path is None:
            break
        while True:
            gpu_id = get_free_gpu()
            if gpu_id is not None:
                run_script(script_path, gpu_id)
                break
            else:
                print("No free GPU available, waiting...")
                time.sleep(900)


def main(script_paths):
    queue = Queue()
    for script_path in script_paths:
        queue.put(script_path)

    process = Process(target=worker, args=(queue,))
    process.start()
    process.join()
    queue.put(None)


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    script_commands = benchmarking_experiments()
    main(script_commands)
