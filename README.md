# PremiumSoft.uz Info Bot

A simple Telegram bot that provides information about PremiumSoft.uz company and services.

## Features

- `/start` - Welcome message and introduction
- `/info` - Detailed information about PremiumSoft.uz
- `/help` - Available commands and help

## Bot Commands

### /start
Welcomes users and introduces the bot functionality.

### /info
Provides comprehensive information about PremiumSoft.uz including:
- Company overview
- Services offered
- Technologies used
- Contact information
- Why choose PremiumSoft.uz

### /help
Shows available commands and basic usage instructions.

## Deployment

1. Set up your Telegram bot token in Vercel environment variables
2. Deploy to Vercel
3. Set up the webhook using: `https://your-vercel-url.vercel.app/api/telegram/setup-webhook`

## Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from BotFather

## Testing

- Visit `https://your-vercel-url.vercel.app/api/telegram/test-bot` to test bot connectivity
- Send `/start` or `/info` to your bot on Telegram
