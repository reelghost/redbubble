'''A script to login and post on redbubble'''

from time import sleep
import random
import pickle
import undetected_chromedriver as uc
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


def redbubble_login(driver, username, password):
    '''Logins to redbubble'''
    driver.get("https://www.redbubble.com/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ReduxFormInput2')))

    # Load cookies if they exist
    try:
        with open("redbubble_cookies.pkl", "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        sleep(random.randint(3,5))
    except FileNotFoundError:
        # Check if already logged in by looking for a logout element or user's profile
        if "auth/login" in driver.current_url:
            email_input = driver.find_element(By.ID, "ReduxFormInput1")
            password_input = driver.find_element(By.ID, "ReduxFormInput2")

            email_input.send_keys(username)
            sleep(random.randint(1,2))
            password_input.send_keys(password)
            sleep(random.randint(1,2))
            password_input.send_keys(Keys.RETURN)

    # check if login was a success
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="User account menu"]')))
        login_message = "success"
        print("Successfully logged in")
        # Save cookies after every login
        cookies = driver.get_cookies()
        with open("redbubble_cookies.pkl", "wb") as cookiesfile:
            pickle.dump(cookies, cookiesfile)
        sleep(4)
        
    except:
        login_message = "failed"
        print("Login Failed")
    return login_message

def image_upload(driver, image_path: str):
    '''
    Uploads the image from the path
        image_path - the absolute path of the image to be uploaded
    '''
    add_image_url = "https://www.redbubble.com/portfolio/images/new"
    driver.execute_script(f"window.open('{add_image_url}', '_blank');")
    
    # Switch to the new handle
    sleep(random.randint(8,10)) # to make it forget
    driver.switch_to.window(driver.window_handles[1])
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//input[@id="select-image-single"]'))).send_keys(image_path)
    except WebDriverException as e:
        print(e.msg)
    # wait for it to load the image
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@class="single-upload with-uploader has-image"]')))
        sleep(2)
        upload_msg = "success"
        print("Image uploaded successfully")
    except TimeoutException:
        upload_msg = "failed"
        print("Image not yet uploaded...")

    return upload_msg

def enable_product(product):
    '''Enable the product if disabled'''
    if 'all-disabled' in product.get_attribute('class'):
        product.find_element(By.CLASS_NAME, "rb-button.enable-all").click()
    
def make_pattern(product):
    '''
    Makes a pattern design for the product
    '''
    prod_name = product.get_attribute('data-type')
    edit_div = driver.find_element(By.CSS_SELECTOR, f'.image-box.{prod_name}')
    apply_change_btn = edit_div.find_element(By.CSS_SELECTOR, '.apply-changes')
    grid_option = edit_div.find_element(By.XPATH, f'//*[@data-track="ImgUpload:grid:{prod_name}"]')
    driver.execute_script("arguments[0].click();", grid_option)
    sleep(1)
    driver.execute_script("arguments[0].click();", apply_change_btn)
    # actions.move_to_element(apply_change_btn).click().perform()
    sleep(1)
    print(f'-> changed {prod_name} to pattern')
    msg = 'success'
    return msg

def for_pattern():
    '''
    Apply the pattern in every product
    '''
    products = [
            'womens_panel_clothing', 'panel_dress', 'panel_clothing', 'trapeze_dress', 'phone', 'desk_mat', 'mouse_pad',
            'throw_pillow', 'laptop', 'duvet', 'dog_mat', 'cat_mat', 'pet_blanket', 'mug', 'pet_bandana', 'scarf', 'tablet',
            'drawstring_bag', 'spiral_notebook', 'hardcover_journal', 'clock', 'gallery_board', 'acrylic_block', 'tapestry',
            'bath_mat', 'mounted_print', 'mask', 'apron', 'panel_tank', 'phone_wallet', 'pencil_skirt', 'leggings', 'socks',
            'backpack', 'duffle_bag',
    ]
    for product in products:
        prod_element = driver.find_element(By.XPATH, f'//div[@data-type="{product}"]')
        # enable product
        enable_product(prod_element)
        # for products with pattern feature, editing
        sleep(0.5)
        make_pattern(prod_element)
        sleep(1)

def for_sticker():
    '''Only for stickers'''
    sticker = driver.find_element(By.XPATH, f'//div[@data-type="sticker"]')
    enable_product(sticker)
    print("-> sticker enabled")
    # disable everything except sticker
    products = driver.find_elements(By.CSS_SELECTOR, "div.slide.with-uploader.has-image")
    for product in products:
        # disable all except sticker
        if 'all-disabled' not in product.get_attribute('class'):
            if product.get_attribute("data-type") != 'sticker':
                product.find_element(By.CLASS_NAME, "rb-button.disable-all.green").click()
    print("All products disbaled except stickers")


def terms_media_types():
    '''Click on terms and choose media types'''
    driver.find_element(By.XPATH, '//label[@for="media_design"]').click()
    driver.find_element(By.XPATH, '//label[@for="media_drawing"]').click()
    # mark as safe
    driver.find_element(By.ID, "work_safe_for_work_true").click()
    driver.find_element(By.ID, "rightsDeclaration").click()
    # save work
    driver.find_element(By.ID, "submit-work").click()


load_dotenv()

# TODO: for tag generator
# https://api.auuptools.com/redbubble/pure-tags?keyword=tortoise%20sticker&limit=10
options = uc.ChromeOptions()
ua = UserAgent()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-popup-blocking")

driver = uc.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
actions = ActionChains(driver)


# main
image_path = "F:\\joseLatest\\redbubble\\pics\\deadbone.png" # use an absolute path

# program start
login_message = redbubble_login(driver, os.getenv('USERNAME'), os.getenv('PASSWORD'))
if login_message == 'success':
    # Upload an image
    upload_message = image_upload(driver=driver, image_path=image_path)
    sleep(random.randint(2,3))

    if upload_message == "success":
        # input title and keywords
        title = "Adorable Cartoon Tortoise"
        tags = [
            "tortoise", "sticker", "reptile", "animal", "cute", "wildlife", "nature",
            "shell", "slow", "trendy", "adorable", "pet", "sea turtle", "green",
            "illustration", "hydro","cartoon tortoise", "funny tortoise", "cute animal",
            "whimsical tortoise", "tortoise lover", "reptile art", "kids room decor",
            "smiling tortoise", "animal illustration", "cartoon art", "quirky animal",
            "nature lover", "pet lover", "tortoise illustration", "wildlife art",
            "animal sticker", "hand-drawn", "watercolor tortoise"
        ]



        descr = " A detailed and expressive tortoise with a captivating smile. Whether you're a fan of reptiles, wildlife, or simply enjoy adorable art, this tortoise sticker is sure to bring a smile to your face and add a touch of nature-inspired charm to your collection"
        driver.find_element(By.XPATH, '//div[@class="add-work-details__title"]/input').send_keys(title)
        for tag in tags:
            driver.find_element(By.XPATH, '//div[@class="add-work-details__tags"]/textarea').send_keys(tag + ',')
        driver.find_element(By.XPATH, '//div[@class="add-work-details__description"]/textarea').send_keys(descr)
        sleep(random.randint(2,3))

        
        # do the edits for pattern
        # for_pattern() # Enable if you want patterns
        # for sticker
        for_sticker()
        # TODO: Add one for tshirts 500px x 500px
        
            
            
        sleep(5)
        # media types
        terms_media_types()

        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//a[@data-cy="edit-work-url"]')))
            print("Your design has been published")
        except:
            print("Publishing failed, please confirm")
else:
    print("unable to login")

sleep(10)
# close the browser
driver.quit()