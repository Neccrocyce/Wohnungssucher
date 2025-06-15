import unittest

from sources_and_data import test_user_config_0
from sources_and_data.ws_test import WSTest


class MyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    def test_1(self):
        config = test_user_config_0.config
        defaults = test_user_config_0.defaults_test

        platform = WSTest(config, defaults)
        platform()
        # self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
