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
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1002063224194")
TELEGRAM_TOPIC_ID = os.environ.get("TELEGRAM_TOPIC_ID", "3189")

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

# User state management for lead generation
user_states = {}

class UserState:
    NORMAL = "normal"
    COLLECTING_PROJECT = "collecting_project"
    COLLECTING_NAME = "collecting_name"
    COLLECTING_PHONE = "collecting_phone"
    COLLECTING_EMAIL = "collecting_email"

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

def send_to_group(message, topic_id=None):
    """Send message to the specified Telegram group."""
    if not BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Bot token or chat ID not configured for group messaging")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    if topic_id:
        payload["message_thread_id"] = int(topic_id)

    try:
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()

        if response_json.get("ok"):
            logger.info(f"Message sent to group successfully")
            return True
        else:
            logger.error(f"Failed to send to group: {response_json}")
            return False

    except Exception as e:
        logger.error(f"Error sending to group: {e}")
        return False

def format_lead_message(user_data, telegram_user):
    """Format lead information for group message."""
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Handle None values for username and last_name
    username = telegram_user.get('username', 'Yoq / None')
    user_id = telegram_user.get('id', 'Nomalum / Unknown')
    first_name = telegram_user.get('first_name', 'Belgilanmagan / Not specified')
    last_name = telegram_user.get('last_name', 'Yoq / None')

    project = user_data.get('project', 'Belgilanmagan / Not specified')
    name = user_data.get('name', 'Belgilanmagan / Not specified')
    phone = user_data.get('phone', 'Belgilanmagan / Not specified')
    email = user_data.get('email', 'Belgilanmagan / Not specified')

    message = f"""
🆕 *Yangi mijoz so'rovi / New Lead*

📋 *Loyiha tavsifi / Project Description:*
{project}

👤 *Mijoz malumotlari / Customer Information:*
• *Ism / Name:* {name}
• *Telefon / Phone:* {phone}
• *Email:* {email}

📱 *Telegram profil malumotlari / Telegram Profile:*
• *Username:* @{username}
• *User ID:* {user_id}
• *Ism / First Name:* {first_name}
• *Familiya / Last Name:* {last_name}

⏰ *Vaqt / Timestamp:* {timestamp}
🤖 *Manba / Source:* PremiumSoft Telegram Bot

#YangiMijoz #NewLead #PremiumSoft
"""
    return message.strip()

def add_cta_to_message(message):
    """Add call-to-action to any bot response."""
    cta = "\n\n🤝 *Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!*"
    return message + cta

def is_group_chat(chat_type):
    """Check if the chat is a group or supergroup."""
    return chat_type in ['group', 'supergroup']

def is_bot_mentioned(text, bot_username="optimuspremiumbot"):
    """Check if bot is mentioned in the message."""
    if not text:
        return False

    text_lower = text.lower()
    mentions = [f"@{bot_username.lower()}", "/start", "/help", "/info", "/ai"]
    return any(mention in text_lower for mention in mentions)

