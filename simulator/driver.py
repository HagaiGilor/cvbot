import time
from contextlib import suppress
from typing import Optional

from selenium.common import StaleElementReferenceException, NoSuchElementException, \
    ElementNotInteractableException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from simulator.constants import LINKEDIN_JOBS_SEARCH_URL, LINKEDIN_SIGN_IN_URL, EMAIL, PASSWORD, \
    RESUME_TEXT


class Driver(WebDriver):

    def sign_in_linked_in(self, username: str, password: str):
        self.get(LINKEDIN_SIGN_IN_URL)
        self.write_to_element(id_='username', value=username)
        self.write_to_element(id_='password', value=password)
        self.click_button_by_text(name='Sign in')

    def init_jobs_linkedin(self):
        self.get(LINKEDIN_JOBS_SEARCH_URL)
        self.click_button_by_text(name='Easy Apply')

    def apply_to_linkedin_jobs(self):
        time.sleep(4)
        list_items = "//li[contains(@class, 'jobs-search-results__list-item')]"
        # div_items = "//div[contains(@class, 'job-card-container')]"
        job_cards = self.find_elements(by=By.XPATH, value=list_items)
        print(f'{job_cards=}')
        self.iterate_job_cards(job_cards=job_cards)

    def iterate_job_cards(self, job_cards: list[WebElement]):
        for job_card in job_cards:
            print(f'Iterating on {job_card.text}=')
            self.click_linkedin_job_card(job_card=job_card)
            self.place_application_linkedin()
            time.sleep(2)

    def click_linkedin_job_card(self, job_card: WebElement):
        card_id = job_card.get_attribute('id')
        self.click_by_id(value=card_id)

    @staticmethod
    def generate_xpath(tag: str, text: Optional[str] = None,
                       class_: Optional[str] = None,
                       aria_label: Optional[str] = None):
        if text:
            return f"//{tag}[text()='{text}']"

        if class_:
            return f"//{tag}[contains(@class, '{class_}')]"

        if aria_label:
            return f"//{tag}[contains(@aria-label, '{aria_label}')]"

        raise ValueError("Missing value")

    def place_application_linkedin(self):
        try:
            self.wait_for_element_to_be_clickable(
                locator=(By.XPATH, self.generate_xpath(tag='span', text='Easy Apply')))
            self.click_element_by_text(element_tag='span', text='Easy Apply')
        except (NoSuchElementException, TimeoutException):
            return

        self.click_all_next_linkedin()
        self.fill_all_input_with_value()
        self.click_review_and_submit()

    def click_review_and_submit(self):
        try:
            self.click_element_by_text(element_tag='span', text='Review')
            self.click_element_by_text(element_tag='span', text='Submit application')
            self.press_x()
        except NoSuchElementException:
            self.abort_application()

    def abort_application(self):
        self.press_x()
        self.click_element_by_text(element_tag='span', text='Discard')

    def press_x(self):
        time.sleep(1)
        xpath = self.generate_xpath(tag='li-icon', class_='artdeco-button__icon')
        abort_button = self.wait_for_element_to_be_clickable(locator=(By.XPATH, xpath))
        abort_button.click()

    def click_element_by_text(self, element_tag: str, text: str):
        xpath = self.generate_xpath(tag=element_tag, text=text)

        try:
            self.find_element_by_xpath(value=xpath).click()
        except StaleElementReferenceException:
            self.find_element_by_xpath(value=xpath).click()

    def click_all_next_linkedin(self):
        while True:
            with suppress(NoSuchElementException):
                self.click_element_by_text(element_tag='span', text='Next')
                continue
            return

    def check_for_resume_selection(self):
        xpath = self.generate_xpath(tag='button', aria_label=RESUME_TEXT)
        resume_button = self.find_element_by_xpath(value=xpath)

        if not resume_button:
            return

        # Need to add wait for resume_button to be clickable, should be moved to it's own function
        self.wait_for_element_to_be_clickable(locator=(By.XPATH, xpath))
        resume_button.click()

    def fill_all_input_with_value(self, value: int = 1):
        inputs = self.find_elements(by=By.XPATH, value='//input')
        for input_ in inputs:

            try:
                input_id = input_.get_attribute('id')
            except StaleElementReferenceException:
                continue

            if not input_id:
                continue

            with suppress(ElementNotInteractableException):
                self.write_to_element(id_=input_id, value=value)

    def click_button_by_text(self, name: str):
        xpath = self.generate_xpath(tag='button', text=name)
        element = self.find_element_by_xpath(value=xpath)
        self.wait_for_element_to_be_clickable(locator=(By.XPATH, xpath))
        element.click()

    def wait_for_element_to_be_clickable(self, locator) -> WebElement:
        print(f'{locator=}')
        waited_element = WebDriverWait(driver=self, timeout=2).until(
            method=expected_conditions.element_to_be_clickable(locator))
        return waited_element

    def write_to_element(self, id_: str, value: str):
        element = self.find_element_by_id(value=id_)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(value)

    def find_element_by_name(self, value: str) -> WebElement:
        return self.find_element(by=By.NAME, value=value)

    def find_element_by_id(self, value: str) -> WebElement:
        return self.find_element(by=By.ID, value=value)

    def find_element_by_xpath(self, value: str) -> WebElement:
        return self.find_element(by=By.XPATH, value=value)

    def click_by_id(self, value: str):
        element = self.find_element_by_id(value=value)
        print(f'found {element=}')
        element.click()


def test_func():
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver.get(LINKEDIN_URL)
    # driver.click_by_id()

    driver = Driver()
    driver.maximize_window()
    linkedin(driver=driver)
    time.sleep(100)


def linkedin(driver: Driver):
    driver.sign_in_linked_in(username=EMAIL, password=PASSWORD)
    driver.init_jobs_linkedin()
    driver.apply_to_linkedin_jobs()
    time.sleep(100)


if __name__ == '__main__':
    test_func()
