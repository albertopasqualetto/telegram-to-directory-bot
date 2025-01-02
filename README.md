# telegram-to-directory-bot
Telegram bot which recieves files and moves them to a specified destination directory

Usage with docker compose (adapt it to your needs):
```yaml
# a telegram-bot-api server is needed to download big files
telegram-bot-api:
    image: aiogram/telegram-bot-api:latest
    environment:
      TELEGRAM_API_ID: "YOUR_API_ID"
      TELEGRAM_API_HASH: "YOUR_API_HASH"
      TELEGRAM_LOCAL: 1
    volumes:
      - telegram-bot-api-data:/var/lib/telegram-bot-api
    ports:
      - "8081:8081"

telegram-to-directory-bot:
    container_name: telegram-to-directory-bot
    build:
      context: ./telegram-to-directory-bot
      dockerfile: Dockerfile
      tags:
        - "telegram-to-directory-bot:latest"
    environment:
      TG_BOT_API_SERVER: "http://telegram-bot-api:8081"
      TG_BOT_TOKEN: "YOUR_BOT_TOKEN"
      TG_FILTERS: "FILTER1|FILTER2|OTHER_FILTERS"   # Filters for the files to be moved, filter names are the same as here https://docs.python-telegram-bot.org/en/v21.6/telegram.ext.filters.html separated by "|"
      UID: 1001 # UID of the user that will own the files, optional
      GID: 988  # GID of the group that will own the files, optional
      PERMISSIONS: "766" # Permissions to set for the files, optional
      DESTINATION_NAME: "destination"   # Name of the destination directory; only used for tg answer message, optional
    volumes:
      - telegram-bot-api-data:/origin
      - type: bind
        source: /path/to/destination/on/host
        target: /destination
```