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

def send_telegram_message(chat_id, text, parse_mode=None, message_thread_id=None):
    """Send a message to a Telegram chat, optionally to a specific topic/thread."""
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

    # Add topic/thread support
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    try:
        logger.info(f"Sending message to chat {chat_id}" + (f" in thread {message_thread_id}" if message_thread_id else ""))
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

def send_telegram_location(chat_id, latitude, longitude, message_thread_id=None):
    """Send a location to a Telegram chat."""
    if not BOT_TOKEN:
        logger.error("No bot token provided")
        return False

    if not chat_id:
        logger.error("No chat_id provided")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation"
    payload = {
        "chat_id": chat_id,
        "latitude": latitude,
        "longitude": longitude
    }

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    try:
        logger.info(f"Sending location to chat {chat_id}")
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()

        if not response_json.get("ok"):
            error_code = response_json.get("error_code", "unknown")
            error_desc = response_json.get("description", "unknown error")
            logger.error(f"Telegram API error {error_code}: {error_desc}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error sending location: {e}")
        return False

def send_typing_action(chat_id, message_thread_id=None):
    """Send typing action to show bot is processing."""
    if not BOT_TOKEN or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except:
        return False

def get_user_stats(chat_id):
    """Get user interaction statistics."""
    if chat_id not in user_states:
        user_states[chat_id] = {'state': UserState.NORMAL, 'message_count': 0, 'last_interaction': None}

    import datetime
    user_states[chat_id]['message_count'] = user_states[chat_id].get('message_count', 0) + 1
    user_states[chat_id]['last_interaction'] = datetime.datetime.now()

    return user_states[chat_id]

def is_business_hours():
    """Check if it's business hours in Uzbekistan (UTC+5)."""
    import datetime

    # Get current time in Uzbekistan (UTC+5)
    utc_now = datetime.datetime.utcnow()
    uzbekistan_time = utc_now + datetime.timedelta(hours=5)

    # Business hours: 9 AM to 5 PM, Monday to Saturday
    if uzbekistan_time.weekday() >= 6:  # Sunday only
        return False

    hour = uzbekistan_time.hour
    return 9 <= hour <= 17

def get_business_hours_message(user_language="uzbek"):
    """Get business hours message."""
    if user_language == "english":
        return "\n\n🕒 *Business Hours:* Monday-Saturday, 9:00-17:00 (Uzbekistan time)"
    else:
        return "\n\n🕒 *Ish vaqti:* Dushanba-Shanba, 9:00-17:00 (O'zbekiston vaqti)"

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

    # Handle None values - don't translate usernames and technical fields
    username = telegram_user.get('username', 'None')
    user_id = telegram_user.get('id', 'Unknown')
    first_name = telegram_user.get('first_name', 'Not specified')
    last_name = telegram_user.get('last_name', 'None')

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
• *First Name:* {first_name}
• *Last Name:* {last_name}

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
    bot_username_lower = bot_username.lower()

    # Check for direct mentions
    mentions = [f"@{bot_username_lower}"]

    # Check for commands (with or without bot username)
    commands = ["/start", "/help", "/info", "/ai", "/order", "/hours", "/location"]
    for command in commands:
        mentions.extend([
            command,
            f"{command}@{bot_username_lower}"
        ])

    return any(mention in text_lower for mention in mentions)

def clean_command_text(text, bot_username="optimuspremiumbot"):
    """Remove bot username from command text."""
    if not text:
        return text

    # Remove @botusername from commands
    bot_mention = f"@{bot_username.lower()}"
    if bot_mention in text.lower():
        # Find the position and remove it
        text_lower = text.lower()
        mention_pos = text_lower.find(bot_mention)
        if mention_pos != -1:
            text = text[:mention_pos] + text[mention_pos + len(bot_mention):]

    return text.strip()

def is_reply_to_bot(message):
    """Check if the message is a reply to the bot."""
    reply_to_message = message.get('reply_to_message')
    if not reply_to_message:
        return False

    # Check if the replied message is from the bot
    replied_from = reply_to_message.get('from', {})
    return replied_from.get('is_bot', False) and replied_from.get('username', '').lower() == 'optimuspremiumbot'

