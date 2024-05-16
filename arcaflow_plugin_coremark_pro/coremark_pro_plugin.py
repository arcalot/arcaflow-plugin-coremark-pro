#!/usr/bin/env python3

import subprocess
import sys
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
            command_list, stderr=subprocess.STDOUT, text=True, cwd=workdir
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
        "Runs all of the nine tests, checks their run times, calculates the numer of "
        "iterations for each test to rougly reach the 'target_runtime', and returns "
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

    # Run the basic certify-all
    certify_all(params=CertifyAllInput(verify=True), run_id="tune-iterations")

    benchmark_iterations = {}

    # Get the median time for each benchmark and calculate the target iterations
    with open(file=run_log_path, encoding="utf-8") as file:
        for line in file:
            if "median single" in line:
                line_list = line.split()
                benchmark_iterations[line_list[2]] = ceil(
                    params.target_run_time / float(line_list[6])
                )

    return "success", CertifyAllInput(
        contexts = params.contexts,
        workers = params.workers,
        verify = params.verify,
        iterations = iterationsSchema.unserialize(benchmark_iterations),
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

    ca_cmd = [
        "make",
        "-s",
        "certify-all",
        "XCMD='",
    ]

    if params.verify:
        ca_cmd[-1] += "-v1 "
    else:
        ca_cmd[-1] += "-v0 "

    if params.contexts:
        ca_cmd[-1] += f"-c{params.contexts}"

    if params.workers:
        ca_cmd[-1] += f"-w{params.workers}"

    ca_cmd[-1] += "'"

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

    for line in ca_return[1].splitlines():
        line_list = line.split()
        try:
            line_name = line_list[0]
        except IndexError:
            pass
        if line_name in ca_results and len(line_list) > 1:
            ca_results[line_name] = {
                "MultiCore": line_list[1],
                "SingleCore": line_list[2],
                "Scaling": line_list[3],
            }
            if line_name != "CoreMark-PRO":
                with open(file=run_log_path, encoding="utf-8") as file:
                    for line in file:
                        line_list = line.split()
                        if "median single" in line and line_list[2] == line_name:
                            ca_results[line_name]["Iterations"] = int(
                                line_list[7]
                            )

    return "success", SuccessOutput(
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
