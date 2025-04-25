# RedditDLBot

A Superb DL Speed Boosted Reddit Downloader Bot powered by the [@BDBOTS API](https://bdbots.xyz). This bot allows you to effortlessly download high-quality media from Reddit.

---

## Features

- **Fast Download Speeds**: Utilize the BDBOTS API for super-fast downloads.
- **Multiple Quality Options**: Select the desired quality including 1080p, 720p, and more.
- **User-Friendly Interface**: Simple commands and inline buttons make usage seamless.
- **Progress Updates**: Real-time updates on download and upload progress.
- **Cache Management**: Efficient caching system to improve performance.

---

## Requirements

- Python 3.9 or above
- Telegram Bot API Token ([Get one from BotFather](https://t.me/BotFather))
- Telegram API ID API HASH From my.telegram.org

---

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/abirxdhack/RedditDLBot.git
cd RedditDLBot
```

### Step 2: Install Dependencies
Use `pip` to install the required Python libraries:
```bash
pip install -r requirements.txt
```

### Step 3: Configure the Bot
Create a `config.py` file and add the following variables:
```python
API_ID = "your-api-id"
API_HASH = "your-api-hash"
BOT_TOKEN = "your-bot-token"
COMMAND_PREFIX = ["/", ".", "!", ","]
```

Replace `"your-api-id"`, `"your-api-hash"`, and `"your-bot-token"` with your actual Telegram API credentials.

---

## Usage

### Start the Bot
Run the bot using the following command:
```bash
python main.py
```

### Commands
- `/start`: Displays the welcome message with helpful links.
- `/red [Reddit URL]`: Downloads media from the given Reddit URL.

Example:
```bash
/red https://reddit.com/r/example_post
```

---

## How it Works

1. The bot listens for the `/red` command along with a Reddit URL.
2. It fetches media metadata and available quality options via the BDBOTS API.
3. The user selects the desired quality through inline buttons.
4. The bot downloads the media, shows real-time progress, and uploads the media to Telegram.

---

## File Structure

```
RedditDLBot/
├── main.py          # Main bot logic
├── app.py           # Bot initialization
├── config.py        # Configuration file (API keys)
├── requirements.txt # Python dependencies
└── utils.py         # Logging and helper functions
```

---

## Contributing

Contributions are welcome! Feel free to fork the repository, make enhancements, and submit a pull request.

---

## Credit

- **API Powered By**: [BDBOTS](https://bdbots.xyz)  
  - Telegram: [T.me/BDBOTS](https://t.me/BDBOTS)  
  - GitHub: [GitHub.com/BDBOTS](https://github.com/BDBOTS)  

---

## Troubleshooting

- **Invalid URL**: Ensure the URL starts with `http`.
- **API Dead**: Check the status of the BDBOTS API or your API key.

---

## License

This project is currently not licensed. Consider adding a license if you wish to open-source your work.

---

## Contact

For any queries or issues, feel free to open an [issue](https://github.com/abirxdhack/RedditDLBot/issues) or contact the developer via the provided links in `/start`.

Happy downloading! 🚀