def detect_language(text):
    """Detect if the message is in Uzbek or English based on keywords and patterns."""
    if not text:
        return "uzbek"  # Default to Uzbek

    text_lower = text.lower()

    # Uzbek indicators
    uzbek_keywords = [
    # --- Salomlashish va xayrlashish ---
    'salom', 'assalomu alaykum', 'alaykum assalom', 'xayr', 'xayrli tong',
    'xayrli kun', 'xayrli kech', 'omad', 'tabriklayman', 'marhamat',

    # --- Odob va minnatdorchilik ---
    'rahmat', 'katta rahmat', 'iltimos', 'iltimos qilaman', 'uzr', 'kechirasiz',
    'afsus', 'rozi', 'marhamat', 'qabul qildim', 'tasdiq',

    # --- Savollar uchun so'zlar ---
    'nima', 'qanday', 'qachon', 'qayerda', 'qayerdan', 'kim', 'nega', 'qancha',
    'qaysi', 'qanaqa', 'qanaqasiga', 'nimaga', 'qayerlik', 'qaysi biri',

    # --- Loyiha va xizmatlar ---
    'loyiha', 'xizmat', 'dastur', 'sayt', 'vebsayt', 'mobil', 'ilova',
    'ishlab chiqish', 'dasturlash', 'yordam', 'kompaniya', 'firma', 'jamoa',
    'zakaz', 'buyurtma', 'texnologiya', 'rivojlantirish', 'yaratish',
    'qilish', 'tuzish', 'platforma', 'raqamlashtirish', 'startap', 'hamkorlik',
    'maqsad', 'natija', 'funksiya', 'imkoniyat', 'integratsiya', 'backend',
    'frontend', 'server', 'ma’lumotlar bazasi',

    # --- Moliyaviy va ish jarayoni ---
    'narx', 'tekinga', 'shartnoma', 'hisob', 'pul', 'to\'lov', 'muddat',
    'byudjet', 'arzon', 'qimmat', 'daromad', 'foyda', 'investitsiya',

    # --- Foydalanuvchi uchun so'zlar ---
    'foydalanuvchi', 'mijoz', 'aloqa', 'savol', 'javob', 'fikr', 'taklif',
    'so\'rov', 'shikoyat', 'profil', 'akkaunt', 'ro\'yxat', 'kirish', 'chiqish',

    # --- Uzbek tiliga xos belgilar ---
    'o\'', 'g\'', 'sh', 'ch', 'ng', 'ʼ', '‘', '’', 'yo\'q', 'ha'
    ]

    # English indicators
    english_keywords = [
    # --- Greetings & Polite words ---
    'hello', 'hi', 'hey', 'good morning', 'good evening', 'good night',
    'bye', 'goodbye', 'thanks', 'thank', 'thank you', 'please', 'welcome',

    # --- Common requests & needs ---
    'need', 'want', 'require', 'looking for', 'searching', 'help', 'support',
    'assist', 'guide', 'show', 'tell', 'explain', 'about',

    # --- Question words ---
    'what', 'how', 'when', 'where', 'who', 'why', 'which', 'whose',

    # --- Project / Business related ---
    'project', 'service', 'solution', 'product', 'platform', 'system',
    'app', 'application', 'website', 'web', 'portal', 'software', 'mobile',
    'development', 'design', 'build', 'create', 'make', 'deploy', 'launch',
    'technology', 'digital', 'automation', 'integration', 'startup', 'business',

    # --- Company / Team ---
    'company', 'team', 'group', 'agency', 'enterprise', 'organization',
    'partner', 'collaboration', 'client', 'customer', 'user', 'profile',

    # --- Finance & Contract ---
    'price', 'cost', 'budget', 'payment', 'invoice', 'deal', 'contract',
    'profit', 'income', 'revenue', 'investment', 'free', 'cheap', 'expensive',

    # --- General small words ---
    'can', 'could', 'will', 'would', 'shall', 'should',
    'you', 'your', 'me', 'my', 'i', 'we', 'our', 'they', 'their',
    'with', 'for', 'and', 'the', 'is', 'are', 'was', 'were', 'very', 'much'
    ]

    # Check for explicit English requests first
    explicit_english_requests = [
        'english', 'ingliz', 'inglizcha', 'in english', 'speak english',
        'can you speak english', 'switch to english', 'ingliz tilida',
        'please respond in english', 'answer in english'
    ]

    if any(phrase in text_lower for phrase in explicit_english_requests):
        return "english"

    # Very specific English phrases that indicate clear English intent
    strong_english_phrases = [
        'hello there', 'thank you very much', 'could you please tell me',
        'i would like to know', 'can you tell me about', 'i need information about',
        'what can you do for me', 'how can you help me with', 'please provide information'
    ]

    # Only switch to English if there's a very specific English phrase AND no Uzbek words
    has_strong_english = any(phrase in text_lower for phrase in strong_english_phrases)

    # Check for any Uzbek words (even common ones)
    uzbek_words = [
        'salom', 'rahmat', 'iltimos', 'kerak', 'nima', 'qanday', 'qachon', 'qayerda',
        'loyiha', 'xizmat', 'dastur', 'sayt', 'mobil', 'yordam', 'kompaniya', 'jamoa',
        'haqida', 'uchun', 'bilan', 'qilish', 'berish', 'olish', 'ko\'rish', 'bo\'lish'
    ]
    has_uzbek_words = any(word in text_lower for word in uzbek_words)

    # Very strict English detection - only if very specific English phrases and NO Uzbek
    if has_strong_english and not has_uzbek_words and len(text.split()) >= 4:
        return "english"

    # Default to Uzbek in ALL other cases
    return "uzbek"

def get_order_prompt(language="uzbek"):
    """Get the order prompt in the specified language."""
    if language == "english":
        return "\n\n💼 To prepare a detailed proposal for your project, send the /order command!"
    else:
        return "\n\n💼 Sizning loyihangiz uchun batafsil taklif tayyorlashimiz uchun /order buyrug'ini yuboring!"

