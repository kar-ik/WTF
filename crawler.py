from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

options = Options()
options.headless = True 

driver = webdriver.Firefox(options=options)

def crawl_page(url):
    try:
        driver.get(url)
        time.sleep(2) 
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        print("\n--- Links Found ---")
        for link in links:
            href = link.get_attribute('href')
            print(f"Link: {href}")
        
        forms = driver.find_elements(By.TAG_NAME, 'form')
        print("\n--- Forms Found ---")
        for form in forms:
            action = form.get_attribute('action')
            method = form.get_attribute('method')
            print(f"Form action: {action}, method: {method}")
            
            inputs = form.find_elements(By.TAG_NAME, 'input')
            for input_field in inputs:
                input_name = input_field.get_attribute('name')
                input_type = input_field.get_attribute('type')
                print(f"Input name: {input_name}, type: {input_type}")
        
        hidden_elements = driver.find_elements(By.XPATH, "//input[@type='hidden']")
        print("\n--- Hidden Elements Found ---")
        for hidden in hidden_elements:
            print(f"Hidden field: {hidden.get_attribute('name')}")
    
    except Exception as e:
        print(f"An error occurred while crawling the page: {str(e)}")

target_url = "http://example.com"
crawl_page(target_url)

driver.quit()