def get_premiumsoft_info():
    """Get information about premiumsoft.uz in Uzbek"""
    info_text = """
🏢 *PremiumSoft.uz* - Farg'ona viloyati elektron hukumat markazining rasmiy brendi

🌟 *Biz haqimizda*
PremiumSoft - Farg'ona viloyati hokimligi qoshidagi Elektron hukumat rivojlantirish markazining rasmiy brendidir. 2008 yildan beri faoliyat yuritib, 30 dan ortiq yuqori malakali dasturchidan iborat professional jamoaga aylandik va ko'plab yirik IT loyihalarni amalga oshirdik.

📊 *Bizning natijalarimiz*
✅ 100+ veb-sayt yaratildi
✅ 40+ mobil ilova ishlab chiqildi
✅ 25+ axborot tizimi yaratildi
✅ 15+ yillik tajriba
✅ Davlat va xususiy sektor tajribasi

💼 *Asosiy xizmatlar*
• *Veb-sayt ishlab chiqish*: Noyob dizayn, CMS, elektron tijorat bilan maxsus saytlar
• *Mobil ilovalar*: Android, iOS, Windows uchun ilovalar Google Play va App Store'da
• *Telegram va Veb-botlar*: Platformalar bo'ylab avtomatlashtirilgan suhbat yechimlari
• *UX/UI Dizayn*: Veb-saytlar, tizimlar, ilovalar, bannerlar uchun ijodiy dizayn
• *Logo va Brending*: Biznes identifikatsiyasi va reklama dizayni
• *Domen va Hosting*: O'zbekistonda arzon hosting va domen xizmatlari, 24/7 qo'llab-quvvatlash

🚀 *Muhim loyihalar*
• *e-App*: Fuqarolarning davlat organlariga murojaat qilish elektron portali
• *Inter Faol Murojaat*: Jismoniy va yuridik shaxslar uchun interaktiv murojaat platformasi
• *My Fergana Portal*: Fuqarolar va biznes uchun elektron xizmatlar - zamonaviy elektron hukumat vositasi
• *E-Tahlil Mobile*: Kundalik faoliyat ma'lumotlari va jamoatchilik fikri bilan mobil vosita
• *MM-Baza Dashboard*: Ish jadvallari va bajarilgan vazifalarni real vaqtda monitoring qilish tizimi
• *Med KPI*: Bemorlar fikri asosida tibbiyot xodimlarini baholash tizimi

👥 *Rahbariyat jamoasi*
• Sirojiddin Maxmudov - Jamoa rahbari
• Muxtorov Abdullajon - Loyiha menejeri
• Solijon Abdurakhmonov - Birinchi o'rinbosar
• Feruza Tolipova - Bosh hisobchi
• Bakhrom Jalilov - RTM direktori

🧠 *Texnik mutaxassislar*
• Mikhail Domozhirov - Full-stack dasturchi
• Otabek Ahmadjonov - Backend jamoa rahbari
• Zokirjon Kholikov - Frontend jamoa rahbari
• Muhammadaziz Mamasodikov - Mobil jamoa rahbari
• Inomjon Abduvahobov - UX/UI dizayner

📞 *Aloqa ma'lumotlari*
🌐 Veb-sayt: https://premiumsoft.uz
📧 Email: info@premiumsoft.uz
📍 Manzil: Farg'ona viloyati, O'zbekiston
🏢 Aniq manzil: Farg'ona sh., Mustaqillik ko'chasi, 19-uy
🏛️ Vakolat: Farg'ona viloyati hokimligi

💬 *Boshlash*
O'zbekistonning yetakchi elektron hukumat rivojlantirish markazi bilan ishlashga tayyormisiz? Professional IT yechimlari uchun biz bilan bog'laning!

🤝 *Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!*

#PremiumSoft #ElektronHukumat #Ozbekiston #Fargona #ITYechimlar
    """
    return info_text.strip()

