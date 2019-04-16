import webbrowser
import re
import os, time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from supreme_scraper import get_page, get_assortment, get_query, get_product_title
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup

debug = 0
url = "https://www.supremenewyork.com/shop"
RELEASE_DATE = datetime.datetime.now().strftime("%m/%d/%Y")
#RELEASE_DATE = "04/11/2019"

def get_date():
    return datetime.datetime.now().strftime("%m/%d/%Y")

def init_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)

    return driver

def close_driver(driver):
    driver.close()

def add_to_cart(driver):
    button = driver.find_element_by_xpath('//*[@id="add-remove-buttons"]/input')
    button.click()
    print("Added item to basket")

    return driver

def checkout(driver):
    wait_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cart"]/a[2]')))
    wait_button.click() 
    print("Entered Checkout")

    return driver

def insert_info_checkout(driver):
    full_name       = "Larsa Hasselbacke"
    email           = "larsa.hasselbacke@retard.com"
    tele            = "112"
    addr            = "Rikspucko 69"
    city            = "Tuppsala"
    post_code       = "75369"
    country         = "swe"
    card_info       = '4539031065689519'
    card_month      = '10'
    card_year       = '20'
    card_cvv        = '930'

    full_name_xpath = '//*[@id="order_billing_name"]'       # Query
    email_xpath     = '//*[@id="order_email"]'              # Query
    tele_xpath      = '//*[@id="order_tel"]'                # Query
    addr_xpath      = '//*[@id="bo"]'                       # Query
    city_xpath      = '//*[@id="order_billing_city"]'       # Query
    postcode_xpath  = '//*[@id="order_billing_zip"]'        # Query
    country_xpath   = '//*[@id="order_billing_country"]'    # Selection
    card_xpath      = '//*[@id="cnb"]'                      # Query
    card_month_xpath= '//*[@id="credit_card_month"]'        # Selection
    card_year_xpath = '//*[@id="credit_card_year"]'         # Selection
    card_cvv_xpath  = '//*[@id="vval"]'                     # Query
    agreement_xpath = '//*[@id="cart-cc"]/fieldset/p/label/div/ins' #Click
    process_xpath   = '//*[@id="pay"]/input'                #Click

    driver.find_element_by_xpath(full_name_xpath).send_keys(full_name)
    driver.find_element_by_xpath(email_xpath).send_keys(email)
    driver.find_element_by_xpath(tele_xpath).send_keys(tele)
    driver.find_element_by_xpath(addr_xpath).send_keys(addr)
    driver.find_element_by_xpath(city_xpath).send_keys(city)
    driver.find_element_by_xpath(postcode_xpath).send_keys(post_code)
    driver.find_element_by_xpath(country_xpath).send_keys(country)
    driver.find_element_by_xpath(card_xpath).send_keys(card_info)
    driver.find_element_by_xpath(card_month_xpath).send_keys(card_month)
    driver.find_element_by_xpath(card_year_xpath).send_keys(card_year)
    driver.find_element_by_xpath(card_cvv_xpath).send_keys(card_cvv)
    driver.find_element_by_xpath(agreement_xpath).click()
    driver.find_element_by_xpath(process_xpath).click()

    print("Personal Information Inserted")

def await_release(release_time=None):
    scheduler = BackgroundScheduler()
    scheduler.add_job(init, 'date', run_date = release_time)

    scheduler.start()
    print("Executes at:", release_time)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(0.01)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

def find_item(assortment, regex):
    count = 0
    for i in assortment:
        print("Searching for item... (" + str(count) + "/" + str(len(assortment)) + ")")
        curr_query   = get_query(i)
        curr_product = get_page(curr_query)

        if re.findall(regex, str(curr_product)):
            print("Item found: ", get_product_title(curr_product))
            print(url + curr_query)
            driver = init_driver(url + curr_query)
            driver = add_to_cart(driver)
            driver = checkout(driver)
            insert_info_checkout(driver)
            break

        count += 1

def init():
    start = datetime.datetime.now()
    #init_driver(url) # Might not be necessary, means to not be locked out of client
    # "Leather Tanker Jacket"
    regex = "Leather Tanker Jacket"
    rd = "04/11/2019"
    home_page = get_page()
    shop_page = get_assortment(home_page)
    item = find_item(shop_page, regex)
    end = datetime.datetime.now()

    process_time = end - start
    print("The Process took: ", process_time)
    time.sleep(5)

def main():
    # Y/M/D/H/M/S
    #release_time = datetime.datetime(2019, 4, 11, 22, 43, 45)
    #2019-04-16
    await_release()

main()