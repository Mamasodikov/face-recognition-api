from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import logging
from urllib.parse import parse_qs, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Try to import Groq for AI functionality
try:
    from groq import Groq
    AI_AVAILABLE = True
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    else:
        groq_client = None
        logger.warning("GROQ_API_KEY not set - AI features disabled")
except ImportError:
    AI_AVAILABLE = False
    groq_client = None
    logger.warning("Groq not installed - AI features disabled")

def send_telegram_message(chat_id, text, parse_mode=None):
    """Send a message to a Telegram chat."""
    if not BOT_TOKEN:
        logger.error("No bot token provided")
        return False

    if not chat_id:
        logger.error("No chat_id provided")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        logger.info(f"Sending message to chat {chat_id}")
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()

        if not response_json.get("ok"):
            error_code = response_json.get("error_code", "unknown")
            error_desc = response_json.get("description", "unknown error")
            logger.error(f"Telegram API error {error_code}: {error_desc}")
            return False

        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error sending message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        return False

def get_premiumsoft_info():
    """Get information about premiumsoft.uz"""
    info_text = """
🏢 *PremiumSoft.uz* - Premium Software Solutions

🌟 *About Us*
PremiumSoft.uz is a leading software development company in Uzbekistan, specializing in creating high-quality digital solutions for businesses of all sizes.

💼 *Our Services*
• Custom Software Development
• Web Application Development
• Mobile App Development (iOS & Android)
• E-commerce Solutions
• Database Design & Management
• Cloud Solutions & Migration
• IT Consulting & Support
• UI/UX Design Services

🚀 *Technologies We Use*
• Frontend: React, Vue.js, Angular, HTML5/CSS3
• Backend: Node.js, Python, PHP, Java
• Mobile: React Native, Flutter, Swift, Kotlin
• Databases: PostgreSQL, MySQL, MongoDB
• Cloud: AWS, Google Cloud, Azure

🎯 *Why Choose Us*
✅ Expert team of developers
✅ Agile development methodology
✅ 24/7 technical support
✅ Competitive pricing
✅ On-time project delivery
✅ Post-launch maintenance

👥 *Team Members*
• Muhammad Aziz Mamasodikov - Mobile Developer (Led development for multiple startups)
• Expert developers specializing in various technologies
• Experienced project managers and consultants

📞 *Contact Information*
🌐 Website: https://premiumsoft.uz
📧 Email: info@premiumsoft.uz
📱 Phone: +998 (XX) XXX-XX-XX
📍 Location: Tashkent, Uzbekistan

💬 *Get Started*
Ready to transform your business with premium software solutions? Contact us today for a free consultation!

#PremiumSoft #SoftwareDevelopment #Uzbekistan #TechSolutions
    """
    return info_text.strip()

def get_company_knowledge_base():
    """Get comprehensive knowledge base about PremiumSoft.uz for AI context."""
    return """
PremiumSoft.uz Company Knowledge Base:

COMPANY OVERVIEW:
- Name: PremiumSoft.uz
- Type: Software Development Company
- Location: Tashkent, Uzbekistan
- Specialization: Premium software solutions for businesses
- Motto: "неограниченное премиальное сотрудничество и передовые программные решения" (Unlimited premium cooperation and advanced software solutions)

SERVICES OFFERED:
1. Custom Software Development
2. Web Application Development (React, Vue.js, Angular, HTML5/CSS3)
3. Mobile App Development (iOS & Android, React Native, Flutter, Swift, Kotlin)
4. E-commerce Solutions
5. Database Design & Management (PostgreSQL, MySQL, MongoDB)
6. Cloud Solutions & Migration (AWS, Google Cloud, Azure)
7. IT Consulting & Support
8. UI/UX Design Services

TECHNOLOGIES:
Frontend: React, Vue.js, Angular, HTML5/CSS3
Backend: Node.js, Python, PHP, Java
Mobile: React Native, Flutter, Swift, Kotlin
Databases: PostgreSQL, MySQL, MongoDB
Cloud: AWS, Google Cloud, Azure

TEAM MEMBERS:
- Muhammad Aziz Mamasodikov: Mobile Developer, experienced in leading development for multiple startups and projects of various sizes, helps startups translate business requirements into functional software

COMPANY VALUES:
- Expert team of developers
- Agile development methodology
- 24/7 technical support
- Competitive pricing
- On-time project delivery
- Post-launch maintenance

CONTACT:
Website: https://premiumsoft.uz
Email: info@premiumsoft.uz
LinkedIn: https://www.linkedin.com/company/premium-soft-uz
Location: Tashkent, Uzbekistan

BUSINESS APPROACH:
- Helps startups and businesses of all sizes
- Translates business requirements into functional software
- Focuses on premium quality solutions
- Provides ongoing support and maintenance
"""

