# Автоматическая авторизация в Telegram Web

![work.](https://github.com/meKryztal/telegramweb/assets/47853767/5af228f0-233e-41d7-a958-fd5cb8d7a7a1)



Вид прокси: user:pass@ip:port



Ставит ник если его нету, ники без @, пример: SilverFox123Aq


По нажатию Enter в конце перезапускает скрипт, удаляя использованый файл сессии и прокси. после чего повторяет с следующем файлом сессии


Создать папку session и в нее закидывась файлы сессии

# Установка:
   ```
   pip install -r requirements.txt
   ```
Если хотите что б браузер запускался с devtool, то в 147 строке #chrome_options.add_argument("--auto-open-devtools-for-tabs") нужно убрать #