def get_company_knowledge_base():
    """Get comprehensive knowledge base about PremiumSoft.uz for AI context."""
    return """
PremiumSoft.uz Company Knowledge Base:

COMPANY OVERVIEW:
- Official Name: PremiumSoft.uz
- Official Status: Official brand of the Center for Development of Electronic Government under the Fergana Region administration
- Established: 2008 (15+ years of experience)
- Team Size: Over 30 highly qualified programmers
- Location: Fergana Region, Uzbekistan
- Authority: Fergana Regional Administration
- Specialization: E-government solutions, web development, mobile apps

TRACK RECORD & ACHIEVEMENTS:
- 100+ websites delivered
- 40+ mobile applications developed
- 25+ information systems created
- Serves both government and private sector clients
- 15+ years of continuous operation since 2008

CORE SERVICES:
1. Website Development: Custom sites with unique designs, content management systems, e-commerce features
2. Mobile Applications: Apps for Android, iOS, and Windows; published on Google Play and App Store
3. Telegram & Web Bots: Automated conversational solutions across platforms
4. UX/UI Design: Creative design for websites, systems, apps, banners, presentation materials
5. Logo & Branding: Business identity and advertising design
6. Domain & Hosting: Affordable hosting and domain services in Uzbekistan, free domain registration when hosting exceeds 1 GB, 24/7 support

NOTABLE PROJECTS:
1. e-App: Electronic appeals portal enabling citizens to submit feedback to government bodies efficiently (Fergana regional administration)
2. Inter Faol Murojaat: Platform for physical and legal persons to submit electronic, interactive appeals to government agencies
3. My Fergana Interactive Portal: Web portal offering electronic services for citizens and businesses - modern e-government tool
4. E-Tahlil Mobile App: Mobile tool presenting daily activity data from sector leaders, allowing public commentary and feedback
5. MM-Baza Dashboard: System for real-time monitoring of work schedules and completed tasks across public and private organizations
6. Med KPI (July 2024): Healthcare staff rating system using patient feedback to evaluate medical personnel and facilities

LEADERSHIP & MANAGEMENT TEAM:
- Sirojiddin Maxmudov: Team Leader
- Muxtorov Abdullajon: Project Manager
- Solijon Abdurakhmonov: First Deputy
- Feruza Tolipova: Chief Accountant
- Bakhrom Jalilov: Director of RTM

TECHNICAL EXPERTS & DEVELOPERS:
- Mikhail Domozhirov: Full-stack Developer
- Otabek Ahmadjonov: Backend Team Lead
- Zokirjon Kholikov: Frontend Team Lead
- Nodirbek Abdumansurov: Frontend Developer
- Odiljon Sultonov: Backend Developer
- Abbosbek Mahmudjonov: Frontend Developer

MOBILE DEVELOPMENT TEAM:
- Muhammadaziz Mamasodikov: Mobile Team Lead (experienced in leading development for multiple startups and projects, helps translate business requirements into functional software)
- Akmaljon Sotvoldiev: Mobile Developer

DESIGN & UX/UI TEAM:
- Inomjon Abduvahobov: UX/UI Designer

SUPPORT & SPECIALISTS:
- Sodirjon Abdurakhmonov: IT Specialist
- Oybek Akbarov: Call Center Specialist
- Nuriddin Juraev: Technical Specialist

COMPANY VALUES & APPROACH:
- Government-backed credibility and authority
- Expert team of over 30 qualified programmers
- E-government specialization with private sector expertise
- Proven track record with major government projects
- 24/7 technical support
- Comprehensive IT solutions from design to deployment
- Focus on both public and private sector needs

CONTACT INFORMATION:
Website: https://premiumsoft.uz
Email: info@premiumsoft.uz
Location: Fergana Region, Uzbekistan
Authority: Center for Development of Electronic Government, Fergana Regional Administration

BUSINESS FOCUS:
- E-government solutions and digital transformation
- Government agency digital services
- Private sector IT solutions
- Mobile-first approach for citizen services
- Real-time monitoring and feedback systems
- Healthcare technology solutions
- Interactive citizen engagement platforms
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
- Your name is OptimusPremium
- Your developer is Muhammad Aziz Mamasodikov, Software engineer at PremiumSoft.uz
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

def handle_lead_collection(chat_id, text, telegram_user):
    """Handle lead generation conversation flow."""
    user_data = user_states[chat_id]

    if user_data['state'] == UserState.COLLECTING_PROJECT:
        user_data['project'] = text
        user_data['state'] = UserState.COLLECTING_NAME
        response = "Rahmat! Endi ismingizni yozing:\n\nThank you! Now please write your name:"
        send_telegram_message(chat_id, response)

    elif user_data['state'] == UserState.COLLECTING_NAME:
        user_data['name'] = text
        user_data['state'] = UserState.COLLECTING_PHONE
        response = "Yaxshi! Endi telefon raqamingizni yozing:\n\nGreat! Now please write your phone number:"
        send_telegram_message(chat_id, response)

    elif user_data['state'] == UserState.COLLECTING_PHONE:
        user_data['phone'] = text
        user_data['state'] = UserState.COLLECTING_EMAIL
        response = "Ajoyib! Oxirida email manzilingizni yozing:\n\nExcellent! Finally, please write your email address:"
        send_telegram_message(chat_id, response)

    elif user_data['state'] == UserState.COLLECTING_EMAIL:
        user_data['email'] = text

        # Send lead to group
        lead_message = format_lead_message(user_data, telegram_user)
        send_to_group(lead_message, TELEGRAM_TOPIC_ID)

        # Reset user state
        user_states[chat_id] = {'state': UserState.NORMAL}

        # Confirm to user
        response = """Rahmat! Ma'lumotlaringiz muvaffaqiyatli yuborildi. Tez orada siz bilan bog'lanamiz!

