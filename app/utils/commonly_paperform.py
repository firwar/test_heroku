from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import os
from dotenv import load_dotenv
import time


class CommonlyPaperform():

    def __init__(self, username, password):
        # Create a ChromeOptions object
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537")
        self.chrome_options.add_argument('window-size=1920,1080')
        self.chrome_options.add_argument('headless')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.username = username 
        self.password = password
        self.driver = None

    def start_driver_login(self):
        # Initialize the webdriver with the custom options
        self.driver = webdriver.Chrome(options=self.chrome_options)

        # driver = webdriver.Chrome(options=chrome_options)  # Recommended
        # Navigate to the URL
        self.driver.get("https://paperform.co/login")

        print("logging in")

        # Locate the email and password fields
        email_field = self.driver.find_element('xpath', '//input[@type="email"]')
        password_field = self.driver.find_element('xpath', '//input[@type="password"]')

        # Input the email and password
        email_field.send_keys(self.username)
        password_field.send_keys(self.password)

        # Locate the submit button and click it
        submit_button = self.driver.find_element('xpath', '//button[@type="submit"]')
        submit_button.click()

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a/span[text()="Create a form"]'))
            )
        except:
            print("could not find element")

        print("logged in")

    def create_post_survey_form(self, form_name, users, venue_name):
        # Once the specific element is found, navigate to another URL
        # Open a new window using JavaScript
        self.driver.execute_script("window.open('');")

        # Switch to the new window (assuming it's the last one)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get("https://paperform.co/create?slug=10ab34c1")


        matrix_element_xpath =  '//*[@id="richEditor"]/div[2]/div/div/div/figure[5]/div/div/div/div/div/div[2]/div/div[3]'
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, matrix_element_xpath))
            )
            print("matrix element now in view")
        except:
            print("matrix element not found")

        edit_url = self.driver.current_url
        print(edit_url)

        # Locate the parent element using its XPath
                                #//*[@id="richEditor"]/div[1]/div/div/div/figure[5]/div/div/div/div/div/div[1]/div/div[3]
        # working
        #parent_element_xpath =  '//*[@id="richEditor"]/div[2]/div/div/div/figure[5]/div/div/div/div/div/div[1]/div/div[3]'
        # xpath shows div[1] but div[2] instead?, unless using the first field configuration element?
        #parent_element_xpath = '//*[@id="richEditor"]/div[1]/div/div/div/figure[5]/div/div/div/div/div/div[2]/div[2]/div[3]'
        #parent_element_xpath = '//*[@id="richEditor"]/div[1]/div/div/div/figure[5]/div/div/div/div/div/div[2]/div[2]'
        parent_element = self.driver.find_element('xpath', matrix_element_xpath)

        # Scroll the parent element into view
        self.driver.execute_script("arguments[0].scrollIntoView();", parent_element)

        # Hover over the parent element
        action = ActionChains(self.driver)
        action.move_to_element(parent_element).perform()

        # Optionally, use JavaScript to focus on the parent element
        # driver.execute_script("arguments[0].focus();", parent_element)

        configure_xpath = '//*[@id="richEditor"]/div[2]/div/div/div/figure[5]/div/div/div/div/div/div[2]/div[2]/div[3]/a[@data-label="Configure"]'
        #configure_xpath = '//*[@id="richEditor"]/div[2]/div/div/div/figure[5]/div/div/div/div/div/div[1]/div/div[3]/a[@data-label="Configure"]'
        try:
            configure_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, configure_xpath))
            )
            print("configure element now in view")
        except:
            print("configure element not found")

        configure_button = self.driver.find_element('xpath', configure_xpath)
        print('found configure button')
        configure_button.click()



        try:
            back_to_editor_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@role="button"]/span[text()="Back to editor"]'))
            )
            print("Button is now in view.")
            # You can perform actions on the button here, like clicking it
        except:
            print("Button did not become visible within the specified time.")


        text_area = self.driver.find_element('xpath', '/html/body/div[37]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/textarea')
        text_area.clear()
        text_area.send_keys('\n'.join(users))

        back_to_editor_button.click()
        # Locate the parent element that holds the text
        # share_xpath = "//a[contains(@class, 'EditorTopBar__section') and contains(span, 'Share')]"
        # share_element = driver.find_element('xpath', share_xpath)
        # share_element.click()
        # 
        # social_xpath = "//a[contains(@class, 'EditorTopBar__submenuitem') and contains(span, 'Social & URL')]"
        # social_element = driver.find_element('xpath', social_xpath)
        # social_element.click()
        # 
        # sharelink_xpath = '//*[@id="root"]/div/div/div[5]/div/div[12]/div/div/div/div/textarea'
        # sharelink_element = driver.find_element_by_xpath(sharelink_xpath)
        # value = sharelink_element.get_attribute("value")
        # print("Textarea value:", value)

        #self.driver.execute_script("arguments[0].textContent = arguments[1];", venue_element, venue_question)
        #self.driver.execute_script("arguments[0].textContent = 'New text';", venue_element)

        # Change the venue question
        #venue_xpath = '//*[@id="richEditor"]/div[1]/div/div/div/figure[5]/div/div/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div/span/span'
        venue_xpath = '//*[@id="richEditor"]/div[1]/div/div/div/figure[5]/div/div/div/div/div/div[1]/div/div[1]/div[1]/div/div/div'
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, venue_xpath))
            )
            print("venue question now in view")
        except:
            print("venue question not found")

        venue_element = self.driver.find_element('xpath', venue_xpath)
        venue_question = "What did you think of " + venue_name + "?"
        action = ActionChains(self.driver)
        action.move_to_element(venue_element).perform()

        actions = ActionChains(self.driver)
        actions.move_to_element(venue_element)
        actions.click()
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
        actions.send_keys(Keys.DELETE)
        actions.send_keys(venue_question)
        actions.perform()
        # Use JavaScript to modify the text content of the element
        # print(venue_question)
        # self.driver.execute_script("arguments[0].innerText = 'Your new text here'", venue_element)
        # self.driver.execute_script('arguments[0].dispatchEvent(new Event("input", { bubbles: true }));', venue_element)


        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.1)
        # XPath to find the 'Save Changes' button
        save_changes_xpath = "//a[contains(@class, 'EditorSaveIndicator__save') and contains(text(), 'Save changes')]"
        # Wait until the element is clickable
        save_changes_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, save_changes_xpath)))

        # Click the element
        save_changes_element.click()

        saved_xpath = "//a[contains(@class, 'EditorSaveIndicator__revert') and contains(text(), 'Saved')]"

        # Wait until the element is clickable
        saved_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, saved_xpath)))
        print("done")

        configure_xpath = "//a[contains(@class, 'EditorTopBar__section') and contains(span, 'Configure')]"
        configure_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, configure_xpath)))
        configure_element.click()

        input_xpath = '//*[@id="root"]/div/div/div[5]/div/div[2]/div/div[1]/div/div[1]/div[2]/input'
        new_value = "New Form Name"

        try:
            input_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, input_xpath))
            )
            print("Input element now in view.")
            
            # Optionally, scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView();", input_element)
            
            # Clear the existing value and set a new value
            input_element.clear()
            input_element.send_keys(new_value)
        except Exception as e:
            print(f"An exception occurred: {e}")

        # Clear the existing value and set a new value
        input_element.clear()
        input_element.send_keys(form_name)



        # Click on the "Share" element and wait for the next element to load
        share_xpath = "//a[contains(@class, 'EditorTopBar__section') and contains(span, 'Share')]"
        share_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, share_xpath)))
        share_element.click()
        time.sleep(0.1)
        # Click on the "Social & URL" element and wait for the next element to load
        social_xpath = "//a[contains(@class, 'EditorTopBar__submenuitem') and contains(span, 'Social & URL')]"
        social_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, social_xpath)))
        max_attempts = 5
        attempts = 0
        while attempts < max_attempts:
            try:
                social_element.click()
                break
            except ElementClickInterceptedException:
                attempts += 1
                print(f"Click intercepted, retrying... {attempts}/{max_attempts}")
                time.sleep(0.5)

        # Find the "Share Link" textarea and get its value
        sharelink_xpath = '//*[@id="root"]/div/div/div[5]/div/div[12]/div/div/div/div/textarea'
        sharelink_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, sharelink_xpath)))
        sharelink_value = sharelink_element.get_attribute("value")
        print("Share Link value:", sharelink_value)
        # XPath to find the 'Save Changes' button
        save_changes_xpath = "//a[contains(@class, 'EditorSaveIndicator__save') and contains(text(), 'Save changes')]"
        # Wait until the element is clickable
        save_changes_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, save_changes_xpath)))

        # Click the element
        save_changes_element.click()

        saved_xpath = "//a[contains(@class, 'EditorSaveIndicator__revert') and contains(text(), 'Saved')]"

        # Wait until the element is clickable
        saved_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, saved_xpath)))
 
        print("done")
        # Note: If the website has CAPTCHA, manual intervention might be required.
        return sharelink_value

    def close(self):
        try:
            self.driver.quit()
        except:
            print("could not close driver")

if __name__ == "__main__":
    load_dotenv()
    PAPERFORM_USERNAME = os.environ.get('PAPERFORM_USERNAME')
    PAPERFORM_PASSWORD = os.environ.get('PAPERFORM_PASSWORD')

    form_name = "Test form 3"
    users = ["Jason", "David", "Somebody"]
    venue_name = "Acova"

    paperform_driver = CommonlyPaperform(PAPERFORM_USERNAME, PAPERFORM_PASSWORD)
    paperform_driver.start_driver_login()
    paperform_driver.create_post_survey_form(form_name, users, venue_name)
    paperform_driver.close()