def get_ai_response(user_message, user_name="User"):
    """Get AI response using Groq API."""
    if not groq_client:
        return "🤖 AI features are currently unavailable. Please use /info for company information or /help for available commands."

    try:
        # Create context with company information
        system_prompt = f"""You are an AI assistant for PremiumSoft.uz, a software development company in Uzbekistan.

{get_company_knowledge_base()}

Your role:
- Answer questions about PremiumSoft.uz services, team, and capabilities
- Help potential clients understand what the company offers
- Provide technical guidance related to software development
- Be friendly, professional, and knowledgeable
- If asked about something not related to PremiumSoft.uz or software development, politely redirect to company topics
- Always be helpful and encourage potential clients to contact the company

User's name: {user_name}
"""

        # Get AI response
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192",  # Free model
            max_tokens=500,
            temperature=0.7
        )

        response = chat_completion.choices[0].message.content
        return response

    except Exception as e:
        logger.error(f"AI response error: {e}")
        return "🤖 I'm having trouble processing your request right now. Please try again or use /info for company information."

def handle_message(message):
    """Handle a message from Telegram."""
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    user_name = message.get('from', {}).get('first_name', 'User')

    if not chat_id:
        logger.error("Message missing chat_id")
        return

    logger.info(f"Received message from {chat_id}: {text}")

    # Handle /start command
    if text == '/start':
        ai_status = "🤖 AI Chat: ✅ Available" if groq_client else "🤖 AI Chat: ❌ Unavailable"
        welcome_text = f"""👋 Hello {user_name}!

Welcome to PremiumSoft.uz AI-Powered Info Bot!

🚀 *What I can do:*
• Answer questions about PremiumSoft.uz
• Provide detailed company information
• Help with technical inquiries
• Chat about our services and team

{ai_status}

💬 *Just ask me anything about PremiumSoft.uz!*
Or use these commands:
• /info - Company overview
• /help - Available commands
• /ai - AI chat status"""
        send_telegram_message(chat_id, welcome_text, parse_mode="Markdown")

    # Handle /info command
    elif text == '/info':
        info_text = get_premiumsoft_info()
        send_telegram_message(chat_id, info_text, parse_mode="Markdown")

    # Handle /help command
    elif text == '/help':
        ai_status = "✅ Available - Just ask me anything!" if groq_client else "❌ Currently unavailable"
        help_text = f"""
🤖 *PremiumSoft.uz AI Info Bot*

*Available commands:*
/start - Start the bot and see welcome message
/info - Get detailed company information
/help - Show this help message
/ai - Check AI chat status

*AI Chat:* {ai_status}

💬 *How to use:*
Just type any question about PremiumSoft.uz and I'll answer using AI!

*Examples:*
• "Tell me about your mobile development services"
• "Who are your team members?"
• "What technologies do you use?"
• "How can you help my startup?"
        """
        send_telegram_message(chat_id, help_text.strip(), parse_mode="Markdown")

    # Handle /ai command
    elif text == '/ai':
        if groq_client:
            ai_text = """🤖 *AI Chat Status: ✅ ACTIVE*

I'm powered by Groq's Llama3 AI model and have comprehensive knowledge about:

📋 *What I know about PremiumSoft.uz:*
• All services and technologies
• Team members and their expertise
• Company values and approach
• Contact information and location

💬 *How to chat with me:*
Just ask me anything! No special commands needed.

*Try asking:*
• "What mobile technologies do you use?"
• "Tell me about Muhammad Aziz"
• "How can you help my e-commerce project?"
• "What's your development process?"
"""
        else:
            ai_text = """🤖 *AI Chat Status: ❌ UNAVAILABLE*

AI features are currently disabled. This could be because:
• Groq API key is not configured
• Service is temporarily unavailable

📋 *Available alternatives:*
• Use /info for detailed company information
• Contact us directly at info@premiumsoft.uz
• Visit our website: https://premiumsoft.uz

The bot will still work for basic information!"""

        send_telegram_message(chat_id, ai_text, parse_mode="Markdown")

    # Handle all other messages with AI
    else:
        # Check if it's a command we don't recognize
        if text.startswith('/'):
            response_text = f"❓ Unknown command: {text}\n\nUse /help to see available commands or just ask me anything about PremiumSoft.uz!"
            send_telegram_message(chat_id, response_text)
        else:
            # Use AI to respond to the message
            logger.info(f"Processing AI request from {user_name}: {text}")
            ai_response = get_ai_response(text, user_name)
            send_telegram_message(chat_id, ai_response)

