# linkpull
A very, very simple file downloader disguised as a telegram bot.

I made this to send links from my iPhone to my Windows PC to automatically download stuff.\
This thing only opens one connection and downloads files using it, unlike IDM, for example.\
This limits your download speeds and performs drastically worse than IDM.

# Usage
Install dependencies:
```python
py -m pip install -r requirements.txt
```

Put your telegram bot token inside .env.example and rename it to .env

You can create a bot using @BotFather on Telegram if you haven't.

Start the bot:
```python
python bot.py
```

Simply send a **direct download link** to your bot in Telegram.

Example:
```
https://example.com/file.zip
```
The bot will:

- Start downloading the file
- Show progress updates
- Save it to the ./downloads folder

# Disclaimer
This project is intended for personal use and convenience. Make sure you comply with the terms of service of any site you download from.
