import typing
from dataclasses import dataclass
from arcaflow_plugin_sdk import schema, plugin


@dataclass
class CertifyAllParams:
    contexts: typing.Annotated[
        typing.Optional[int],
        schema.name("Contexts"),
        schema.description("Number of contexts per benchmark"),
    ] = None
    workers: typing.Annotated[
        typing.Optional[int],
        schema.name("Workers"),
        schema.description("Number of workers per benchmark"),
    ] = None
    verify: typing.Annotated[
        typing.Optional[bool],
        schema.name("Verify"),
        schema.description("Enable benchmark validation runs"),
    ] = False


@dataclass
class TuneIterationsInput(CertifyAllParams):
    target_run_time: typing.Annotated[
        typing.Optional[int],
        schema.name("Target Run Time Seconds"),
        schema.description("Target run time in seconds for each benchmark"),
    ] = 10


@dataclass
class Iterations:
    cjpeg_rose7_preset: typing.Annotated[
        typing.Optional[int],
        schema.id("cjpeg-rose7-preset"),
        schema.name("cjpeg-rose7-preset iterations"),
        schema.description("Iterations for cjpeg-rose7-preset benchmark"),
    ] = None
    core: typing.Annotated[
        typing.Optional[int],
        schema.name("core iterations"),
        schema.description("Iterations for core benchmark"),
    ] = None
    linear_alg_mid_100x100_sp: typing.Annotated[
        typing.Optional[int],
        schema.id("linear_alg-mid-100x100-sp"),
        schema.name("linear_alg-mid-100x100-sp iterations"),
        schema.description("Iterations for linear_alg-mid-100x100-sp benchmark"),
    ] = None
    loops_all_mid_10k_sp: typing.Annotated[
        typing.Optional[int],
        schema.id("loops-all-mid-10k-sp"),
        schema.name("loops-all-mid-10k-sp iterations"),
        schema.description("Iterations for loops-all-mid-10k-sp benchmark"),
    ] = None
    nnet_test: typing.Annotated[
        typing.Optional[int],
        schema.name("nnet_test iterations"),
        schema.description("Iterations for nnet_test benchmark"),
    ] = None
    parser_125k: typing.Annotated[
        typing.Optional[int],
        schema.id("parser-125k"),
        schema.name("parser-125k iterations"),
        schema.description("Iterations for parser-125k benchmark"),
    ] = None
    radix2_big_64k: typing.Annotated[
        typing.Optional[int],
        schema.id("radix2-big-64k"),
        schema.name("radix2-big-64k iterations"),
        schema.description("Iterations for radix2-big-64k benchmark"),
    ] = None
    sha_test: typing.Annotated[
        typing.Optional[int],
        schema.id("sha-test"),
        schema.name("sha-test iterations"),
        schema.description("Iterations for sha-test benchmark"),
    ] = None
    zip_test: typing.Annotated[
        typing.Optional[int],
        schema.id("zip-test"),
        schema.name("zip-test iterations"),
        schema.description("Iterations for zip-test benchmark"),
    ] = None


iterationsSchema = plugin.build_object_schema(Iterations)


@dataclass
class CertifyAllInput(CertifyAllParams):
    """Class simply merges the other input classes"""

    iterations: typing.Annotated[
        typing.Optional[Iterations],
        schema.name("Benchmark Iterations"),
        schema.description("Number of iterations for each benchmark"),
    ] = None


@dataclass
class CertifyAllItem:
    multi_core: typing.Annotated[
        float,
        schema.id("MultiCore"),
        schema.name("MultiCore"),
        schema.description("Benchmark result - Multi-Core (iter/s)"),
    ]
    single_core: typing.Annotated[
        float,
        schema.id("SingleCore"),
        schema.name("SingleCore"),
        schema.description("Benchmark result - Single-Core (iter/s)"),
    ]
    scaling: typing.Annotated[
        float,
        schema.id("Scaling"),
        schema.name("Scaling"),
        schema.description("Benchmark result - Scaling"),
    ]
    iterations: typing.Annotated[
        typing.Optional[int],
        schema.id("Iterations"),
        schema.name("Iterations"),
        schema.description("Number of benchmark iterations"),
    ] = None


@dataclass
class CertifyAllResult:
    cjpeg_rose7_preset: typing.Annotated[
        CertifyAllItem,
        schema.id("cjpeg-rose7-preset"),
        schema.name("cjpeg-rose7-preset"),
        schema.description("cjpeg-rose7-preset benchmark results"),
    ]
    core: typing.Annotated[
        CertifyAllItem,
        schema.id("core"),
        schema.name("core"),
        schema.description("core benchmark results"),
    ]
    linear_alg_mid_100x100_sp: typing.Annotated[
        CertifyAllItem,
        schema.id("linear_alg-mid-100x100-sp"),
        schema.name("linear_alg-mid-100x100-sp"),
        schema.description("linear_alg-mid-100x100-sp benchmark results"),
    ]
    loops_all_mid_10k_sp: typing.Annotated[
        CertifyAllItem,
        schema.id("loops-all-mid-10k-sp"),
        schema.name("loops-all-mid-10k-sp"),
        schema.description("loops-all-mid-10k-sp benchmark results"),
    ]
    nnet_test: typing.Annotated[
        CertifyAllItem,
        schema.name("nnet_test"),
        schema.description("nnet_test benchmark results"),
    ]
    parser_125k: typing.Annotated[
        CertifyAllItem,
        schema.id("parser-125k"),
        schema.name("parser-125k"),
        schema.description("parser-125k benchmark results"),
    ]
    radix2_big_64k: typing.Annotated[
        CertifyAllItem,
        schema.id("radix2-big-64k"),
        schema.name("radix2-big-64k"),
        schema.description("radix2-big-64k benchmark results"),
    ]
    sha_test: typing.Annotated[
        CertifyAllItem,
        schema.id("sha-test"),
        schema.name("sha-test"),
        schema.description("sha-test benchmark results"),
    ]
    zip_test: typing.Annotated[
        CertifyAllItem,
        schema.id("zip-test"),
        schema.name("zip-test"),
        schema.description("zip-test benchmark results"),
    ]
    coremark_pro: typing.Annotated[
        CertifyAllItem,
        schema.id("CoreMark-PRO"),
        schema.name("CoreMark-PRO"),
        schema.description("CoreMark-PRO benchmark results"),
    ]


certifyAllResultSchema = plugin.build_object_schema(CertifyAllResult)


@dataclass
class SuccessOutput:
    coremark_pro_params: typing.Annotated[
        CertifyAllParams,
        schema.name("Test Params"),
        schema.description("The parameters supplied to the CoreMark®-PRO benchmarks"),
    ]
    coremark_pro_results: typing.Annotated[
        CertifyAllResult,
        schema.name("Test Results"),
        schema.description("Results of the CoreMark®-PRO benchmarks"),
    ]


@dataclass
class ErrorOutput:
    error: str