def get_premiumsoft_info():
    """Get information about premiumsoft.uz in Uzbek"""
    info_text = """
🏢 *PremiumSoft.uz* - Farg'ona viloyati elektron hukumat markazining rasmiy brendi

🌟 *Biz haqimizda*
PremiumSoft — bu Farg'onada joylashgan, ko'p yillik tajribaga ega bo'lgan professional, kreativ va jips jamoa. Biz davlat va xususiy sektor uchun maxsus informatsion tizimlar, veb-saytlar, mobil ilovalar, va Telegram botlar ishlab chiqamiz.

Kompaniya "Farg'ona viloyati elektron hukumatni rivojlantirish markazi" ning "PremiumSoft" savdo belgisi ostida faoliyat yuritadi.

📊 *Statistika va yutuqlar*
PremiumSoft jamoasi quyidagi natijalarga erishgan:

✅ 1208+ veb-sayt yaratildi
✅ 46+ mobil ilova ishlab chiqildi
✅ 26+ informatsion tizim qurildi
✅ 75+ Telegram bot yaratildi
✅ 10+ dasturiy mahsulot ishlab chiqildi
✅ 2268+ mijoz xizmat ko'rsatildi

Bu raqamlar kompaniyaning keng ko'lamli tajribasi va ishonchli hamkorlik asosida ishlashini ko'rsatadi.

🧭 *Xizmatlar ro'yxati*
PremiumSoft quyidagi xizmatlarni taklif etadi:

• *Veb-saytlar yaratish* (korporativ, e-commerce, portal)
• *Mobil ilovalar ishlab chiqish* (iOS, Android)
• *Telegram botlar* (avtomatlashtirilgan xizmatlar uchun)
• *Informatsion tizimlar* (CRM, ERP, e-hukumat)
• *UX/UI dizayn* (foydalanuvchi interfeysi va tajribasi)
• *Brend logotiplari va identifikatsiya*
• *Hosting va domen xizmatlari*
• *Server texnik xizmat ko'rsatish*
• *IT-konsalting va raqamlashtirish strategiyasi*

Bundan tashqari, raqamlashtirish bo'yicha dastlabki tahlil va konsultatsiya bepul taqdim etiladi.

🚀 *Muhim loyihalar*
• *e-App*: Fuqarolarning davlat organlariga murojaat qilish elektron portali
• *Inter Faol Murojaat*: Jismoniy va yuridik shaxslar uchun interaktiv murojaat platformasi
• *My Fergana Portal*: Fuqarolar va biznes uchun elektron xizmatlar - zamonaviy elektron hukumat vositasi
• *E-Tahlil Mobile*: Kundalik faoliyat ma'lumotlari va jamoatchilik fikri bilan mobil vosita
• *MM-Baza Dashboard*: Ish jadvallari va bajarilgan vazifalarni real vaqtda monitoring qilish tizimi
• *Med KPI*: Bemorlar fikri asosida tibbiyot xodimlarini baholash tizimi

🧑‍💻 *Jamoa a'zolari*
PremiumSoft jamoasi turli sohalarda yetakchi mutaxassislardan iborat:

• Sirojiddin Maxmudov — Rahbar
• Solijon Abdurakhmonov - Birinchi o'rinbosar
• Feruza Tolipova — Bosh buxgalter
• Muxtorov Abdullajon — Loyihalar menejeri
• Muhammadaziz Mamasaodiqov — Team Lead, mobil dasturchi
• Zokirjon Xolikov — Team Lead, frontend dasturchi
• Otabek Ahmadjonov — Team Lead, backend dasturchi
• Inomjon Abduvahobov — UX/UI dizayner
• Mikhail Domojirov — Full-stack dasturchi

Jamoa har bir loyiha uchun individual yondashuv va zamonaviy texnologiyalar asosida ishlaydi.

💡 *Yondashuv va qadriyatlar*
PremiumSoft quyidagi qadriyatlarga amal qiladi:

• *Innovatsiya* — har bir loyiha zamonaviy texnologiyalar asosida amalga oshiriladi
• *Mas'uliyat* — mijozlar bilan shartnoma asosida, aniq muddat va sifat kafolati bilan ishlash
• *Yoshlar bilan ishlash* — yangi avlod dasturchilarini o'qitish va ish bilan ta'minlash
• *Eksportga yo'naltirilganlik* — IT mahsulotlarini xalqaro bozorlarga olib chiqish

📞 *Aloqa ma'lumotlari*
🌐 Veb-sayt: https://premiumsoft.uz
📧 Email: info@premiumsoft.uz
📞 Telefon: +998 73 244 05 35
📍 Manzil: Farg'ona viloyati, O'zbekiston
🏢 Aniq manzil: Fargʻona, Ahmad Al-Fargʻoniy shoh koʻchasi, 53, 4-qavat
🏛️ Vakolat: Farg'ona viloyati hokimligi

💬 *Boshlash*
O'zbekistonning yetakchi elektron hukumat rivojlantirish markazi bilan ishlashga tayyormisiz? Professional IT yechimlari uchun biz bilan bog'laning!

🤝 *Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!*

#PremiumSoft #ElektronHukumat #Ozbekiston #Fargona #ITYechimlar
    """
    return info_text.strip()

