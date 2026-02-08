import re
import logging
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger('bot_logger')

# 35 ta savol to'plami
QUESTIONS = [
    {"text": "Ism va familiyangizni to'liq kiriting (Masalan: Alisher Navoiy):", "type": "name", "key": "full_name"},
    {"text": "Telefon raqamingizni yuboring (Masalan: +998901234567):", "type": "phone", "key": "phone"},
    {"text": "Yashash manzilingiz (Shahar, Tuman, Ko'cha):", "type": "text", "key": "address", "min": 10},
    {"text": "Tug‘ilgan kuningiz (dd.mm.yyyy formatida):", "type": "date", "key": "birth_date"},
    {"text": "Oilaviy ahvolingiz:", "type": "choice", "key": "marital",
     "choices": ["Oila qurgan", "Ajrashgan", "Oila qurmagan"]},

    # 6-savol (Video): Matn o'rniga Media yuboriladi
    {"text": "Video topshiriq yuklanmoqda...", "type": "video_note", "key": "video_intro",
     "media_key": "video_message"},

    {"text": "Ma’lumotingiz darajasi:", "type": "choice", "key": "edu", "choices": ["Oliy", "O‘rta maxsus", "O‘rta"]},
    {"text": "Qaysi o‘quv yurtini va qachon tamomlagansiz?", "type": "text", "key": "edu_place", "min": 5},

    # 9-savol (Audio): Matn o'rniga Media yuboriladi
    {"text": "Audio topshiriq yuklanmoqda...", "type": "audio", "key": "family_audio", "media_key": "voice_message"},
    {"text": "Avval biror joyda ishlaganmisiz?", "type": "choice", "key": "has_experience", "choices": ["Ha", "Yo'q"]},
    {"text": "Oldingi ish joyingizdan bo‘shash sababimgiz?", "type": "text", "key": "leave_reason", "min": 5},
    {"text": "Sobiq rahbaringizdan tavsiya olishga rozimisiz?", "type": "choice", "key": "rec_consent",
     "choices": ["Ha", "Yo'q"]},
    {"text": "Tavsiya beruvchi shaxsning ismi va telefoni:", "type": "text", "key": "recommender", "min": 10},
    {"text": "Mutaxassisligingiz bo‘yicha qo‘shimcha kurslar:", "type": "text", "key": "extra_courses", "min": 3},
    {"text": "Rus tilini bilish darajangiz:", "type": "choice", "key": "lang_ru",
     "choices": ["A'lo", "Yaxshi", "Past", "Bilmayman"]},
    {"text": "Ingliz tilini bilish darajangiz:", "type": "choice", "key": "lang_en",
     "choices": ["A'lo", "Yaxshi", "Past", "Bilmayman"]},
    {"text": "Qaysi professional dasturlarda (Excel, CRM) ishlay olasiz?", "type": "text", "key": "software_skills",
     "min": 3},
    {"text": "Yaxshi xodimda bo‘lishi kerak bo‘lgan 3 ta sifat:", "type": "text", "key": "worker_qualities", "min": 10},
    {"text": "Hayotingizdagi eng katta yutug‘ingiz deb nimani hisoblaysiz?", "type": "text", "key": "achievement",
     "min": 10},
    {"text": "Ish jarayonida qiyin vaziyatga tushsangiz, kimga murojaat qilasiz?", "type": "text", "key": "support",
     "min": 3},
    {"text": "Nima uchun ba'zi odamlar ishga kech qoladi? Munosabatingiz:", "type": "text", "key": "lateness_view",
     "min": 10},
    {"text": "Agar rahbaringiz sizga nohaq tanbeh bersa, qanday yo‘l tutasiz?", "type": "text",
     "key": "unfair_reprimand", "min": 10},
    {"text": "Jamoada ishlash yoqadimi yoki yakka tartibdami?", "type": "choice", "key": "team_solo",
     "choices": ["Jamoada", "Yakka tartibda"]},
    {"text": "Bizning kompaniya haqida qayerdan ma'lumot oldingiz?", "type": "text", "key": "source", "min": 4},
    {"text": "Bizning korxonada sizni nima ko‘proq qiziqtirdi?", "type": "text", "key": "interest", "min": 10},
    {"text": "Bir vaqtning o‘zida ko‘p topshiriq berilsa, qanday bajarasiz?", "type": "text", "key": "multitask",
     "min": 10},
    {"text": "Sinov muddatida oldingi ishxonangizda qancha maosh olgansiz?", "type": "text", "key": "salary_probation",
     "min": 4},
    {"text": "Siz oldingi ishxonangizda asosiy davr qancha maosh olgansiz?", "type": "text", "key": "salary_main",
     "min": 4},
    {"text": "Qo‘shimcha ish vaqtlarida (overtime) ishlashga tayyormisiz?", "type": "choice", "key": "overtime",
     "choices": ["Tayyorman", "Yo'q"]},
    {"text": "Sizni nima motivatsiyadan tushirishi (zeriktirishi) mumkin?", "type": "text", "key": "demotivation",
     "min": 10},
    {"text": "Ishdagi halollik va sadoqat siz uchun nima degani?", "type": "text", "key": "loyalty", "min": 10},
    {"text": "Biz ish boshlashimiz uchun sizga necha kun vaqt kerak?", "type": "text", "key": "start_in", "min": 1},
    {"text": "Sizda bizga berishni xohlagan qandaydir savolingiz bormi?", "type": "text", "key": "candidate_question",
     "min": 2},
    {"text": "Telegram Username (Masalan: @username):", "type": "text", "key": "telegram_handle", "min": 3},
    {"text": "Ma'lumotlar to'g'riligini tasdiqlaysizmi?", "type": "choice", "key": "final",
     "choices": ["Tasdiqlayman", "Tahrirlash kerak"]}
]


