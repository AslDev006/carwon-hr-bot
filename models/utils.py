import re, logging
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger('bot_logger')

QUESTIONS = [
    {"text": "Ism va familiyangizni to'liq kiriting:", "type": "name", "key": "full_name"},
    {"text": "Telefon raqamingizni yuboring (+998XXXXXXXXX):", "type": "phone", "key": "phone"},
    {"text": "Yashash manzilingiz (Shahar, Tuman):", "type": "text", "key": "address", "min": 10},
    {"text": "Tug‘ilgan kuningiz (dd.mm.yyyy):", "type": "date", "key": "birth_date"},
    {"text": "Oilaviy ahvolingiz:", "type": "choice", "key": "marital", "choices": ["Oila qurgan", "Ajrashgan", "Oila qurmagan"]},
    {"text": "Video topshiriq yuklanmoqda...", "type": "video_note", "key": "video_intro", "media_key": "video_message"},
    {"text": "Ma’lumotingiz darajasi:", "type": "choice", "key": "edu", "choices": ["Oliy", "O‘rta maxsus", "O‘rta"]},
    {"text": "Qaysi o‘quv yurtini tamomlagansiz?", "type": "text", "key": "edu_place", "min": 5},
    {"text": "Audio topshiriq yuklanmoqda...", "type": "audio", "key": "family_audio", "media_key": "voice_message"},
    {"text": "Avval biror joyda ishlaganmisiz?", "type": "choice", "key": "has_experience", "choices": ["Ha", "Yo'q"]},
    {"text": "Oldingi ish joyingizdan bo‘shash sababingiz nima?", "type": "text", "key": "leave_reason", "min": 5},
    {"text": "Sobiq rahbaringizdan tavsiya olishga rozimisiz?", "type": "choice", "key": "rec_consent", "choices": ["Ha", "Yo'q"]},
    {"text": "Tavsiya beruvchi shaxsning ismi va telefoni:", "type": "text", "key": "recommender", "min": 10},
    {"text": "Mutaxassisligingiz bo‘yicha qo‘shimcha kurslar:", "type": "text", "key": "extra_courses", "min": 3},
    {"text": "Rus tilini bilish darajangiz:", "type": "choice", "key": "lang_ru", "choices": ["A'lo", "Yaxshi", "Past", "Bilmayman"]},
    {"text": "Ingliz tilini bilish darajangiz:", "type": "choice", "key": "lang_en", "choices": ["A'lo", "Yaxshi", "Past", "Bilmayman"]},
    {"text": "Qaysi professional dasturlarda ishlay olasiz?", "type": "text", "key": "software_skills", "min": 3},
    {"text": "Yaxshi xodimda bo‘lishi kerak bo‘lgan 3 ta sifat:", "type": "text", "key": "qualities", "min": 10},
    {"text": "Hayotingizdagi eng katta yutug‘ingiz?", "type": "text", "key": "achievement", "min": 10},
    {"text": "Ishda qiyin vaziyatda kimga murojaat qilasiz?", "type": "text", "key": "support", "min": 3},
    {"text": "Nima uchun ba'zi odamlar ishga kech qoladi?", "type": "text", "key": "lateness", "min": 10},
    {"text": "Rahbar nohaq tanbeh bersa, nima qilasiz?", "type": "text", "key": "reprimand", "min": 10},
    {"text": "Jamoada ishlash yoqadimi yoki yakka?", "type": "choice", "key": "team_solo", "choices": ["Jamoada", "Yakka"]},
    {"text": "Kompaniya haqida qayerdan bildingiz?", "type": "text", "key": "source", "min": 4},
    {"text": "Bizda sizni nima ko‘proq qiziqtirdi?", "type": "text", "key": "interest", "min": 10},
    {"text": "Ko'p topshiriq berilsa, qanday bajarasiz?", "type": "text", "key": "multitask", "min": 10},
    {"text": "Sinov muddatida oldingi maoshingiz?", "type": "text", "key": "sal_prob", "min": 4},
    {"text": "Asosiy davrda qancha maosh olgansiz?", "type": "text", "key": "sal_main", "min": 4},
    {"text": "Qo‘shimcha ishlashga (overtime) tayyormisiz?", "type": "choice", "key": "overtime", "choices": ["Tayyorman", "Yo'q"]},
    {"text": "Sizni nima motivatsiyadan tushirishi mumkin?", "type": "text", "key": "demotivation", "min": 10},
    {"text": "Ishdagi halollik va sadoqat nima?", "type": "text", "key": "loyalty", "min": 10},
    {"text": "Ish boshlash uchun necha kun kerak?", "type": "text", "key": "start_days", "min": 1},
    {"text": "Bizga berishni xohlagan savolingiz bormi?", "type": "text", "key": "questions", "min": 2},
    {"text": "Telegram Username (@username):", "type": "text", "key": "tg_user", "min": 3},
    {"text": "Ma'lumotlar to'g'riligini tasdiqlaysizmi?", "type": "choice", "key": "final", "choices": ["Tasdiqlayman", "Tahrirlash"]}
]

def get_choice_keyboard(choices):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=str(c), callback_data=f"choice_{c}")] for c in choices])

def validate_input(step_idx, message):
    q = QUESTIONS[step_idx]
    val = message.text or ""
    try:
        if q["type"] == "name":
            if len(val.split()) < 2 or not all(x.isalpha() for x in "".join(val.split())): return False, "F.I.SH to'liq va faqat harflardan bo'lsin."
        elif q["type"] == "phone":
            if not re.match(r"^\+998\d{9}$", val.replace(" ", "")): return False, "Format: +998901234567"
        elif q["type"] == "date":
            dt = datetime.strptime(val, "%d.%m.%Y")
            if not (1960 < dt.year < 2010): return False, "Sana mantiqsiz."
        elif q["type"] == "video_note":
            if not message.video_note: return False, "Iltimos, aylana video yuboring."
        elif q["type"] == "audio":
            if not (message.voice or message.audio): return False, "Ovozli xabar yuboring."
        elif q["type"] == "text":
            if len(val) < q.get("min", 2): return False, "Javob juda qisqa."
        return True, ""
    except: return False, "Format noto'g'ri."