Thank you! Your information has been successfully sent. We will contact you soon!

🤝 Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!"""
        send_telegram_message(chat_id, response)

def start_lead_collection(chat_id):
    """Start the lead collection process."""
    user_states[chat_id] = {
        'state': UserState.COLLECTING_PROJECT,
        'project': '',
        'name': '',
        'phone': '',
        'email': ''
    }

    response = """Ajoyib! Sizning loyihangiz haqida batafsil ma'lumot bering:
• Qanday xizmat kerak?
• Loyiha maqsadi nima?
• Qanday funksiyalar bo'lishi kerak?

Great! Please provide detailed information about your project:
• What service do you need?
• What is the project goal?
• What features should it have?"""

    send_telegram_message(chat_id, response)

def handle_message(message):
    """Handle a message from Telegram."""
    chat_id = message.get('chat', {}).get('id')
    chat_type = message.get('chat', {}).get('type', 'private')
    text = message.get('text', '')
    user_name = message.get('from', {}).get('first_name', 'Foydalanuvchi')
    telegram_user = message.get('from', {})

    if not chat_id:
        logger.error("Message missing chat_id")
        return

    # Group behavior control - only respond when mentioned
    if is_group_chat(chat_type) and not is_bot_mentioned(text):
        logger.info(f"Ignoring group message without mention: {text}")
        return

    logger.info(f"Received message from {chat_id}: {text}")

    # Handle lead generation states
    if chat_id in user_states and user_states[chat_id]['state'] != UserState.NORMAL:
        handle_lead_collection(chat_id, text, telegram_user)
        return

    # Handle /start command
    if text == '/start':
        ai_status = "🤖 AI Suhbat: ✅ Mavjud" if groq_client else "🤖 AI Suhbat: ❌ Mavjud emas"
        welcome_text = f"""👋 Salom {user_name}!

PremiumSoft.uz AI-powered ma'lumot botiga xush kelibsiz!

🚀 *Men nima qila olaman:*
• PremiumSoft.uz haqida savollaringizga javob beraman
• Kompaniya haqida batafsil ma'lumot beraman
• Texnik savollar bo'yicha yordam beraman
• Xizmatlarimiz va jamoamiz haqida suhbatlashaman

{ai_status}

💬 *PremiumSoft.uz haqida biror narsa so'rang!*
Yoki quyidagi buyruqlardan foydalaning:
• /info - Kompaniya haqida
• /help - Mavjud buyruqlar
• /ai - AI suhbat holati
• /order - Buyurtma berish"""

        response_with_cta = add_cta_to_message(welcome_text)
        send_telegram_message(chat_id, response_with_cta, parse_mode="Markdown")

    # Handle /info command
    elif text == '/info':
        info_text = get_premiumsoft_info()
        info_with_cta = add_cta_to_message(info_text)
        send_telegram_message(chat_id, info_with_cta, parse_mode="Markdown")

    # Handle /help command
    elif text == '/help':
        ai_status = "✅ Mavjud - Biror narsa so'rang!" if groq_client else "❌ Hozircha mavjud emas"
        help_text = f"""
🤖 *PremiumSoft.uz AI Ma'lumot Bot*

*Mavjud buyruqlar:*
/start - Botni ishga tushirish va xush kelibsiz xabarini ko'rish
/info - Kompaniya haqida batafsil ma'lumot
/help - Ushbu yordam xabarini ko'rsatish
/ai - AI suhbat holatini tekshirish
/order - Buyurtma berish jarayonini boshlash

*AI Suhbat:* {ai_status}

💬 *Qanday foydalanish:*
PremiumSoft.uz haqida biror savol yozing va men AI yordamida javob beraman!

