import unittest
from parse_mdl import parse_mdl


class TestMaterials1(unittest.TestCase):
    """It tests the parsing of a material file, and checks that the parsed data is correct"""
    def setUp(self):
        # Load test data
        mdl_file = "test_files/lamp/Materials/MI_LampPost01.mdl"
        self.parsed_raw = parse_mdl(mdl_file)
        self.results = {
            "base_color": "test_files\\lamp\\Materials\\Textures\\T_BG_D.png",
            "normal": "test_files\\lamp\\Materials\\Textures\\T_B_N.png",
            "metallic": "test_files\\lamp\\Materials\\Textures\\T_BB_D.png",
            "emissive": "test_files\\lamp\\Materials\\Textures\\T_BB_D.png",
            "roughness": "test_files\\lamp\\Materials\\Textures\\T_BB_D.png",
            "specular": "test_files\\lamp\\Materials\\Textures\\T_BB_D.png",
        }

    def test_base_color1(self):
        self.assertIsNotNone(self.parsed_raw["base_color"])
        self.assertIn("base_color", self.parsed_raw)
        self.assertEqual(self.parsed_raw["base_color"]["texture_map"], self.results["base_color"])

    def test_normal1(self):
        self.assertIsNotNone(self.parsed_raw["normal"])
        self.assertIn("normal", self.parsed_raw)
        self.assertEqual(self.parsed_raw["normal"]["texture_map"], self.results["normal"])
    
    def test_specular1(self):
        self.assertIsNotNone(self.parsed_raw["specular"])
        self.assertIn("specular", self.parsed_raw)
        self.assertEqual(self.parsed_raw["specular"]["texture_map"], self.results["specular"])
        self.assertEqual(self.parsed_raw["specular"]["channel"], "x")

    def test_roughness1(self):
        self.assertIsNotNone(self.parsed_raw["roughness"])
        self.assertIn("roughness", self.parsed_raw)
        self.assertEqual(self.parsed_raw["roughness"]["texture_map"], self.results["roughness"])
        self.assertEqual(self.parsed_raw["roughness"]["channel"], "y")

    def test_metallic1(self):
        self.assertIsNotNone(self.parsed_raw["metallic"])
        self.assertIn("metallic", self.parsed_raw)
        self.assertEqual(self.parsed_raw["metallic"]["texture_map"], self.results["metallic"])
        self.assertEqual(self.parsed_raw["metallic"]["channel"], "z")

    def test_emissive1(self):
        self.assertIsNotNone(self.parsed_raw["emissive"])
        self.assertIn("emissive", self.parsed_raw)
        self.assertEqual(self.parsed_raw["emissive"]["texture_map"], self.results["emissive"])


if __name__ == '__main__':
    unittest.main()