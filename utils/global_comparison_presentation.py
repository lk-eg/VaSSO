import pandas as pd


# Write global comparison file
def comp_file_logging(
    args,
    max_acc,
    train_acc1,
    test_loss,
    train_loss,
    overhead,
    used_training,
    optimiser_overhead_calculation,
):
    comp_file_name = "comp_" + args.dataset_nn_combination + ".info"
    with open(comp_file_name, "a") as f:
        opt = args.opt.split("-")[0]
        f.write(f"OPTIMISER: {opt} - theta = {args.theta} \n")
        if optimiser_overhead_calculation:
            reuse_method = args.crt
            f.write(f"Reuse method: {reuse_method}")
            if reuse_method == "naive":
                f.write(f" - k={args.crt_k} \n")
            elif reuse_method == "random":
                f.write(f" - p={args.crt_p} \n")
            elif reuse_method[:11] == "gSAMNormEMA":
                f.write(f" - zeta={args.zeta} \n")
        f.write(
            f"Max Test Accuracy: {max_acc:.4f}, Last Train Accuracy: {train_acc1:.4f}, Difference (Train Accuracy - Test Accuracy) = {train_acc1 - max_acc:.4f} \n"
        )
        f.write(
            f"Last Test Loss: {test_loss:.4f}, Last Train Loss: {train_loss:.4f}, Difference (test loss - train loss) = {test_loss - train_loss:.4f} \n"
        )
        if optimiser_overhead_calculation:
            f.write(f"More calculations x SGD: {overhead:.4f} \n")
        f.write(f"Training Time: {used_training} \n")
        f.write("\n")


# save into a csv file
def training_result_save(args, top_1_test_acc, overhead_over_sgd):
    results = []
    exp_res = {
        "optimizer": args.opt,
        "top-1 test acc": top_1_test_acc,
        "overhead": overhead_over_sgd,
    }
    if args.crt != "none":
        exp_res["criterion"] = args.crt
        epx_res[]
    results.append(
        {
            "optimizer": args.opt,
            "configuration": "default",
            "top-1 test acc": top_1_test_acc,
            "overhead": overhead_over_sgd,
        }
    )
    df = pd.DataFrame(results)
    numerical_results_csv_fp = args.dataset_nn_combination + "_results.csv"
    try:
        with open(numerical_results_csv_fp, "r") as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    df.to_csv(
        numerical_results_csv_fp,
        mode="a" if file_exists else "w",
        header=not file_exists,
        index=False,
    )


# Needs WandB plotting as well (Runtime - Test Accuracy Plots).


# automatically generate LaTeX Table as well from the results:
