from selenium.webdriver.common.by import By
import re


def test_admin_home_page(selenium_driver):
    drv = selenium_driver
    assert re.search("Hello,\s+Stranger", drv.page_source)

    # Navigate to login page
    drv.find_element(By.LINK_TEXT, "Log In").click()
    assert "<h1>Login</h1>" in drv.page_source

    # Log in
    drv.find_element(By.NAME, "email").send_keys("john@example.com")
    drv.find_element(By.NAME, "password").send_keys("cat")
    drv.find_element(By.NAME, "submit").click()
    assert re.search("Hello,\s+john", drv.page_source)

    # Navigate to the users profile
    drv.find_element(By.LINK_TEXT, "Profile").click()
    assert "<h1>john</h1>" in drv.page_source
