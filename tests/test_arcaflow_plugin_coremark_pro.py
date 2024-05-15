#!/usr/bin/env python3
import unittest
import coremark_pro_plugin
from coremark_pro_schema import (
    CertifyAllParams,
    CertifyAllResult,
    CertifyAllItem,
    SuccessOutput,
    ErrorOutput,
)
from arcaflow_plugin_sdk import plugin


params = CertifyAllParams(
    contexts = 2,
    workers = 4,
)

certify_all_item = CertifyAllItem(
    multi_core = 1.234,
    single_core = 2.468,
    scaling = 9.999,
)

class CoreMarkProTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(params)

        plugin.test_object_serialization(
            CertifyAllResult(
                cjpeg_rose7_preset = certify_all_item,
                core = certify_all_item,
                linear_alg_mid_100x100_sp = certify_all_item,
                loops_all_mid_10k_sp = certify_all_item,
                nnet_test = certify_all_item,
                parser_125k = certify_all_item,
                radix2_big_64k = certify_all_item,
                sha_test = certify_all_item,
                zip_test = certify_all_item,
                coremark_pro = certify_all_item,
            )
        )

        plugin.test_object_serialization(
            ErrorOutput(error="This is an error")
        )

    # def test_functional(self):
    #     output_id, output_data = coremark_pro_plugin.certify_all(
    #         params=params, run_id="plugin_ci"
    #     )

    #     self.assertEqual("success", output_id)
    #     self.assertEqual(
    #         output_data,
    #         SuccessOutput(
    #             coremark_pro_params=params,
    #             coremark_pro_results=CertifyAllResult(
                    
    #             )
    #         ),
    #     )


if __name__ == "__main__":
    unittest.main()
