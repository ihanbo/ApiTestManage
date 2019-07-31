import unittest
import os
from appium import webdriver
from time import sleep


class appiumSimpleTezt(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor='http://0.0.0.0:4723/wd/hub',
            desired_capabilities={
                # 'app':app,
                'platformName': 'iOS',
                'platformVersion': '12.3.1',
                'deviceName': 'iPhone',
                'bundleId': 'bitauto.application',
                'udid': '00008020-001E11502E04002E'
            }
        )

    def test_push_view(self):
        next_view_button = self.driver.find_element_by_accessibility_id("entry next view")
        next_view_button.click()

        sleep(2)

        back_view_button = self.driver.find_element_by_accessibility_id("Back")
        back_view_button.click()

    def tearDown(self):
        sleep(1)
    # self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(appiumSimpleTezt)
    unittest.TextTestRunner(verbosity=2).run(suite)
