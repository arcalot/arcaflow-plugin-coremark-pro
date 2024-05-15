#!/usr/bin/env python3

import subprocess
import sys
import typing
from arcaflow_plugin_sdk import plugin
from coremark_pro_schema import (
    CertifyAllParams,
    certifyAllResultSchema,
    SuccessOutput,
    ErrorOutput,
)


def run_oneshot_cmd(command_list, workdir) -> str:
    try:
        cmd_out = subprocess.check_output(
            command_list,
            stderr=subprocess.PIPE,
            text=True,
            cwd=workdir
        )
    except subprocess.CalledProcessError as error:
        return "error", ErrorOutput(
            f"{error.cmd[0]} failed with return code "
            f"{error.returncode}:\n{error.output}"
        )
    return "completed", cmd_out


@plugin.step(
    id="certify-all",
    name="certify-all",
    description=(
        "Runs all of the nine tests, collects their output scores, and processes them "
        "to generate the final CoreMark-PRO score"
    ),
    outputs={"success": SuccessOutput, "error": ErrorOutput},
)
def certify_all(
    params: CertifyAllParams,
) -> typing.Tuple[str, typing.Union[SuccessOutput, ErrorOutput]]:

    ca_cmd = [
        "make",
        "-s",
        "certify-all",
        f"XCMD='-c{params.contexts} -w{params.workers}'",
    ]

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
        try:
            line_name = line.split()[0]
        except IndexError:
            pass
        if line_name in ca_results and len(line.split()) > 1:
            ca_results[line_name] = {
                "MultiCore": line.split()[1],
                "SingleCore": line.split()[2],
                "Scaling": line.split()[3]
            }

    return "success", SuccessOutput(
        coremark_pro_params=params,
        coremark_pro_results=certifyAllResultSchema.unserialize(ca_results),
    )


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                certify_all,
            )
        )
    )