def get_premiumsoft_info_english():
    """Get information about premiumsoft.uz in English"""
    info_text = """
🏢 *PremiumSoft.uz* - Official Brand of Fergana Regional e-Government Center

🌟 *About Us*
PremiumSoft is a professional, creative and experienced team located in Fergana. They develop custom information systems, websites, mobile applications, and Telegram bots for government and private sectors.

The company operates under the brand "Fergana Regional Electronic Government Development Center".

📊 *Statistics and Achievements*
PremiumSoft team has achieved the following results:

✅ 1208+ websites created
✅ 46+ mobile applications developed
✅ 26+ information systems built
✅ 75+ Telegram bots created
✅ 10+ software products developed
✅ 2268+ clients served

These numbers demonstrate the company's extensive experience and reliable partnership-based work.

🧭 *Services List*
PremiumSoft offers the following services:

• *Website Development* (corporate, e-commerce, portal)
• *Mobile Application Development* (iOS, Android)
• *Telegram Bots* (for automated services)
• *Information Systems* (CRM, ERP, e-government)
• *UX/UI Design* (user interface and experience)
• *Brand Logos and Identity*
• *Hosting and Domain Services*
• *Server Technical Support*
• *IT Consulting and Digitalization Strategy*

Additionally, initial analysis and consultation on digitalization is provided free of charge.

🚀 *Notable Projects*
• *e-App*: Electronic appeals portal for citizens to government bodies
• *Inter Faol Murojaat*: Interactive appeals platform for legal/physical persons
• *My Fergana Portal*: E-government services for citizens and businesses
• *E-Tahlil Mobile*: Daily activity monitoring with public feedback
• *MM-Baza Dashboard*: Real-time work schedule and task monitoring
• *Med KPI*: Healthcare staff rating system using patient feedback

🧑‍💻 *Team Members*
PremiumSoft team consists of leading specialists in various fields:

• Sirojiddin Maxmudov — Leader
• Muxtorov Abdullajon — Project Manager
• Muhammadaziz Mamasaodiqov — Team Lead, Mobile Developer
• Zokirjon Xolikov — Team Lead, Frontend Developer
• Otabek Ahmadjonov — Team Lead, Backend Developer
• Inomjon Abduvahobov — UX/UI Designer
• Feruza Tolipova — Chief Accountant
• Mikhail Domojirov — Full-stack Developer

The team works with individual approach for each project using modern technologies.

💡 *Approach and Values*
PremiumSoft follows these core values:

• *Innovation* — every project is implemented using modern technologies
• *Responsibility* — working with clients based on contracts, with clear deadlines and quality guarantees
• *Youth Development* — training and employing new generation programmers
• *Export Orientation* — bringing IT products to international markets

📞 *Contact Information*
🌐 Website: https://premiumsoft.uz
📧 Email: info@premiumsoft.uz
📞 Phone: +998 73 244 05 35
📍 Location: Fergana Region, Uzbekistan
🏢 Address: Fergana, Ahmad Al-Fergani Shah Street, 53, 4th floor
🏛️ Authority: Fergana Regional Administration

💬 *Get Started*
Ready to work with Uzbekistan's leading e-government development center? Contact us for professional IT solutions!

🤝 *If you need our services, feel free to contact us!*

#PremiumSoft #eGovernment #Uzbekistan #Fergana #TechSolutions
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
- 1208+ websites delivered
- 46+ mobile applications developed
- 26+ information systems created
- 75+ Telegram bots created
- 10+ software products developed
- 2268+ clients served
- Serves both government and private sector clients
- Multi-year experience with extensive portfolio

CORE SERVICES:
1. Website Development: Corporate, e-commerce, portal websites
2. Mobile Application Development: iOS, Android applications
3. Telegram Bots: Automated services and conversational solutions
4. Information Systems: CRM, ERP, e-government systems
5. UX/UI Design: User interface and experience design
6. Brand Logos and Identity: Corporate branding and identification
7. Hosting and Domain Services: Server hosting and domain registration
8. Server Technical Support: Technical maintenance and support
9. IT Consulting and Digitalization Strategy: Digital transformation consulting

Additionally, initial analysis and consultation on digitalization is provided free of charge.

NOTABLE PROJECTS:
1. e-App: Electronic appeals portal enabling citizens to submit feedback to government bodies efficiently (Fergana regional administration)
2. Inter Faol Murojaat: Platform for physical and legal persons to submit electronic, interactive appeals to government agencies
3. My Fergana Interactive Portal: Web portal offering electronic services for citizens and businesses - modern e-government tool
4. E-Tahlil Mobile App: Mobile tool presenting daily activity data from sector leaders, allowing public commentary and feedback
5. MM-Baza Dashboard: System for real-time monitoring of work schedules and completed tasks across public and private organizations
6. Med KPI (July 2024): Healthcare staff rating system using patient feedback to evaluate medical personnel and facilities

TEAM MEMBERS:
PremiumSoft team consists of leading specialists in various fields:

- Sirojiddin Maxmudov — Leader
- Muxtorov Abdullajon — Project Manager
- Muhammadaziz Mamasaodiqov — Team Lead, Mobile Developer
- Zokirjon Xolikov — Team Lead, Frontend Developer
- Otabek Ahmadjonov — Team Lead, Backend Developer
- Inomjon Abduvahobov — UX/UI Designer
- Feruza Tolipova — Chief Accountant
- Mikhail Domojirov — Full-stack Developer

The team works with individual approach for each project using modern technologies.

APPROACH AND VALUES:
PremiumSoft follows these core values:

- Innovation — every project is implemented using modern technologies
- Responsibility — working with clients based on contracts, with clear deadlines and quality guarantees
- Youth Development — training and employing new generation programmers
- Export Orientation — bringing IT products to international markets
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
Phone: +998 73 244 05 35
Address: Fergana, Ahmad Al-Fergani Shah Street, 53, 4th floor
Location: Fergana Region, Uzbekistan
Authority: Center for Development of Electronic Government, Fergana Regional Administration
Business Hours: Monday-Saturday, 9:00-17:00 (Uzbekistan time)

BUSINESS FOCUS:
- E-government solutions and digital transformation
- Government agency digital services
- Private sector IT solutions
- Mobile-first approach for citizen services
- Real-time monitoring and feedback systems
- Healthcare technology solutions
- Interactive citizen engagement platforms
"""

