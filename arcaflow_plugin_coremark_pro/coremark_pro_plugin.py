#!/usr/bin/env python3

import subprocess
import sys
import re
import typing
from math import ceil
from arcaflow_plugin_sdk import plugin
from coremark_pro_schema import (
    TuneIterationsInput,
    CertifyAllInput,
    iterationsSchema,
    certifyAllResultSchema,
    SuccessOutput,
    ErrorOutput,
)


def run_oneshot_cmd(command_list, workdir) -> str:
    try:
        cmd_out = subprocess.check_output(
            command_list,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=workdir,
        )
    except subprocess.CalledProcessError as error:
        return "error", ErrorOutput(
            f"{error.cmd[0]} failed with return code "
            f"{error.returncode}:\n{error.output}"
        )
    return "completed", cmd_out


run_log_path = "/root/coremark-pro/builds/linux64/gcc64/logs/linux64.gcc64.log"


@plugin.step(
    id="tune-iterations",
    name="Tune Iterations",
    description=(
        "Runs all of the nine tests, checks their run times, calculates the number of "
        "iterations for each test to roughly reach the 'target_runtime', and returns "
        "an object compatible with the 'certify-all' step. NOTE -- If you are going to "
        "pass the output of the 'tune-iterations' step to the 'certify-all' step in a "
        "workflow, you should include in the input to this step all of the parameters "
        "for the 'certify-all' step so that the output object generated is complete."
    ),
    outputs={"success": CertifyAllInput, "error": ErrorOutput},
)
def tune_iterations(
    params: TuneIterationsInput,
) -> typing.Tuple[str, typing.Union[CertifyAllInput, ErrorOutput]]:

    # Run the basic certify-all to generate logs
    certify_all(params=CertifyAllInput(verify=True), run_id="tune-iterations")

    benchmark_iterations = {}

    # Get the median time for each benchmark and calculate the target iterations
    with open(file=run_log_path, encoding="utf-8") as file:
        for log in file:
            if "median single" in log:
                log_list = log.split()
                log_name = log_list[2]
                benchmark_iterations[log_name] = ceil(
                    params.target_run_time / float(log_list[6])
                )

    return "success", CertifyAllInput(
        contexts=params.contexts,
        workers=params.workers,
        verify=params.verify,
        iterations=iterationsSchema.unserialize(benchmark_iterations),
    )


@plugin.step(
    id="certify-all",
    name="Certify All",
    description=(
        "Runs all of the nine tests, collects their output scores, and processes them "
        "to generate the final CoreMark-PRO score"
    ),
    outputs={"success": SuccessOutput, "error": ErrorOutput},
)
def certify_all(
    params: CertifyAllInput,
) -> typing.Tuple[str, typing.Union[SuccessOutput, ErrorOutput]]:

    # Modify individual benchmark iterations if they were provided
    if params.iterations:
        target_iterations = iterationsSchema.serialize(params.iterations)
        for benchmark, iterations in target_iterations.items():
            with open(
                file=f"/root/coremark-pro/workloads/{benchmark}/{benchmark}.opt",
                mode="r+",
                encoding="utf-8",
            ) as file:
                opt_output = ""
                for line in file:
                    if "WLD_CMD_FLAGS" in line:
                        opt_output += f"override WLD_CMD_FLAGS=-i{iterations}\n"
                    else:
                        opt_output += line
                file.write(opt_output)

    # Prepare the certify-all command
    ca_cmd = [
        "make",
        "-s",
        "certify-all",
    ]

    xcmd = ["-v1" if params.verify else "-v0"]
    if params.contexts:
        xcmd.append(f"-c{params.contexts}")
    if params.workers:
        xcmd.append(f"-w{params.workers}")
    # The coremark `make` command passes parameters to the individual benchmarks via
    # the sub-parameters provided to the XCMD variable
    ca_cmd.append(f"XCMD={' '.join(xcmd)}")

    # Run certify-all
    ca_return = run_oneshot_cmd(ca_cmd, "/root/coremark-pro")

    if ca_return[0] == "error":
        return ca_return

    ca_results = {
        "cjpeg-rose7-preset": {},
        "core": {},
        "linear_alg-mid-100x100-sp": {},
        "loops-all-mid-10k-sp": {},
        "nnet_test": {},
        "parser-125k": {},
        "radix2-big-64k": {},
        "sha-test": {},
        "zip-test": {},
        "CoreMark-PRO": {},
    }

    # Construct the output object
    exclusion_search = re.compile(r"^(\s+|Starting|Workload|-|Mark)", re.IGNORECASE)
    for line in ca_return[1].splitlines():
        if exclusion_search.match(line):
            continue
        line_list = line.split()
        try:
            line_name = line_list[0]
        except IndexError:
            continue
        if line_name in ca_results:
            ca_results[line_name] = {
                "MultiCore": float(line_list[1]),
                "SingleCore": float(line_list[2]),
                "Scaling": float(line_list[3]),
            }

    # Collect the per-benchmark iterations from the log file
    with open(file=run_log_path, encoding="utf-8") as file:
        for log in file:
            if "median single" not in log or "CoreMark-PRO" in log:
                continue
            log_list = log.split()
            log_name = log_list[2]
            if log_name in ca_results:
                ca_results[log_name]["Iterations"] = int(log_list[7])

    return "success", SuccessOutput(
        coremark_pro_command=" ".join(ca_cmd),
        coremark_pro_params=params,
        coremark_pro_results=certifyAllResultSchema.unserialize(ca_results),
    )


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                tune_iterations,
                certify_all,
            )
        )
    )
