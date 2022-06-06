import unittest
from usd_preview_replacer.parse_mdl import parse_mdl


class TestMaterials(unittest.TestCase):
    def setUp(self):
        # Load test data
        mdl_file1 = "tests/test_files/lamp/Lamp.mdl"
        self.parsed_raw_1 = parse_mdl(mdl_file1)

    def test_base_color(self):
        #self.assertEqual(len(self.parsed_raw_1), 1)
        self.assertEqual(self.parsed_raw_1[0]["type"], "base_color")

    def test_normal(self):
        #self.assertEqual(len(self.parsed_raw_1), 2)
        self.assertEqual(self.parsed_raw_1[1]["type"], "normal")

    def test_metallic(self):
        #self.assertEqual(len(self.parsed_raw_1), 3)
        self.assertEqual(self.parsed_raw_1[2]["type"], "metallic")