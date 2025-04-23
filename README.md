# Telegram Liveness Detection Bot

A Telegram bot that analyzes face images for liveness detection, deployed on Vercel.

## Features

- Receive images from users via Telegram
- Process images to detect faces
- Analyze faces for liveness detection
- Return liveness scores and other metrics

## Deployment Instructions

### 1. Prerequisites

- A Telegram bot token (create one via [@BotFather](https://t.me/botfather))
- A Vercel account
- GitHub account

### 2. Deploy to Vercel

1. Fork or clone this repository to your GitHub account
2. Connect your GitHub repository to Vercel
3. Configure the deployment:
    - Set the Framework Preset to "Other"
    - Add the environment variable `TELEGRAM_BOT_TOKEN` with your bot token
4. Deploy the project

### 3. Set Up the Webhook

After deployment, you need to set up the webhook to connect your Telegram bot to your Vercel deployment:

\`\`\`bash
# Option 1: Visit the setup URL
https://your-vercel-url.vercel.app/api/telegram/setup-webhook

# Option 2: Run the setup script
python setup-webhook.py YOUR_BOT_TOKEN your-vercel-url.vercel.app
