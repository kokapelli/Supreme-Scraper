import webbrowser
import re
import os, time
from threading import Thread
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
import queue as queue

URL = "https://www.supremenewyork.com/shop"
THREAD_NUM = 8
ITEM = "Leather Tanker Jacket"
RELEASE_DATE = "04/11/2019"
FULL_NAME       = "Larsa Hasselbacke"
EMAIL           = "larsa.hasselbacke@retard.com"
TELE            = "112"
ADDR            = "Rikspucko 69"
CITY            = "Tuppsala"
POST_CODE       = "75369"
COUNTRY         = "swe"
CARD_INFO       = '4539031065689519'
CARD_MONTH      = '10'
CARD_YEAR       = '20'
CARD_CVV        = '930'



START_TIME = datetime.datetime.now()


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

    driver.find_element_by_xpath(full_name_xpath).send_keys(FULL_NAME)
    driver.find_element_by_xpath(email_xpath).send_keys(EMAIL)
    driver.find_element_by_xpath(tele_xpath).send_keys(TELE)
    driver.find_element_by_xpath(addr_xpath).send_keys(ADDR)
    driver.find_element_by_xpath(city_xpath).send_keys(CITY)
    driver.find_element_by_xpath(postcode_xpath).send_keys(POST_CODE)
    driver.find_element_by_xpath(country_xpath).send_keys(COUNTRY)
    driver.find_element_by_xpath(card_xpath).send_keys(CARD_INFO)
    driver.find_element_by_xpath(card_month_xpath).send_keys(CARD_MONTH)
    driver.find_element_by_xpath(card_year_xpath).send_keys(CARD_YEAR)
    driver.find_element_by_xpath(card_cvv_xpath).send_keys(CARD_CVV)
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

def find_item(item, regex):
    while True: 
        try:
            query   = get_query(item.get())
            product = get_page(query)

            if re.findall(regex, str(product)):
                print("Item found!")
                init_checkout(query)
        except:
            print("Item Sold Out!")

        item.task_done()

def init_checkout(query):
    driver = init_driver(URL + query)
    driver = add_to_cart(driver)
    driver = checkout(driver)
    insert_info_checkout(driver)

def init():
    home_page = get_page()
    shop_page = get_assortment(home_page, 0) # Second parameter one fetches only new releases

    q = queue.Queue(maxsize=0)

    for i in range(THREAD_NUM):
        worker = Thread(target=find_item, args=(q, ITEM,))
        worker.setDaemon(True)
        worker.start()

    for i in shop_page:
        q.put(i)
        
    q.join()
    end = datetime.datetime.now()

    process_time = end - START_TIME
    print("The Process took: ", process_time)
    time.sleep(5)

def main():
    # Set release Date/Time
    # Y/M/D/H/M/S
    #release_time = datetime.datetime(2019, 4, 11, 22, 43, 45)
    
    # Create and assign names
    await_release()
    
main()