def setup_webhook(host, custom_url=None):
    """Set up webhook for the bot."""
    if not BOT_TOKEN:
        return {"error": "Bot token not configured"}

    try:
        if custom_url:
            webhook_url = custom_url
        else:
            webhook_url = f"https://{host}/api/telegram"

        # Validate webhook URL
        if not webhook_url.startswith('https://'):
            return {"error": "Webhook URL must use HTTPS"}

        # Set the webhook
        set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        params = {
            'url': webhook_url,
            'drop_pending_updates': True
        }
        response = requests.post(set_webhook_url, json=params, timeout=10)
        result = response.json()

        if result.get('ok'):
            logger.info(f"Webhook successfully set to {webhook_url}")
        else:
            logger.error(f"Failed to set webhook: {result.get('description', 'Unknown error')}")

        return result

    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return {"error": str(e)}

def test_bot():
    """Test bot connectivity."""
    if not BOT_TOKEN:
        return {"error": "Bot token not configured"}

    try:
        get_me_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(get_me_url, timeout=10)
        result = response.json()

        if result.get('ok'):
            bot_info = result.get('result', {})
            return {
                "success": True,
                "bot_name": bot_info.get('first_name', 'Unknown'),
                "username": bot_info.get('username', 'Unknown'),
                "bot_id": bot_info.get('id')
            }
        else:
            return {"error": result.get('description', 'Unknown error')}

    except Exception as e:
        logger.error(f"Error testing bot: {e}")
        return {"error": str(e)}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Send headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

            # Basic status
            response_text = '✅ PremiumSoft.uz Info Bot is active on Vercel!\n'

            if BOT_TOKEN:
                response_text += "✅ Bot token is configured\n"
            else:
                response_text += "❌ WARNING: Bot token is not configured!\n"

            # Handle specific endpoints
            if 'setup-webhook' in self.path:
                host = self.headers.get('Host', 'unknown-host')
                result = setup_webhook(host)
                response_text += f"\nWebhook setup result: {json.dumps(result)}"

            elif 'test-bot' in self.path:
                result = test_bot()
                response_text += f"\nBot test result: {json.dumps(result)}"

            self.wfile.write(response_text.encode())

        except Exception as e:
            logger.error(f"GET error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())

    def do_POST(self):
        """Handle POST requests (Telegram webhooks)."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > 0:
                # Read request body
                post_data = self.rfile.read(content_length)
                update = json.loads(post_data.decode('utf-8'))

                logger.info("Received Telegram update")

                # Process the update
                if 'message' in update:
                    handle_message(update['message'])
                else:
                    logger.info("Received non-message update (ignored)")

            # Send OK response
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())

        except Exception as e:
            logger.error(f"POST error: {e}")
            # Still send 200 to prevent Telegram retries
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