def get_ai_response(user_message, user_name="User", user_language="uzbek"):
    """Get AI response using Groq API in the user's language."""
    if not groq_client:
        if user_language == "english":
            return "🤖 AI features are currently unavailable. Please use /info for company information or /help for available commands."
        else:
            return "🤖 AI xususiyatlari hozircha mavjud emas. Kompaniya ma'lumotlari uchun /info yoki yordam uchun /help dan foydalaning."

    try:
        # Language-specific instructions - default to Uzbek
        if user_language == "english":
            language_instruction = "The user has explicitly requested English. Respond in English only."
            fallback_message = "🤖 I'm having trouble processing your request right now. Please try again or use /info for company information."
        else:
            language_instruction = "FAQAT o'zbek tilida javob bering. Always respond in Uzbek language only. Do not use English unless explicitly requested."
            fallback_message = "🤖 Hozir so'rovingizni qayta ishlay olmayapman. Iltimos, qayta urinib ko'ring yoki kompaniya ma'lumotlari uchun /info dan foydalaning."

        # Create context with company information
        system_prompt = f"""You are an AI assistant for PremiumSoft.uz, a software development company in Uzbekistan.

{get_company_knowledge_base()}

Your role:
- You talk primarily in Uzbek until someone asks for English
- Your name is OptimusPremium
- Your developer is Muhammad Aziz Mamasodikov, Software engineer at PremiumSoft.uz
- Answer questions about PremiumSoft.uz services, team, and capabilities
- Help potential clients understand what the company offers
- Provide technical guidance related to software development
- Be friendly, professional, and knowledgeable
- If asked about something not related to PremiumSoft.uz or software development, politely redirect to company topics
- Always be helpful and encourage potential clients to contact the company
- {language_instruction}

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
        return fallback_message

def handle_lead_collection(chat_id, text, telegram_user, message_thread_id=None, user_language="uzbek"):
    """Handle lead generation conversation flow."""
    user_data = user_states[chat_id]

    # Check for stop commands
    stop_keywords = ['stop', 'bekor', 'bekor qilish', 'cancel', 'quit', 'exit', 'chiqish', 'toxta', 'toxtash']
    if any(keyword in text.lower() for keyword in stop_keywords):
        # Reset user state
        user_states[chat_id] = {'state': UserState.NORMAL}

        if user_language == "english":
            response = """❌ Order process cancelled.

You can start again anytime by sending /order command.

🤝 If you need our services, feel free to contact us!"""
        else:
            response = """❌ Buyurtma jarayoni bekor qilindi.

Istalgan vaqtda /order buyrug'i orqali qaytadan boshlashingiz mumkin.

🤝 Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!"""

        send_telegram_message(chat_id, response, message_thread_id=message_thread_id)
        return

    if user_data['state'] == UserState.COLLECTING_PROJECT:
        user_data['project'] = text
        user_data['state'] = UserState.COLLECTING_NAME
        if user_language == "english":
            response = "Thank you! Now please write your name:\n\n💡 *Tip: You can type 'stop' anytime to cancel*"
        else:
            response = "Rahmat! Endi ismingizni yozing:\n\n💡 *Maslahat: Bekor qilish uchun 'stop' yozing*"
        send_telegram_message(chat_id, response, parse_mode="Markdown", message_thread_id=message_thread_id)

    elif user_data['state'] == UserState.COLLECTING_NAME:
        user_data['name'] = text
        user_data['state'] = UserState.COLLECTING_PHONE
        if user_language == "english":
            response = "Great! Now please write your phone number:\n\n💡 *Tip: You can type 'stop' anytime to cancel*"
        else:
            response = "Yaxshi! Endi telefon raqamingizni yozing:\n\n💡 *Maslahat: Bekor qilish uchun 'stop' yozing*"
        send_telegram_message(chat_id, response, parse_mode="Markdown", message_thread_id=message_thread_id)

    elif user_data['state'] == UserState.COLLECTING_PHONE:
        user_data['phone'] = text
        user_data['state'] = UserState.COLLECTING_EMAIL
        if user_language == "english":
            response = "Excellent! Finally, please write your email address:\n\n💡 *Tip: You can type 'stop' anytime to cancel*"
        else:
            response = "Ajoyib! Oxirida email manzilingizni yozing:\n\n💡 *Maslahat: Bekor qilish uchun 'stop' yozing*"
        send_telegram_message(chat_id, response, parse_mode="Markdown", message_thread_id=message_thread_id)

    elif user_data['state'] == UserState.COLLECTING_EMAIL:
        user_data['email'] = text

        # Send lead to group
        lead_message = format_lead_message(user_data, telegram_user)
        send_to_group(lead_message, TELEGRAM_TOPIC_ID)

        # Reset user state
        user_states[chat_id] = {'state': UserState.NORMAL}

        # Confirm to user in their language
        if user_language == "english":
            response = """✅ Thank you! Your information has been successfully sent. We will contact you soon!

