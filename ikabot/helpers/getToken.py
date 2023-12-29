#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

mail = "nfinewif@fjneufe.com"
pw = "iBIB!i78g!dqub"


def getToken(debug=False):
    if debug is True: print('Setting up Selenium...')
    
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")# REQUIRES MANUALLY SET USER-AGENT TO PREVENT HEADLESS DETECTION
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    driver = webdriver.Firefox(options=options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    token = None
    generated = False

    def interceptor(request):
        nonlocal token, generated
        if (
            request.method == "POST"
            and request.url == "https://gameforge.com/api/v1/auth/thin/sessions"
        ):
            # The body is in bytes so convert to a string
            body = request.body.decode("utf-8")
            # Load the JSON
            data = json.loads(body)
            raw_token = data["blackbox"]
            token = raw_token[4:]
            if debug is True:
                print(f"TOKEN = {token}")
                time.sleep(5)
            print("SUCCESS! Fresh blackbox token was successfully generated.\nPlease wait...")
            generated = True

    driver.request_interceptor = interceptor

    if debug is True: print('Connecting to Gameforge...')
    driver.get('https://lobby.ikariam.gameforge.com')
    time.sleep(2)

    email_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/form/div[2]/div/input')))
    pass_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/form/div[3]/div/input')))
    
    if debug is True: print("Entering login credentials...")
    email_input.clear()
    email_input.send_keys(mail)
    pass_input.clear()
    pass_input.send_keys(pw)

    if debug is True: print('Sending login request...')
    login_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/form/p/button[1]')))
    login_button.click()

    try:
        wait_count = 0
        while generated is False:
            time.sleep(0.2)
            wait_count += 1
            if wait_count > 100:
                if debug is True: print("Blackbox token generation timeout.")
                break
        if debug is True: print("Terminating webdriver...")
        driver.quit()
        return token

    except Exception as e:
        if debug is True:
            print(e)
            time.sleep(30)
        token = None
        driver.quit()
        return token