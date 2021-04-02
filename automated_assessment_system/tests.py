from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


class FooTests(StaticLiveServerTestCase):
    fixtures = ["datadump.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_admin_can_log_in(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/accounts/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("super@example.com")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("pass")
        self.selenium.find_element_by_xpath('//input[@value="login"]').click()
        # Used Chrome inspection to copy xpath.
        username_element = self.selenium.find_element_by_xpath(
            '//*[@id="wrapper"]/div/div[2]/div/div/p'
        )
        self.assertEqual(
            username_element.text,
            "Hello, super@example.com",
            msg="Make sure we are logged in",
        )