📞 Our team will reach out within 24 hours to discuss your project.

🤝 If you need our services, feel free to contact us!"""
        else:
            response = """✅ Rahmat! Ma'lumotlaringiz muvaffaqiyatli yuborildi. Tez orada siz bilan bog'lanamiz!

📞 Bizning jamoa 24 soat ichida loyihangizni muhokama qilish uchun siz bilan bog'lanadi.

🤝 Agar bizning xizmatlarimizga muhtoj bo'lsangiz, biz bilan bog'lanishdan tortinmang!"""

        send_telegram_message(chat_id, response, message_thread_id=message_thread_id)

def start_lead_collection(chat_id, message_thread_id=None, user_language="uzbek"):
    """Start the lead collection process - Default to Uzbek."""
    user_states[chat_id] = {
        'state': UserState.COLLECTING_PROJECT,
        'project': '',
        'name': '',
        'phone': '',
        'email': ''
    }

    # Always default to Uzbek unless explicitly English
    if user_language == "english":
        response = """Great! Please provide detailed information about your project:
• What service do you need?
• What is the project goal?
• What features should it have?"""
    else:
        # Default to Uzbek
        response = """Ajoyib! Sizning loyihangiz haqida batafsil ma'lumot bering:
• Qanday xizmat kerak?
• Loyiha maqsadi nima?
• Qanday funksiyalar bo'lishi kerak?

💡 *Ingliz tilida javob olish uchun "inglizcha" deb yozing*"""

    send_telegram_message(chat_id, response, message_thread_id=message_thread_id)

def handle_message(message):
    """Handle a message from Telegram."""
    chat_id = message.get('chat', {}).get('id')
    chat_type = message.get('chat', {}).get('type', 'private')
    text = message.get('text', '')
    user_name = message.get('from', {}).get('first_name', 'Foydalanuvchi')
    telegram_user = message.get('from', {})

    # Extract topic/thread information
    message_thread_id = message.get('message_thread_id')

    if not chat_id:
        logger.error("Message missing chat_id")
        return

    # Check if this is a reply to the bot
    is_reply = is_reply_to_bot(message)

    # Group behavior control - respond if mentioned, is a reply to bot, or in private chat
    if is_group_chat(chat_type) and not is_bot_mentioned(text) and not is_reply:
        logger.info(f"Ignoring group message without mention or reply: {text}")
        return

    logger.info(f"Received message from {chat_id}: {text}" + (f" in thread {message_thread_id}" if message_thread_id else ""))

    # Clean command text (remove @botusername)
    clean_text = clean_command_text(text)

    # Detect user's language
    user_language = detect_language(clean_text)
    logger.info(f"Detected language: {user_language}")

    # Handle lead generation states
    if chat_id in user_states and user_states[chat_id]['state'] != UserState.NORMAL:
        handle_lead_collection(chat_id, clean_text, telegram_user, message_thread_id, user_language)
        return

    # Handle /start command - Default to Uzbek
    if clean_text == '/start':
        # Always start with Uzbek unless explicitly requested English
        if user_language == "english" and ("english" in clean_text.lower() or "ingliz" in clean_text.lower()):
            ai_status = "🤖 AI Chat: ✅ Available" if groq_client else "🤖 AI Chat: ❌ Unavailable"
            welcome_text = f"""👋 Hello {user_name}!

