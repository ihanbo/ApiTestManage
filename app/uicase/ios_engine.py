
import unittest
import os
from appium import webdriver
from time  import sleep


class  appiumSimpleTezt (unittest.TestCase):

    def  setUp(self):

        self.driver = webdriver.Remote(
            command_executor = 'http://127.0.0.1:4723/wd/hub',
            desired_capabilities = {
                # 'app':app,
                'platformName': 'iOS',
                'platformVersion': '12.3.1',
                'deviceName': 'iPhone',
                'bundleId': 'bitauto.application',
                'udid': 'dcfd046369ce2313d16a46c89358df63d336abfe'
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
