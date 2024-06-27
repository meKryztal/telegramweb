import asyncio
import os
import glob
import re
import sqlite3
import time
import random
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon import functions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import zipfile
from selenium import webdriver
import socks
from colorama import *

api_id = '22579982'
api_hash = '2825cfd9be7a2b620e1753fa646cd3d6'

with open('proxy.txt', 'r') as proxy_file:
    proxy_data = proxy_file.read().strip()


match = re.match(r'(\w+):(\w+)@([\d\.]+):(\d+)', proxy_data)
if match:
    PROXY_USER = match.group(1)
    PROXY_PASS = match.group(2)
    PROXY_HOST = match.group(3)
    PROXY_PORT = match.group(4)

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


async def change_username(client):
    nicknames_file = "nicknames.txt"
    with open(nicknames_file, 'r') as file:
        nicknames = file.read().splitlines()

    while nicknames:
        nickname = random.choice(nicknames)
        try:
            await client(functions.account.UpdateUsernameRequest(nickname))
            print(f"{Fore.LIGHTYELLOW_EX}Username изменен на: {nickname}")
            nicknames.remove(nickname)
            with open(nicknames_file, 'w') as file:
                file.write('\n'.join(nicknames))
            return True
        except UsernameOccupiedError:
            print(f"{Fore.LIGHTYELLOW_EX}Username {nickname} занят. Пробую другой.")
            nicknames.remove(nickname)
            with open(nicknames_file, 'w') as file:
                file.write('\n'.join(nicknames))
            if not nicknames:
                print(f"{Fore.LIGHTYELLOW_EX}Файл с никами пуст.")
                return False


async def main(session_file):
    client = TelegramClient(session_file, api_id, api_hash, proxy=(socks.HTTP, PROXY_HOST, int(PROXY_PORT), True, PROXY_USER, PROXY_PASS))
    await client.connect()
    if not await client.is_user_authorized():
        print(f"{Fore.LIGHTYELLOW_EX}Сессия {session_file} не авторизована. Пропускаю.")
        await client.disconnect()
        os.remove(session_file)
        return False
    else:
        print(f"{Fore.LIGHTYELLOW_EX}Сессия {session_file} активна.")

        me = await client.get_me()

    try:
        await client.start()
        print(f"{Fore.LIGHTYELLOW_EX}Подключился")

        parsed_phone_number = me.phone
        print(f"{Fore.LIGHTYELLOW_EX}Номер телефона: {parsed_phone_number}")

        if me.username:
            print(f"{Fore.LIGHTYELLOW_EX}Username уже есть: {me.username}")
        else:
            username_changed = await change_username(client)
            if not username_changed:
                print(f"{Fore.LIGHTYELLOW_EX}Ошибка смены username.")
                return
        chrome_options = webdriver.ChromeOptions()

        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)
        #chrome_options.add_argument("--auto-open-devtools-for-tabs")
        chrome_options.add_argument("--disable-notifications")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(options=chrome_options)


        driver.get("https://web.telegram.org/k/")

        time.sleep(3)
        try:
            start_button1 = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[3]/div/div[2]/button[1]/div'))
            )
            start_button1.click()
        except Exception as e:
            print(f"{Fore.LIGHTYELLOW_EX}Error during phone number input: {e}")
            return
        time.sleep(1)
        try:

            phone_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[3]/div[2]/div[1]'))
            )

            phone_input.send_keys(Keys.CONTROL + "a")
            phone_input.send_keys(Keys.DELETE)
            phone_input.send_keys(parsed_phone_number)

            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[3]/button[1]'))
            )
            login_button.click()
        except Exception as e:
            print(f"{Fore.LIGHTYELLOW_EX}Телефон: {e}")
            return

        code_received = asyncio.Event()

        @client.on(events.NewMessage(chats=777000))
        async def normal_handler(event):
            nonlocal code_received
            code = re.search(r'\b\d{5}\b', event.message.message)
            if code:
                print(f"{Fore.LIGHTYELLOW_EX}Код: {code.group()}")

                try:
                    code_input = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[4]/div/div[3]/div/input'))
                    )
                    code_input.send_keys(code.group())
                    code_received.set()
                except Exception as e:
                    print(f"{Fore.LIGHTYELLOW_EX}Error during code input: {e}")

        await code_received.wait()
#Ваша ссылка с рефкой
        driver.get(
            "https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3DWaterCoinCISBot%26start%3D6922127089")

        start_button_two = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="column-center"]/div[1]/div/div[4]/div/div[4]/button[1]'))
        )
        start_button_two.click()


        try:
            await client.disconnect()
            print(f"Вышел из сессии")
        except sqlite3.OperationalError as e:
            print(f"SQLite Operational Error: {e}")

        input(f"{Fore.LIGHTYELLOW_EX}Нажми Enter после завершения")
        driver.quit()
        os.remove(session_file)
        with open('proxy.txt', 'r') as proxy_file:
            lines = proxy_file.readlines()

        proxy_to_remove = f"{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}\n"

        if proxy_to_remove in lines:
            lines.remove(proxy_to_remove)

        with open('proxy.txt', 'w') as proxy_file:
            proxy_file.writelines(lines)
        time.sleep(5)
    finally:
        await run_sessions()


async def run_sessions():
    while True:
        session_files = glob.glob("session/*.session")

        for session_file in session_files:
            try:
                await main(session_file)
            except Exception as e:
                print(f"Error in session {session_file}: {e}")

        print(f"{Fore.LIGHTYELLOW_EX}Сессии закончились.")
        await asyncio.sleep(10)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(run_sessions())
        except Exception as e:
            print(f"Main loop error: {e}")
        print(f"{Fore.LIGHTYELLOW_EX}Рестарт...")
        if input(f"{Fore.LIGHTYELLOW_EX}Press Enter to exit or type 'restart' to restart: ").strip().lower() != 'restart':
            break