def get_choice_keyboard(choices):
    """Inline tugmalarni yaratish"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=str(c), callback_data=f"choice_{c}")] for c in choices])


def validate_input(step_idx, message):
    """Deep Verification (Chuqur tekshiruv)"""
    q = QUESTIONS[step_idx]
    val = message.text or ""

    try:
        # 1. Ism-familiya tekshiruvi (Kamida 2 ta so'z va faqat harf)
        if q["type"] == "name":
            parts = val.strip().split()
            if len(parts) < 2: return False, "F.I.SH to'liq bo'lishi kerak (Ism va Familiya)."
            if not all(x.isalpha() for x in "".join(parts)): return False, "Ismda faqat harflar bo'lishi shart."

        # 2. Telefon raqam (+998XXXXXXXXX)
        elif q["type"] == "phone":
            if not re.match(r"^\+998\d{9}$", val.replace(" ", "")):
                return False, "Telefon noto'g'ri. Namuna: +998901234567"

        # 3. Tug'ilgan sana (Haqiqiy sana va mantiqiy yil)
        elif q["type"] == "date":
            dt = datetime.strptime(val, "%d.%m.%Y")
            if not (1960 < dt.year < 2010):
                return False, "Sana mantiqsiz. Haqiqiy tug'ilgan yilingizni kiriting."

        # 4. Aylana video (Video note)
        elif q["type"] == "video_note":
            if not message.video_note: return False, "Iltimos, faqat aylana (video-message) yuboring."
            if message.video_note.duration < 10: return False, "Video juda qisqa. Kamida 10 soniya bo'lsin."

        # 5. Ovozli xabar (Voice)
        elif q["type"] == "audio":
            if not (message.voice or message.audio): return False, "Iltimos, ovozli xabar yoki audio yuboring."
            duration = message.voice.duration if message.voice else message.audio.duration
            if duration < 10: return False, "Ovozli xabar juda qisqa."

        elif q["type"] == "text":
            min_len = q.get("min", 2)
            if len(val) < min_len: return False, f"Javob juda qisqa (Kamida {min_len} belgi)."
            if val.lower() in ["asdasd", "qwerty", "test", "salom", "yo'q"]:
                return False, "Iltimos, mazmunliroq javob bering."

        return True, ""
    except ValueError:
        return False, "Sana formati noto'g'ri (dd.mm.yyyy)."
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        return False, "Ma'lumot noto'g'ri yuborildi."