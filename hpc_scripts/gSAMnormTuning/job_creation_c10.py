import os


def dict_creation(
    name: str,
    dir: str,
    opt: str,
    seed: int,
    lam: float,
    mem: str = "1G",
    dataset: str = "CIFAR10_cutout",
    model: str = "resnet18",
    rho: float = 0.1,
    t: float = 0.4,
    w: float = 1e-3,
    crt: str = "gSAMflat",
    crt_z: float = 1.0,
    z_2: float = 1.1,
    dataset_nn_combination: str = "cifar10_rn18_gSAM",
):
    d = {}
    d["name"] = name + "_" + str(seed)
    d["output_dir"] = dir
    d["memcpu"] = mem
    d["dataset"] = dataset
    d["model"] = model
    d["opt"] = opt
    d["rho"] = rho
    d["theta"] = t
    d["weight_decay"] = w
    d["crt"] = crt
    d["lam"] = lam
    d["z"] = crt_z
    d["z_two"] = z_2
    d["seed"] = seed
    d["dataset_nn_combination"] = dataset_nn_combination
    return d


seeds = [3107, 1234, 42, 87283, 913248]
crt_opts = ["vassoremu-sgd"]
crts = ["gSAMflat", "gSAMsharp", "gSAMratio"]
lambdas = [0.1, 0.2, 0.9]
zs = [1.1, 1.15, 1.2, 1.5]
zss = [1.1, 1.15, 1.2, 1.5, 1.6, 1.7, 1.8]


# Filling of experiment creation commands
def filling_out_experiment_commands() -> list:
    experiments = []

    for seed in seeds:
        for crt_opt in crt_opts:
            for crt in crts:
                for lam in lambdas:
                    if crt == "gSAMratio":
                        for z_1 in zss:
                            for z_2 in zss:
                                name = "{}_{}_l={}_z1={}_z2={}".format(
                                    crt_opt, crt, lam, z_1, z_2
                                )
                                experiments.append(
                                    dict_creation(
                                        name=name,
                                        dir=crt,
                                        opt=crt_opt,
                                        seed=seed,
                                        lam=lam,
                                        crt=crt,
                                        crt_z=z_1,
                                        z_2=z_2,
                                    )
                                )
                        continue
                    for z in zs:
                        name = "{}_{}_l={}_z1={}".format(crt_opt, crt, lam, z)
                        experiments.append(
                            dict_creation(
                                name=name,
                                dir=crt,
                                opt=crt_opt,
                                seed=seed,
                                lam=lam,
                                crt=crt,
                                crt_z=z,
                            )
                        )

    return experiments


slurm_template = """#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus=1
#SBATCH --time=10:00:00
#SBATCH --job-name={name}_c10_rn18
#SBATCH --mem-per-cpu={memcpu}
#SBATCH --output={output_dir}/outputs/{name}.out
#SBATCH --error={output_dir}/errors/{name}.err
#SBATCH --open-mode=truncate

module load eth_proxy
module load stack/2024-06
module load python_cuda/3.11.6
module load py-distro/1.8.0-4tnktx7

cd ~/sam/VaSSO

python3 train.py \
    --dataset {dataset} \
    --model {model} \
    --opt {opt} \
    --rho {rho} \
    --theta {theta} \
    --crt {crt} \
    --lam {lam} \
    --crt_z {z} \
    --z_two {z_two} \
    --seed {seed} \
    --dataset_nn_combination {dataset_nn_combination} \
"""

for experiment in filling_out_experiment_commands():
    script_content = slurm_template.format(**experiment)
    output_dir = experiment["output_dir"]
    os.makedirs(os.path.join(output_dir, "scripts"), exist_ok=True)
    script_filename = os.path.join(output_dir, "scripts", f"{experiment['name']}.sh")
    with open(script_filename, "w") as file:
        file.write(script_content)
