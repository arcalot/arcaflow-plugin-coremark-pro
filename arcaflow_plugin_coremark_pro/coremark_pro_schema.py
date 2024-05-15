#!/usr/bin/env python3

import typing
from dataclasses import dataclass
from arcaflow_plugin_sdk import schema, plugin


@dataclass
class CertifyAllParams:
    contexts: typing.Annotated[
        int,
        schema.name("Contexts"),
        schema.description("Number of contexts per benchmark"),
    ]
    workers: typing.Annotated[
        int,
        schema.name("Workers"),
        schema.description("Number of workers per benchmark")
    ]


@dataclass
class CertifyAllItem:
    multi_core: typing.Annotated[
        float,
        schema.id("MultiCore"),
        schema.name("MultiCore"),
        schema.description("Workload retult - Multi-Core (iter/s)"),
    ]
    single_core: typing.Annotated[
        float,
        schema.id("SingleCore"),
        schema.name("SingleCore"),
        schema.description("Workload retult - Single-Core (iter/s)"),
    ]
    scaling: typing.Annotated[
        float,
        schema.id("Scaling"),
        schema.name("Scaling"),
        schema.description("Workload retult - Scaling"),
    ]


@dataclass
class CertifyAllResult:
    cjpeg_rose7_preset: typing.Annotated[
        CertifyAllItem,
        schema.id("cjpeg-rose7-preset"),
        schema.name("CJPEG Rose7 Preset"),
        schema.description("Workload: CJPEG Rose7 Preset"),
    ]
    core: typing.Annotated[
        CertifyAllItem,
        schema.id("core"),
        schema.name("Core"),
        schema.description("Workload: Core"),
    ]
    linear_alg_mid_100x100_sp: typing.Annotated[
        CertifyAllItem,
        schema.id("linear_alg-mid-100x100-sp"),
        schema.name("Linear Alg Mid 100x100 SP"),
        schema.description("Workload: Linear Alg Mid 100x100 SP"),
    ]
    loops_all_mid_10k_sp: typing.Annotated[
        CertifyAllItem,
        schema.id("loops-all-mid-10k-sp"),
        schema.name("Loops All Mid 10k SP"),
        schema.description("Workload: Loops All Mid 10k SP"),
    ]
    nnet_test: typing.Annotated[
        CertifyAllItem,
        schema.name("NNet Test"),
        schema.description("Workload: NNet Test"),
    ]
    parser_125k: typing.Annotated[
        CertifyAllItem,
        schema.id("parser-125k"),
        schema.name("Parser 125k"),
        schema.description("Workload: Parser 125k"),
    ]
    radix2_big_64k: typing.Annotated[
        CertifyAllItem,
        schema.id("radix2-big-64k"),
        schema.name("Radix2 Big 64k"),
        schema.description("Workload: Radix2 Big 64k"),
    ]
    sha_test: typing.Annotated[
        CertifyAllItem,
        schema.id("sha-test"),
        schema.name("SHA Test"),
        schema.description("Workload: SHA Test"),
    ]
    zip_test: typing.Annotated[
        CertifyAllItem,
        schema.id("zip-test"),
        schema.name("ZIP Test"),
        schema.description("Workload: ZIP Test"),
    ]
    coremark_pro: typing.Annotated[
        CertifyAllItem,
        schema.id("CoreMark-PRO"),
        schema.name("CoreMark PRO"),
        schema.description("Benchmark: CoreMark-PRO"),
    ]

certifyAllResultSchema = plugin.build_object_schema(CertifyAllResult)


@dataclass
class SuccessOutput():
    coremark_pro_params: typing.Annotated[
        CertifyAllParams,
        schema.name("Test Params"),
        schema.description("The paramaters applied to the CoreMark®-PRO tests"),
    ]
    coremark_pro_results: typing.Annotated[
        CertifyAllResult,
        schema.name("Test Results"),
        schema.description("The results of the CoreMark®-PRO")
    ]


@dataclass
class ErrorOutput:
    error: str
