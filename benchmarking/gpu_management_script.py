import pynvml
import os
import subprocess
import time
from multiprocessing import Process
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

    with open("gpu_doc_cosSim.info", "a") as f:
        f.write(f"Running script {script_path} on GPU {gpu_id}")
        subprocess.run(
            ["nohup", "python3", "../train.py"] + script_path.split(),
            env=env,
            stdout=f,
            stderr=f,
            preexec_fn=os.setpgrp,
        )


def worker(script_path):
    initialize_nvml()
    while True:
        gpu_id = get_free_gpu()
        if gpu_id is not None:
            run_script(script_path, gpu_id)
            break
        else:
            # print("No free GPU available, waiting...")
            time.sleep(1800)


def main(script_paths):
    processes = []
    for script_path in script_paths:
        p = Process(target=worker, args=(script_path,))
        p.start()
        processes.append(p)
        time.sleep(20)

    for p in processes:
        p.join()


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    script_commands = benchmarking_experiments()
    main(script_commands)
