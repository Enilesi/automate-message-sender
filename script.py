import time
from urllib.parse import quote

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from dotenv import load_dotenv
import os

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("WhatsAppContacts").sheet1

formatted_numbers = []
for cell in sheet.col_values(1):
    num = cell.strip().replace("+", "").replace(" ", "")
    if not num:
        continue
    if num.startswith("0"):
        num = num[1:]
    formatted = f"+40 {num[0:2]} {num[2]} {num[3:6]} {num[6:]}"
    formatted_numbers.append(formatted)



with open("message.txt", "r", encoding="utf-8") as f:
    message = f.read()

encoded = quote(message, safe='')

options = Options()
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")
print("⌛  Please scan QR (or restore session)…")
time.sleep(40)

try:
    btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button//div[text()='Continue']"))
    )
    btn.click()
    time.sleep(1)
except TimeoutException:
    pass

for number in formatted_numbers:
    print(f"🕿  → {number}")
    chat_url = f"https://web.whatsapp.com/send?phone={number}&text={encoded}"
    driver.get(chat_url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Phone number shared via url is invalid')]")
            )
        )
        print("   ❌ not on WhatsApp, skipping")
        continue
    except TimeoutException:
        pass

    try:
        inp = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
            )
        )
    except TimeoutException:
        print("   ❌ chat didn’t load, skipping")
        continue

    try:
        inp.send_keys("\n") 
        print("   ✅ sent")
    except Exception as e:
        print(f"   ❌ failed to send: {e}")

    time.sleep(3)

print("All done.")
driver.quit()