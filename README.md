# 📸 Instagram Scraper for Telegram

> A lightweight Telegram bot that fetches Instagram post metadata on demand — name, username, description, likes, comments, and publication date — delivered straight to your chat.

---

## ✨ Features

- 🔗 **Post scraping** — Extract rich data from any public Instagram post URL
- 👤 **Profile info** — Retrieves the author's name and username
- 📝 **Description parsing** — Full post caption with clickable `#hashtags` and `@mentions`
- ❤️ **Engagement stats** — Likes and comments count
- 📅 **Publication date** — When the post was originally shared
- 🔒 **Access control** — Whitelist-based authorization, only allowed users can interact with the bot
- 🐛 **Debug mode** — Saves raw HTML responses and logs for development

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- A Telegram Bot token (get one from [@BotFather](//t.me/BotFather))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/visnowden/instagram_telegram_scraper.git
   cd instagram_telegram_scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.exemple .env
   rm .env.exemple
   ```
   Then edit `.env` with your values (see [Configuration](\b#%EF%B8%8F-configuration) below).

4. **Run the bot**
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration

All configuration lives in the `.env` file:

| Variable           | Description                                              | Example                  |
|--------------------|----------------------------------------------------------|--------------------------|
| `TELEGRAM_TOKEN`   | Your bot token from @BotFather (**required**)            | `123456:ABC-DEF...`      |
| `AUTHORIZED_USERS` | Comma-separated list of allowed Telegram usernames       | `john,jane,bob`          |
| `DEV`              | Enable debug mode (`True` / `False`)                     | `False`                  |

```env
TELEGRAM_TOKEN=your_telegram_token_here
AUTHORIZED_USERS=your_telegram_username
DEV=False
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## 🤖 Bot Commands

| Command          | Description                                         |
|------------------|-----------------------------------------------------|
| `/start`         | Greets the authorized user                          |
| `/insta <url>`   | Fetches and displays metadata for an Instagram post |

### Example Usage

```
/insta https://www.instagram.com/p/XXXXXXXXXXX/
```

**Sample response:**
```
The post has the following data:
Name: John Doe
Username: @johndoe
Description: Beautiful sunset 🌅 #photography #nature

❤️ 1,234 likes
💬 56 comments
Publication date: January 1, 2025
```

---

## 📁 Project Structure

```
instagram_telegram_scraper/
├── main.py           # Bot logic and scraper
├── requirements.txt  # Python dependencies
├── .env.exemple      # Environment variable template
├── .gitignore
└── README.md
```

---

## 📦 Dependencies

| Package                  | Version   | Purpose                        |
|--------------------------|-----------|--------------------------------|
| `python-telegram-bot`    | 22.6      | Telegram Bot API wrapper       |
| `beautifulsoup4`         | 4.14.3    | HTML parsing / scraping        |
| `python-dotenv`          | 1.2.2     | Environment variable loading   |
| `requests`               | 2.32.5    | HTTP requests                  |

---

## 🐛 Debug Mode

Set `DEV=True` in your `.env` to enable debug mode:

- Prints HTTP status codes to the console
- Saves the raw HTML of each scraped page to `page_content.html`
- Appends errors to `logs.log`
- Shows response time on each bot reply

---

## 🛡️ Error Handling

The bot gracefully handles the following scenarios:

| Situation                         | Bot Response                                               |
|-----------------------------------|------------------------------------------------------------|
| Instagram is unreachable          | "Apparently Instagram is currently unavailable."           |
| Post has been deleted / bad link  | "Check the link again, the post may have been removed."    |
| Repeated failed URL               | Suggests retrying later                                    |
| Unknown error                     | Generic fallback message                                   |

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in this repository.

---

<div align="center">
  Made with ❤️ and Python
</div>