Welcome to PremiumSoft.uz AI-powered Info Bot!

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
• /ai - AI chat status
• /order - Place an order"""
        else:
            # Default to Uzbek for all users
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
• /order - Buyurtma berish

💡 *Ingliz tilida javob olish uchun "inglizcha" yoki "english" deb yozing*"""

        response_with_cta = add_cta_to_message(welcome_text)
        send_telegram_message(chat_id, response_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle /info command - Default to Uzbek
    elif clean_text == '/info':
        # Only use English if explicitly requested
        if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
            info_text = get_premiumsoft_info_english()
        else:
            # Default to Uzbek
            info_text = get_premiumsoft_info()
        info_with_cta = add_cta_to_message(info_text)
        send_telegram_message(chat_id, info_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle /help command - Default to Uzbek
    elif clean_text == '/help':
        # Only use English if explicitly requested
        if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
            ai_status = "✅ Available - Just ask me anything!" if groq_client else "❌ Currently unavailable"
            help_text = f"""
🤖 *PremiumSoft.uz AI Info Bot*

*Available commands:*
/start - Start the bot and see welcome message
/info - Get detailed company information
/help - Show this help message
/ai - Check AI chat status
/order - Start order process
/hours - Check business hours
/location - Get our location

*AI Chat:* {ai_status}

💬 *How to use:*
Just type any question about PremiumSoft.uz and I'll answer using AI!

*Quick actions:*
• Type "location" to get our address
• Type "hello" for a greeting
• Type "thanks" to express gratitude

*Examples:*
• "Tell me about your mobile development services"
• "Who are your team members?"
• "What technologies do you use?"
• "How can you help my startup?"
            """
        else:
            ai_status = "✅ Mavjud - Biror narsa so'rang!" if groq_client else "❌ Hozircha mavjud emas"
            help_text = f"""
🤖 *PremiumSoft.uz AI Ma'lumot Bot*

*Mavjud buyruqlar:*
/start - Botni ishga tushirish va xush kelibsiz xabarini ko'rish
/info - Kompaniya haqida batafsil ma'lumot
/help - Ushbu yordam xabarini ko'rsatish
/ai - AI suhbat holatini tekshirish
/order - Buyurtma berish jarayonini boshlash
/hours - Ish vaqtini tekshirish
/location - Bizning manzilimizni olish

*AI Suhbat:* {ai_status}

💬 *Qanday foydalanish:*
PremiumSoft.uz haqida biror savol yozing va men AI yordamida javob beraman!

*Tezkor harakatlar:*
• "manzil" yozing - bizning manzilimizni olish uchun
• "salom" yozing - salomlashish uchun
• "rahmat" yozing - minnatdorchilik bildirish uchun

*Misollar:*
• "Mobil dasturlash xizmatlaringiz haqida gapirib bering"
• "Jamoa a'zolaringiz kimlar?"
• "Qanday texnologiyalardan foydalanasiz?"
• "Mening startupimga qanday yordam bera olasiz?"
            """
        help_with_cta = add_cta_to_message(help_text.strip())
        send_telegram_message(chat_id, help_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle /order command
    elif clean_text == '/order' or 'buyurtma' in clean_text.lower() or 'order' in clean_text.lower():
        start_lead_collection(chat_id, message_thread_id, user_language)

    # Handle /hours command
    elif clean_text == '/hours' or clean_text == '/vaqt':
        business_hours_msg = get_business_hours_message(user_language)

        if is_business_hours():
            if user_language == "english":
                hours_text = f"🟢 *We're currently ONLINE!*{business_hours_msg}\n\n📞 Contact us now for immediate assistance!"
            else:
                hours_text = f"🟢 *Hozir ONLAYNMIZ!*{business_hours_msg}\n\n📞 Darhol yordam olish uchun biz bilan bog'laning!"
        else:
            if user_language == "english":
                hours_text = f"🔴 *We're currently OFFLINE*{business_hours_msg}\n\n📧 Send us a message and we'll respond during business hours!"
            else:
                hours_text = f"🔴 *Hozir OFFLAYNMIZ*{business_hours_msg}\n\n📧 Xabar yuboring, ish vaqtida javob beramiz!"

        hours_with_cta = add_cta_to_message(hours_text)
        send_telegram_message(chat_id, hours_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle /location command
    elif clean_text == '/location' or clean_text == '/manzil':
        send_telegram_location(chat_id, 40.391014, 71.773127, message_thread_id)

        if user_language == "english":
            location_text = """📍 *PremiumSoft.uz Location*

🏢 Address: Fergana, Ahmad Al-Fergani Shah Street, 53, 4th floor
📞 Phone: +998 73 244 05 35
🏛️ Authority: Fergana Regional Administration
📧 Email: info@premiumsoft.uz
🌐 Website: https://premiumsoft.uz"""
        else:
            location_text = """📍 *PremiumSoft.uz Manzili*

🏢 Manzil: Fargʻona, Ahmad Al-Fargʻoniy shoh koʻchasi, 53, 4-qavat
📞 Telefon: +998 73 244 05 35
🏛️ Vakolat: Farg'ona viloyati hokimligi
📧 Email: info@premiumsoft.uz
🌐 Veb-sayt: https://premiumsoft.uz"""

        location_with_cta = add_cta_to_message(location_text)
        send_telegram_message(chat_id, location_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle /ai command - Default to Uzbek
    elif clean_text == '/ai':
        # Only use English if explicitly requested
        if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
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
• "Tell me about Muhammadaziz"
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
        else:
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
        send_telegram_message(chat_id, ai_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)

    # Handle all other messages with AI
    else:
        # Check for location requests
        location_keywords = ['location', 'manzil', 'address', 'joylashuv', 'where', 'qayerda', 'qayer']
        if any(keyword in clean_text.lower() for keyword in location_keywords):
            # Send PremiumSoft location (Ahmad Al-Fergani coordinates)
            # Ahmad Al-Fergani Street, Fergana coordinates: 40.391014, 71.773127
            send_telegram_location(chat_id, 40.391014, 71.773127, message_thread_id)

            if user_language == "english":
                location_text = """📍 *PremiumSoft.uz Location*

🏢 Address: Fergana, Ahmad Al-Fergani Shah Street, 53, 4th floor
📞 Phone: +998 73 244 05 35
🏛️ Authority: Fergana Regional Administration
📧 Email: info@premiumsoft.uz
🌐 Website: https://premiumsoft.uz"""
            else:
                location_text = """📍 *PremiumSoft.uz Manzili*

🏢 Manzil: Fargʻona, Ahmad Al-Fargʻoniy shoh koʻchasi, 53, 4-qavat
📞 Telefon: +998 73 244 05 35
🏛️ Vakolat: Farg'ona viloyati hokimligi
📧 Email: info@premiumsoft.uz
🌐 Veb-sayt: https://premiumsoft.uz"""

            location_with_cta = add_cta_to_message(location_text)
            send_telegram_message(chat_id, location_with_cta, parse_mode="Markdown", message_thread_id=message_thread_id)
            return

        # Check for greeting messages - Default to Uzbek
        greeting_keywords = ['salom', 'hello', 'hi', 'assalomu alaykum', 'good morning', 'good day', 'xayrli']
        if any(keyword in clean_text.lower() for keyword in greeting_keywords):
            # Only use English if explicitly requested
            if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
                greeting_response = f"Hello {user_name}! 👋 Welcome to PremiumSoft.uz! How can I help you today?"
            else:
                # Default to Uzbek
                greeting_response = f"Salom {user_name}! 👋 PremiumSoft.uz ga xush kelibsiz! Bugun sizga qanday yordam bera olaman?"

            greeting_with_cta = add_cta_to_message(greeting_response)
            send_telegram_message(chat_id, greeting_with_cta, message_thread_id=message_thread_id)
            return

        # Check for thanks messages - Default to Uzbek
        thanks_keywords = ['rahmat', 'thank', 'thanks', 'tashakkur', 'grateful']
        if any(keyword in clean_text.lower() for keyword in thanks_keywords):
            # Only use English if explicitly requested
            if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
                thanks_response = f"You're welcome, {user_name}! 😊 Is there anything else I can help you with?"
            else:
                # Default to Uzbek
                thanks_response = f"Arzimaydi, {user_name}! 😊 Yana biror narsada yordam bera olamanmi?"

            thanks_with_cta = add_cta_to_message(thanks_response)
            send_telegram_message(chat_id, thanks_with_cta, message_thread_id=message_thread_id)
            return

        # Check if it's a command we don't recognize - Default to Uzbek
        if clean_text.startswith('/'):
            # Only use English if explicitly requested
            if user_language == "english" and ("english" in text.lower() or "ingliz" in text.lower()):
                response_text = f"❓ Unknown command: {clean_text}\n\nUse /help to see available commands or just ask me anything about PremiumSoft.uz!"
            else:
                # Default to Uzbek
                response_text = f"❓ Noma'lum buyruq: {clean_text}\n\nMavjud buyruqlarni ko'rish uchun /help dan foydalaning yoki PremiumSoft.uz haqida biror narsa so'rang!"
            response_with_cta = add_cta_to_message(response_text)
            send_telegram_message(chat_id, response_with_cta, message_thread_id=message_thread_id)
        else:
            # Check for service interest keywords
            service_keywords = [
                'xizmat', 'service', 'loyiha', 'project', 'dastur', 'app', 'sayt', 'website',
                'mobil', 'mobile', 'bot', 'dizayn', 'design', 'ishlab chiqish', 'development',
                'kerak', 'need', 'qilish', 'make', 'yaratish', 'create', 'buyurtma', 'order',
                'price', 'narx', 'cost', 'qancha', 'how much', 'budget'
            ]

            if any(keyword in clean_text.lower() for keyword in service_keywords):
                # Show typing indicator
                send_typing_action(chat_id, message_thread_id)

                # Trigger lead collection for service inquiries
                ai_response = get_ai_response(clean_text, user_name, user_language)
                ai_with_cta = add_cta_to_message(ai_response)

                # Add business hours info if outside business hours
                if not is_business_hours():
                    business_hours_msg = get_business_hours_message(user_language)
                    ai_with_cta += business_hours_msg

                # Consolidate order prompt into the main response
                order_prompt = get_order_prompt(user_language)
                consolidated_response = ai_with_cta + order_prompt

                send_telegram_message(chat_id, consolidated_response, message_thread_id=message_thread_id)
            else:
                # Show typing indicator for AI processing
                send_typing_action(chat_id, message_thread_id)

                # Use AI to respond to the message
                logger.info(f"Processing AI request from {user_name}: {clean_text}")
                ai_response = get_ai_response(clean_text, user_name, user_language)
                ai_with_cta = add_cta_to_message(ai_response)

                # Track user stats
                user_stats = get_user_stats(chat_id)

                # Add personalized touch for frequent users
                if user_stats.get('message_count', 0) > 5:
                    if user_language == "english":
                        ai_with_cta += f"\n\n💫 *Thanks for being an active user, {user_name}!*"
                    else:
                        ai_with_cta += f"\n\n💫 *Faol foydalanuvchi bo'lganingiz uchun rahmat, {user_name}!*"

                send_telegram_message(chat_id, ai_with_cta, message_thread_id=message_thread_id)

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
