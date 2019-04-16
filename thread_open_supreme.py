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

DEBUG = 0
THREAD_NUM = 1
URL = "https://www.supremenewyork.com/shop"


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

def find_item(item, regex):
    while True: 
        query   = get_query(item.get())
        product = get_page(query)

        if re.findall(regex, str(product)):
            init_checkout(query)

        item.task_done()

def init_checkout(query):
    print("Item found: ")
    print(URL + query)
    driver = init_driver(URL + query)
    driver = add_to_cart(driver)
    driver = checkout(driver)
    insert_info_checkout(driver)

def init():
    #init_driver(url) # Might not be necessary, means to not be locked out of client
    # "Leather Tanker Jacket"
    regex = "Leather Tanker Jacket"
    rd = "04/11/2019"
    home_page = get_page()
    shop_page = get_assortment(home_page, 1) # Second paramter one fetches only new releases

    q = queue.Queue(maxsize=0)

    for i in range(THREAD_NUM):
        worker = Thread(target=find_item, args=(q, regex,))
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