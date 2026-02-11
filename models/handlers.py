import os, logging, traceback, aiohttp
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.db import transaction
from django.core.files.base import ContentFile
from .models import Vacancy, Candidate, MediaStorage, BotErrorLog
from .utils import QUESTIONS, validate_input, get_choice_keyboard

logger = logging.getLogger('bot_logger')
router = Router()

class Interview(StatesGroup):
    answering = State()

def parse_tg_link(link: str):
    try:
        parts = link.strip().split('/')
        msg_id = int(parts[-1])
        chat_part = parts[-2]
        chat_id = int(f"-100{chat_part}") if chat_part.isdigit() else f"@{chat_part}"
        return chat_id, msg_id
    except: return None, None

async def send_media_by_key(bot: Bot, user_id: int, key: str):
    media = await sync_to_async(lambda: MediaStorage.objects.filter(key=key).first())()
    if media and media.link:
        chat_id, msg_id = parse_tg_link(media.link)
        if chat_id and msg_id:
            try: return await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=msg_id)
            except: pass
    return False

async def report_error(bot: Bot, user: types.User, error: Exception, step: int = 0):
    admin_id = os.getenv("ADMIN_ID")
    tb = traceback.format_exc()
    await sync_to_async(BotErrorLog.objects.create)(
        user_id=user.id, error_type=type(error).__name__, message=str(error), stack_trace=tb
    )
    msg = f"🚨 <b>BOT ERROR</b>\n👤 {user.full_name}\n📍 Step: {step}\n❌ {str(error)}"
    try: await bot.send_message(admin_id, msg, parse_mode="HTML")
    except: pass

async def download_tg_file(bot: Bot, file_id: str):
    try:
        file = await bot.get_file(file_id)
        url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return ContentFile(await resp.read(), name=os.path.basename(file.file_path))
    except: pass
    return None

@sync_to_async
def sync_save_candidate(u_id, v_id, ans, video_content=None, voice_content=None):
    with transaction.atomic():
        vac = Vacancy.objects.get(id=v_id)
        cand = Candidate.objects.create(
            user_id=u_id, vacancy=vac, answers=ans,
            full_name=ans.get('full_name', ''), phone=ans.get('phone', ''),
            video_note_id=ans.get('video_intro'), voice_id=ans.get('family_audio')
        )
        if video_content: cand.video_note_file.save(video_content.name, video_content, save=False)
        if voice_content: cand.voice_file.save(voice_content.name, voice_content, save=False)
        cand.save()
        return cand

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    try:
        await state.clear()
        await send_media_by_key(bot, message.chat.id, "start")
        vacs = await sync_to_async(list)(Vacancy.objects.filter(is_active=True).only('id', 'title'))
        if not vacs: return await bot.send_message(message.chat.id, "Hozircha bo'sh vakansiyalar yo'q.")
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=v.title, callback_data=f"v_{v.id}")] for v in vacs])
        await bot.send_message(message.chat.id, "<b>Carwon HR botiga xush kelibsiz.</b>\n\nVakansiyani tanlang:", reply_markup=kb, parse_mode="HTML")
    except Exception as e: await report_error(bot, message.from_user, e, step=0)


@router.callback_query(F.data.startswith("v_"))
async def start_survey(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    v_id = int(call.data.split("_")[1])
    vacancy = await sync_to_async(Vacancy.objects.get)(id=v_id)
    await state.update_data(v_id=v_id)
    text = (
        f"📋 <b>{vacancy.title}</b>\n\n"
        f"{vacancy.description if vacancy.description else 'Ushbu vakansiya boʻyicha maʼlumot kiritilmagan.'}\n\n"
        f"<i>Agar shartlar ma'qul bo'lsa, anketani to'ldirishni boshlang:</i>"
    )
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🚀 Anketani boshlash", callback_data="start_questions")]
    ])
    await bot.send_message(call.message.chat.id, text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "start_questions")
async def start_questions_handler(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(step=0, answers={})
    await bot.send_message(call.message.chat.id, QUESTIONS[0]["text"])
    await state.set_state(Interview.answering)
    await call.answer()

@router.callback_query(Interview.answering, F.data.startswith("choice_"))
async def handle_choice(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    val = call.data.replace("choice_", "")
    mock_msg = types.Message(message_id=call.message.message_id, date=call.message.date, chat=call.message.chat, from_user=call.from_user, text=val)
    await handle_interview(mock_msg, state, bot)
    await call.answer()

@router.message(Interview.answering)
async def handle_interview(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data(); step = data.get('step', 0); chat_id = message.chat.id
    try:
        is_valid, err = validate_input(step, message)
        if not is_valid: return await bot.send_message(chat_id, f"❌ {err}")

        answers = data.get('answers', {}); q = QUESTIONS[step]
        val = message.video_note.file_id if message.video_note else (message.voice.file_id if message.voice else (message.audio.file_id if message.audio else message.text))
        answers[q["key"]] = val

        next_step = step + 1
        if q["key"] == "has_experience" and val == "Yo'q":
            next_step = step + 4

        if next_step < len(QUESTIONS):
            await state.update_data(answers=answers, step=next_step); next_q = QUESTIONS[next_step]
            if "media_key" in next_q:
                await send_media_by_key(bot, chat_id, next_q["media_key"])
                if next_q["type"] in ["video_note", "audio"]: return
            if next_q.get("type") == "choice":
                await bot.send_message(chat_id, next_q["text"], reply_markup=get_choice_keyboard(next_q["choices"]))
            else: await bot.send_message(chat_id, next_q["text"])
        else:
            video_c = await download_tg_file(bot, answers.get('video_intro')) if answers.get('video_intro') else None
            voice_c = await download_tg_file(bot, answers.get('family_audio')) if answers.get('family_audio') else None
            cand = await sync_save_candidate(message.from_user.id, data['v_id'], answers, video_c, voice_c)
            await bot.send_message(chat_id, "✅ Arizangiz muvaffaqiyatli qabul qilindi!")
            base_url = os.getenv("SITE_URL", "http://127.0.0.1:8000").rstrip('/')
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Webda ko'rish 🌐", url=f"{base_url}/candidate/{cand.id}/")]])
            await bot.send_message(os.getenv("ADMIN_ID"), f"🆕 <b>Yangi nomzod!</b>\n👤 {cand.full_name}\n💼 {cand.vacancy.title}", reply_markup=kb, parse_mode="HTML")
            await state.clear()
    except Exception as e:
        await report_error(bot, message.from_user, e, step)
        await bot.send_message(chat_id, "⚠️ Texnik xatolik yuz berdi.")