*Misollar:*
• "Mobil dasturlash xizmatlaringiz haqida gapirib bering"
• "Jamoa a'zolaringiz kimlar?"
• "Qanday texnologiyalardan foydalanasiz?"
• "Mening startupimga qanday yordam bera olasiz?"
        """
        help_with_cta = add_cta_to_message(help_text.strip())
        send_telegram_message(chat_id, help_with_cta, parse_mode="Markdown")

    # Handle /order command
    elif text == '/order' or 'buyurtma' in text.lower() or 'order' in text.lower():
        start_lead_collection(chat_id)

    # Handle /ai command
    elif text == '/ai':
        if groq_client:
            ai_text = """🤖 *AI Suhbat Holati: ✅ FAOL*

Men Groq'ning Llama3 AI modeli bilan ishlayman va quyidagilar haqida to'liq ma'lumotga egaman:

📋 *PremiumSoft.uz haqida bilganlarim:*
• Barcha xizmatlar va texnologiyalar
• Jamoa a'zolari va ularning tajribasi
• Kompaniya qadriyatlari va yondashuvi
• Aloqa ma'lumotlari va joylashuv

💬 *Men bilan qanday suhbatlashish:*
Shunchaki biror narsa so'rang! Maxsus buyruqlar kerak emas.

*Sinab ko'ring:*
• "Qanday mobil texnologiyalardan foydalanasiz?"
• "Muhammadaziz haqida gapirib bering"
• "Mening elektron tijorat loyihamga qanday yordam bera olasiz?"
• "Ishlab chiqish jarayoningiz qanday?"
"""
        else:
            ai_text = """🤖 *AI Suhbat Holati: ❌ MAVJUD EMAS*

AI xususiyatlari hozircha o'chirilgan. Buning sababi:
• Groq API kaliti sozlanmagan
• Xizmat vaqtincha mavjud emas

📋 *Mavjud alternativalar:*
• Kompaniya haqida batafsil ma'lumot uchun /info dan foydalaning
• To'g'ridan-to'g'ri info@premiumsoft.uz ga murojaat qiling
• Veb-saytimizga tashrif buyuring: https://premiumsoft.uz

Bot asosiy ma'lumotlar uchun ishlashda davom etadi!"""

        ai_with_cta = add_cta_to_message(ai_text)
        send_telegram_message(chat_id, ai_with_cta, parse_mode="Markdown")

    # Handle all other messages with AI
    else:
        # Check if it's a command we don't recognize
        if text.startswith('/'):
            response_text = f"❓ Noma'lum buyruq: {text}\n\nMavjud buyruqlarni ko'rish uchun /help dan foydalaning yoki PremiumSoft.uz haqida biror narsa so'rang!"
            response_with_cta = add_cta_to_message(response_text)
            send_telegram_message(chat_id, response_with_cta)
        else:
            # Check for service interest keywords
            service_keywords = [
                'xizmat', 'service', 'loyiha', 'project', 'dastur', 'app', 'sayt', 'website',
                'mobil', 'mobile', 'bot', 'dizayn', 'design', 'ishlab chiqish', 'development',
                'kerak', 'need', 'qilish', 'make', 'yaratish', 'create', 'buyurtma', 'order'
            ]

            if any(keyword in text.lower() for keyword in service_keywords):
                # Trigger lead collection for service inquiries
                ai_response = get_ai_response(text, user_name)
                ai_with_cta = add_cta_to_message(ai_response)
                send_telegram_message(chat_id, ai_with_cta)

                # Follow up with lead collection offer
                follow_up = """
💼 Sizning loyihangiz uchun batafsil taklif tayyorlashimiz uchun /order buyrug'ini yuboring!

💼 To prepare a detailed proposal for your project, send the /order command!"""
                send_telegram_message(chat_id, follow_up)
            else:
                # Use AI to respond to the message
                logger.info(f"Processing AI request from {user_name}: {text}")
                ai_response = get_ai_response(text, user_name)
                ai_with_cta = add_cta_to_message(ai_response)
                send_telegram_message(chat_id, ai_with_cta)

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
