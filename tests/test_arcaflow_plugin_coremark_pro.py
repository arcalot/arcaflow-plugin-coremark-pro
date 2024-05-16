#!/usr/bin/env python3
import unittest

import coremark_pro_plugin
from coremark_pro_schema import (
    TuneIterationsInput,
    Iterations,
    CertifyAllInput,
    CertifyAllResult,
    CertifyAllItem,
    ErrorOutput,
)
from arcaflow_plugin_sdk import plugin


tune_iterations_input = TuneIterationsInput(
    contexts=1,
    workers=1,
    target_run_time=2,
)

iterations = Iterations(
    cjpeg_rose7_preset=1,
    core=2,
    linear_alg_mid_100x100_sp=3,
    loops_all_mid_10k_sp=4,
    nnet_test=5,
    parser_125k=6,
    radix2_big_64k=7,
    sha_test=8,
    zip_test=9,
)

certify_all_input = CertifyAllInput(
    verify=True,
    contexts=1,
    workers=1,
    iterations=iterations,
)

certify_all_item = CertifyAllItem(
    multi_core=1.234,
    single_core=2.468,
    scaling=9.999,
)


class CoreMarkProTest(unittest.TestCase):
    @staticmethod
    def test_serialization_tune_iterations():
        plugin.test_object_serialization(tune_iterations_input)

    @staticmethod
    def test_serialization_certify_all():
        plugin.test_object_serialization(certify_all_input)

    @staticmethod
    def test_serialization_results():
        plugin.test_object_serialization(
            CertifyAllResult(
                cjpeg_rose7_preset=certify_all_item,
                core=certify_all_item,
                linear_alg_mid_100x100_sp=certify_all_item,
                loops_all_mid_10k_sp=certify_all_item,
                nnet_test=certify_all_item,
                parser_125k=certify_all_item,
                radix2_big_64k=certify_all_item,
                sha_test=certify_all_item,
                zip_test=certify_all_item,
                coremark_pro=certify_all_item,
            )
        )

    @staticmethod
    def test_serialization_error():
        plugin.test_object_serialization(ErrorOutput(error="This is an error"))

    def test_functional(self):
        ti_output_id, ti_output_data = coremark_pro_plugin.tune_iterations(
            params=tune_iterations_input, run_id="plugin_ci"
        )

        self.assertEqual(ti_output_id, "success")
        self.assertEqual(ti_output_data.contexts, 1)
        self.assertEqual(ti_output_data.workers, 1)
        self.assertIsInstance(ti_output_data.iterations.core, int)

        ca_output_id, ca_output_data = coremark_pro_plugin.certify_all(
            params=ti_output_data, run_id="plugin_ci"
        )

        self.assertEqual(ca_output_id, "success")
        self.assertEqual(ca_output_data.coremark_pro_params.contexts, 1)
        self.assertEqual(ca_output_data.coremark_pro_params.workers, 1)
        self.assertEqual(
            ca_output_data.coremark_pro_params.iterations.core,
            ca_output_data.coremark_pro_results.core.iterations,
        )
        self.assertIsInstance(
            ca_output_data.coremark_pro_results.core.multi_core,
            float,
        )
        print(f"CA output is: {ca_output_data}")


if __name__ == "__main__":
    unittest.main()
