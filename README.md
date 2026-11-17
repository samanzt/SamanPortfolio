# Saman Portfolio Bot

A bilingual Telegram bot designed to introduce my programming skills and projects while providing an administration panel for managing multiple Telegram bots.

<kbd> </kbd>

**Try the bot:** [@SamanPortfolioBot](https://t.me/SamanPortfolioBot)

## Features

- **Bilingual Interface:** Persian and English language support.
- **About Me:** Introduction and personal profile.
- **Skills:** Display of programming skills and technologies.
- **Projects:** Showcase projects with descriptions and links.
- **Contact:** Easy access to contact information.
- **Admin Panel:** Private management panel restricted to the owner.
- **Project Management:** Add, edit, and delete projects.
- **Bot Management:** Start and stop registered Telegram bots directly from the admin panel.

## Technologies

- Python
- python-telegram-bot
- SQLite
- python-dotenv
- Linux / VPS Hosting

## Project Structure

```text
SamanPortfolio/
├── database/
├── handlers/
├── keyboards/
├── services/
├── config.py
├── main.py
├── .env
├── .gitignore
└── requirements.txt
```

## Installation

1. Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd SamanPortfolio
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
```

5. Run the bot:

```bash
python main.py
```

## Security

- Bot tokens and sensitive information are stored in environment variables.
- The `.env` file must never be committed to GitHub.
- Administrative features are restricted to the authorized owner.

## Author

**Saman**

GitHub: [@samanzt](https://github.com/samanzt)