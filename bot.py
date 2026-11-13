import asyncio
import json
import logging
import os
import random
import re
import sys

# Ensure script dir is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

import db
from helpers import cyr_to_lat, lat_to_cyr, split_message, t

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Paths and Config
BOT_TOKEN = "9003885248:AAGRC7WY6iyr7AV9L0qgCyGLf5mBJo6cUDY"
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BOT_DIR, "bot_data.json")

# APP_DIR for images: check local images folder first, fallback to ../histology-exam
if os.path.exists(os.path.join(BOT_DIR, "images")):
    APP_DIR = BOT_DIR
else:
    APP_DIR = os.path.abspath(os.path.join(BOT_DIR, "..", "histology-exam"))

# Load Data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    BOT_DATA = json.load(f)

QUESTIONS = {q["id"]: q for q in BOT_DATA.get("questions", [])}
CASES = {c["id"]: c for c in BOT_DATA.get("cases", [])}
PREPARATIONS = {p["id"]: p for p in BOT_DATA.get("preparations", [])}
SCHEMES = {s["id"]: s for s in BOT_DATA.get("schemes", [])}

# Initialize Database
db.init_db()

# Initialize Bot & Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Keyboards
def get_main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text=t("btn_questions", lang)),
            KeyboardButton(text=t("btn_cases", lang)),
        ],
        [
            KeyboardButton(text=t("btn_preps", lang)),
            KeyboardButton(text=t("btn_schemes", lang)),
        ],
        [
            KeyboardButton(text=t("btn_sim", lang)),
            KeyboardButton(text=t("btn_search", lang)),
        ],
        [
            KeyboardButton(text=t("btn_lang", lang)),
            KeyboardButton(text=t("btn_help", lang)),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_lang_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha (Lotin)", callback_data="set_lang:uz"),
            ],
            [
                InlineKeyboardButton(text="🇺🇿 Ўзбекча (Кирилл)", callback_data="set_lang:uz_cyr"),
            ],
            [
                InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="set_lang:ru"),
            ],
        ]
    )

def localize_txt(text: str, lang: str) -> str:
    if not text:
        return ""
    if lang == "uz_cyr":
        return lat_to_cyr(text)
    elif lang == "uz":
        return cyr_to_lat(text)
    return text

# -------------------------------------------------------------
# COMMAND HANDLERS
# -------------------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = db.get_user_lang(user_id)
    db.set_user_lang(
        user_id,
        lang,
        message.from_user.username or "",
        message.from_user.first_name or "",
    )
    await message.answer(
        t("welcome", lang),
        reply_markup=get_main_menu(lang),
        parse_mode=ParseMode.HTML,
    )

@dp.message(Command("til"))
async def cmd_til(message: Message):
    await message.answer(
        "🌐 <b>Iltimos, o'zingizga qulay tilni tanlang / Пожалуйста, выберите язык:</b>",
        reply_markup=get_lang_inline_kb(),
        parse_mode=ParseMode.HTML,
    )

@dp.message(Command("yordam"))
@dp.message(Command("help"))
async def cmd_help(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await message.answer(
        t("help_text", lang),
        parse_mode=ParseMode.HTML,
    )

@dp.message(Command("savol"))
async def cmd_savol(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        qid = int(args[1])
        if qid in QUESTIONS:
            await send_question(message.chat.id, qid, lang=lang)
            return
    await send_question(message.chat.id, random.choice(list(QUESTIONS.keys())), lang=lang)

@dp.message(Command("masala"))
async def cmd_masala(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        cid = int(args[1])
        if cid in CASES:
            await send_case(message.chat.id, cid, lang=lang)
            return
    await send_case(message.chat.id, random.choice(list(CASES.keys())), lang=lang)

@dp.message(Command("preparat"))
async def cmd_preparat(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        pid = int(args[1])
        if pid in PREPARATIONS:
            await send_preparation(message.chat.id, pid, lang=lang)
            return
    await send_preparation(message.chat.id, random.choice(list(PREPARATIONS.keys())), lang=lang)

@dp.message(Command("sxema"))
async def cmd_sxema(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sid = int(args[1])
        if sid in SCHEMES:
            await send_scheme(message.chat.id, sid, lang=lang)
            return
    await send_scheme(message.chat.id, random.choice(list(SCHEMES.keys())), lang=lang)

@dp.message(Command("bilet"))
async def cmd_bilet(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await generate_ticket(message.chat.id, lang=lang)

# -------------------------------------------------------------
# MENU BUTTON HANDLERS
# -------------------------------------------------------------
@dp.message(F.text.contains("Nazariy") | F.text.contains("Назарий") | F.text.contains("Теоретические"))
async def menu_questions(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    qid = random.choice(list(QUESTIONS.keys()))
    await send_question(message.chat.id, qid, lang=lang)

@dp.message(F.text.contains("Vaziyatli") | F.text.contains("Вазиятли") | F.text.contains("Ситуационные"))
async def menu_cases(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    cid = random.choice(list(CASES.keys()))
    await send_case(message.chat.id, cid, lang=lang)

@dp.message(F.text.contains("Preparat") | F.text.contains("Препарат"))
async def menu_preparations(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    pid = random.choice(list(PREPARATIONS.keys()))
    await send_preparation(message.chat.id, pid, lang=lang)

@dp.message(F.text.contains("Sxema") | F.text.contains("Схема"))
async def menu_schemes(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    sid = random.choice(list(SCHEMES.keys()))
    await send_scheme(message.chat.id, sid, lang=lang)

@dp.message(F.text.contains("trenajyor") | F.text.contains("тренажёр") | F.text.contains("тренажер"))
async def menu_sim(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await generate_ticket(message.chat.id, lang=lang)

@dp.message(F.text.contains("Qidiruv") | F.text.contains("Қидирув") | F.text.contains("Поиск"))
async def menu_search(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await message.answer(t("search_prompt", lang), parse_mode=ParseMode.HTML)

@dp.message(F.text.contains("Tilni") | F.text.contains("Тилни") | F.text.contains("Выбор языка"))
async def menu_lang(message: Message):
    await cmd_til(message)

@dp.message(F.text.contains("Yordam") | F.text.contains("Ёрдам") | F.text.contains("Справка"))
async def menu_help(message: Message):
    await cmd_help(message)

# -------------------------------------------------------------
# 1. NAZARIY SAVOLLAR (QUESTIONS)
# -------------------------------------------------------------
def get_question_kb(qid: int, show_answer: bool, lang: str) -> InlineKeyboardMarkup:
    total = len(QUESTIONS)
    prev_id = total if qid <= 1 else qid - 1
    next_id = 1 if qid >= total else qid + 1

    ans_btn = InlineKeyboardButton(
        text=t("hide_answer", lang) if show_answer else t("show_answer", lang),
        callback_data=f"q_ans:{qid}:{0 if show_answer else 1}",
    )
    nav_row = [
        InlineKeyboardButton(text=t("prev_btn", lang), callback_data=f"q_nav:{prev_id}"),
        InlineKeyboardButton(text=f"🎲 {t('random_btn', lang)}", callback_data="q_rand"),
        InlineKeyboardButton(text=t("next_btn", lang), callback_data=f"q_nav:{next_id}"),
    ]
    tools_row = [
        InlineKeyboardButton(text=f"📑 {t('list_btn', lang)} (1-111)", callback_data="q_list:1"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[ans_btn], nav_row, tools_row])

async def send_question(chat_id: int, qid: int, show_answer: bool = False, message_to_edit: Message = None, lang: str = "uz"):
    q = QUESTIONS.get(qid)
    if not q:
        return

    q_text = q.get("question_uz") if lang == "uz" else q.get("question")
    if not q_text:
        q_text = q.get("question", "")
    q_text = localize_txt(q_text, lang)

    cat = localize_txt(q.get("category", ""), lang)
    ans_text = localize_txt(q.get("answer_clean", ""), lang)

    msg_text = f"📚 <b>{t('btn_questions', lang).split()[0]} #{q['id']} / {len(QUESTIONS)}</b>\n"
    if cat:
        msg_text += f"🏷️ <i>{cat}</i>\n\n"
    else:
        msg_text += "\n"

    msg_text += f"❓ <b>{q_text}</b>\n"

    if show_answer and ans_text:
        msg_text += f"\n━━━━━━━━━━━━━━━━━━━━\n💡 <b>{t('show_answer', lang).split()[-1]}:</b>\n\n{ans_text}"

    kb = get_question_kb(qid, show_answer, lang)

    # Chunk if message is longer than 4000
    chunks = split_message(msg_text, limit=3900)
    if message_to_edit:
        try:
            if len(chunks) == 1:
                await message_to_edit.edit_text(chunks[0], reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                await message_to_edit.edit_text(chunks[0], parse_mode=ParseMode.HTML)
                for chunk in chunks[1:-1]:
                    await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
                await bot.send_message(chat_id, chunks[-1], reply_markup=kb, parse_mode=ParseMode.HTML)
            return
        except Exception as e:
            logging.debug(f"Edit question fallback: {e}")

    if len(chunks) == 1:
        await bot.send_message(chat_id, chunks[0], reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        for chunk in chunks[:-1]:
            await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id, chunks[-1], reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 2. VAZIYATLI MASALALAR (CASES)
# -------------------------------------------------------------
def get_case_kb(cid: int, show_solution: bool, lang: str) -> InlineKeyboardMarkup:
    total = len(CASES)
    prev_id = total if cid <= 1 else cid - 1
    next_id = 1 if cid >= total else cid + 1

    sol_btn = InlineKeyboardButton(
        text=t("hide_answer", lang) if show_solution else t("show_solution", lang),
        callback_data=f"c_sol:{cid}:{0 if show_solution else 1}",
    )
    nav_row = [
        InlineKeyboardButton(text=t("prev_btn", lang), callback_data=f"c_nav:{prev_id}"),
        InlineKeyboardButton(text=f"🎲 {t('random_btn', lang)}", callback_data="c_rand"),
        InlineKeyboardButton(text=t("next_btn", lang), callback_data=f"c_nav:{next_id}"),
    ]
    tools_row = [
        InlineKeyboardButton(text=f"📑 {t('list_btn', lang)} (1-85)", callback_data="c_list:1"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[sol_btn], nav_row, tools_row])

async def send_case(chat_id: int, cid: int, show_solution: bool = False, message_to_edit: Message = None, lang: str = "uz"):
    c = CASES.get(cid)
    if not c:
        return

    title = c.get("title_uz") if lang == "uz" else c.get("title")
    title = localize_txt(title or c.get("title", ""), lang)

    text = c.get("case_text_uz") if lang == "uz" else c.get("case_text")
    text = localize_txt(text or c.get("case_text", ""), lang)

    sub_q = c.get("sub_questions", [])
    solution = localize_txt(c.get("solution_clean", ""), lang)

    msg_text = f"🩺 <b>{t('btn_cases', lang).split()[0]} #{c['id']} / {len(CASES)}</b>\n"
    msg_text += f"📌 <b>{title}</b>\n\n"
    msg_text += f"📋 <i>Klinik vaziyat:</i>\n{text}\n"

    if sub_q:
        msg_text += "\n❓ <b>Savollar:</b>\n"
        for sq in sub_q:
            msg_text += f"• {localize_txt(sq, lang)}\n"

    if show_solution and solution:
        msg_text += f"\n━━━━━━━━━━━━━━━━━━━━\n💡 <b>{t('show_solution', lang)}:</b>\n\n{solution}"

    kb = get_case_kb(cid, show_solution, lang)

    chunks = split_message(msg_text, limit=3900)
    if message_to_edit:
        try:
            if len(chunks) == 1:
                await message_to_edit.edit_text(chunks[0], reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                await message_to_edit.edit_text(chunks[0], parse_mode=ParseMode.HTML)
                for chunk in chunks[1:-1]:
                    await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
                await bot.send_message(chat_id, chunks[-1], reply_markup=kb, parse_mode=ParseMode.HTML)
            return
        except Exception as e:
            logging.debug(f"Edit case fallback: {e}")

    if len(chunks) == 1:
        await bot.send_message(chat_id, chunks[0], reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        for chunk in chunks[:-1]:
            await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id, chunks[-1], reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 3. MIKROSKOPIK PREPARATLAR (PREPARATIONS)
# -------------------------------------------------------------
def get_prep_kb(pid: int, mode: str, show_layers: bool, show_qa: bool, lang: str) -> InlineKeyboardMarkup:
    total = len(PREPARATIONS)
    prev_id = total if pid <= 1 else pid - 1
    next_id = 1 if pid >= total else pid + 1

    toggle_mode = "atlas" if mode == "micro" else "micro"
    toggle_text = t("show_atlas", lang) if mode == "micro" else t("show_micro", lang)

    row1 = [
        InlineKeyboardButton(text=toggle_text, callback_data=f"p_mode:{pid}:{toggle_mode}"),
        InlineKeyboardButton(text=f"📝 {t('show_layers', lang)}", callback_data=f"p_layers:{pid}"),
    ]
    row2 = [
        InlineKeyboardButton(text=f"❓ {t('show_exam_qa', lang)}", callback_data=f"p_qa:{pid}"),
        InlineKeyboardButton(text=f"🎲 {t('random_btn', lang)}", callback_data="p_rand"),
    ]
    row3 = [
        InlineKeyboardButton(text=t("prev_btn", lang), callback_data=f"p_nav:{prev_id}:{mode}"),
        InlineKeyboardButton(text=t("next_btn", lang), callback_data=f"p_nav:{next_id}:{mode}"),
    ]
    row4 = [
        InlineKeyboardButton(text=f"📑 {t('list_btn', lang)} (1-51)", callback_data="p_list:1"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])

async def send_preparation(chat_id: int, pid: int, mode: str = "micro", lang: str = "uz"):
    p = PREPARATIONS.get(pid)
    if not p:
        return

    name = localize_txt(p.get("name", ""), lang)
    lat_name = p.get("name_lat", "")
    stain = localize_txt(p.get("staining", ""), lang)
    diag = localize_txt(p.get("diagnostic_key", ""), lang)

    # Choose image
    img_rel = p.get("micro_image") if mode == "micro" else p.get("atlas_image")
    img_path = os.path.join(APP_DIR, img_rel)

    caption = f"🔬 <b>{t('btn_preps', lang).split()[0]} #{p['id']} / {len(PREPARATIONS)}</b>\n"
    caption += f"🧫 <b>{name}</b>\n"
    if lat_name:
        caption += f"🏛️ <i>{lat_name}</i>\n"
    if stain:
        caption += f"🎨 <b>Bo'yash:</b> {stain}\n"
    if diag:
        caption += f"🔍 <b>Diagnostika belgisi:</b> {diag}\n"

    mode_label = "🔬 Haqiqiy mikroskop fotosurati" if mode == "micro" else "📖 O'quv atlas diagrammasi"
    caption += f"\n<i>Ko'rinish: {mode_label}</i>"

    kb = get_prep_kb(pid, mode, False, False, lang)

    if os.path.exists(img_path):
        photo = FSInputFile(img_path)
        await bot.send_photo(chat_id, photo, caption=caption[:1020], reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id, caption, reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 4. SXEMALAR VA DIAGRAMMALAR (SCHEMES) - 83 TA
# -------------------------------------------------------------
def get_scheme_kb(sid: int, show_answer: bool, lang: str) -> InlineKeyboardMarkup:
    total = len(SCHEMES)
    prev_id = total if sid <= 1 else sid - 1
    next_id = 1 if sid >= total else sid + 1

    ans_btn = InlineKeyboardButton(
        text=t("hide_answer", lang) if show_answer else t("show_structures", lang),
        callback_data=f"s_ans:{sid}:{0 if show_answer else 1}",
    )
    nav_row = [
        InlineKeyboardButton(text=t("prev_btn", lang), callback_data=f"s_nav:{prev_id}"),
        InlineKeyboardButton(text=f"🎲 {t('random_btn', lang)}", callback_data="s_rand"),
        InlineKeyboardButton(text=t("next_btn", lang), callback_data=f"s_nav:{next_id}"),
    ]
    tools_row = [
        InlineKeyboardButton(text=f"📑 {t('list_btn', lang)} (1-83)", callback_data="s_list:1"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[ans_btn], nav_row, tools_row])

async def send_scheme(chat_id: int, sid: int, show_answer: bool = False, lang: str = "uz"):
    s = SCHEMES.get(sid)
    if not s:
        return

    title = s.get("title_uz") if lang == "uz" else s.get("title_cyr")
    title = localize_txt(title or s.get("title", ""), lang)

    question = s.get("question_uz") if lang == "uz" else s.get("question_cyr")
    question = localize_txt(question or s.get("question", ""), lang)

    cat = localize_txt(s.get("category", ""), lang)

    img_rel = s.get("image", f"images/schemes/image{sid}.png")
    img_path = os.path.join(APP_DIR, img_rel)

    caption = f"📊 <b>{t('btn_schemes', lang).split()[0]} #{s['id']} / {len(SCHEMES)}</b>\n"
    if cat:
        caption += f"🏷️ <i>{cat}</i>\n"
    caption += f"📌 <b>{title}</b>\n\n"
    caption += f"🎯 <b>Topshiriq:</b> {question}\n"

    kb = get_scheme_kb(sid, show_answer, lang)

    if not show_answer:
        caption += "\n💡 <i>Sxemadagi 1, 2, 3... raqamlarni aniqlang va javobni tekshirish uchun quyidagi tugmani bosing.</i>"

    if os.path.exists(img_path):
        photo = FSInputFile(img_path)
        await bot.send_photo(chat_id, photo, caption=caption[:1020], reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id, caption, reply_markup=kb, parse_mode=ParseMode.HTML)

    if show_answer:
        ans = s.get("answer_uz_clean") if lang == "uz" else s.get("answer_cyr_clean")
        ans = localize_txt(ans or s.get("answer_clean", ""), lang)
        ans_msg = f"🎯 <b>#{sid}. {title} — {t('show_structures', lang)}:</b>\n\n{ans}"
        chunks = split_message(ans_msg, limit=3900)
        for chunk in chunks:
            await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 5. IMTIHON TRENAJYORI (EXAM SIMULATOR)
# -------------------------------------------------------------
async def generate_ticket(chat_id: int, lang: str = "uz"):
    ticket_id = random.randint(100, 999)
    q_id = random.choice(list(QUESTIONS.keys()))
    c_id = random.choice(list(CASES.keys()))
    p_id = random.choice(list(PREPARATIONS.keys()))
    s_id = random.choice(list(SCHEMES.keys()))

    q = QUESTIONS[q_id]
    c = CASES[c_id]
    p = PREPARATIONS[p_id]
    s = SCHEMES[s_id]

    q_title = localize_txt(q.get("question_uz") if lang == "uz" else q.get("question", ""), lang)
    c_title = localize_txt(c.get("title_uz") if lang == "uz" else c.get("title", ""), lang)
    p_title = localize_txt(p.get("name", ""), lang)
    s_title = localize_txt(s.get("title_uz") if lang == "uz" else s.get("title", ""), lang)

    text = f"🎯 <b>GISTOLOGIYA OG'ZAKI IMTIHON BILETI #{ticket_id}</b>\n"
    text += f"<i>Haqiqiy imtihon talablari asosida 4 ta topshiriq:</i>\n\n"
    text += f"1️⃣ <b>Nazariy savol #{q_id}:</b>\n{q_title}\n\n"
    text += f"2️⃣ <b>Vaziyatli masala #{c_id}:</b>\n{c_title}\n\n"
    text += f"3️⃣ <b>Mikroskopik preparat #{p_id}:</b>\n{p_title} ({p.get('name_lat', '')})\n\n"
    text += f"4️⃣ <b>Imtihon sxemasi #{s_id}:</b>\n{s_title}\n\n"
    text += "👇 <i>Har bir topshiriqni ochish va javoblarini tekshirish uchun quyidagi tugmalardan foydalaning:</i>"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"1️⃣ Savolni ochish (#{q_id})", callback_data=f"q_nav:{q_id}"),
            ],
            [
                InlineKeyboardButton(text=f"2️⃣ Masalani ochish (#{c_id})", callback_data=f"c_nav:{c_id}"),
            ],
            [
                InlineKeyboardButton(text=f"3️⃣ Preparatni ochish (#{p_id})", callback_data=f"p_nav:{p_id}:micro"),
            ],
            [
                InlineKeyboardButton(text=f"4️⃣ Sxemani ochish (#{s_id})", callback_data=f"s_nav:{s_id}"),
            ],
            [
                InlineKeyboardButton(text="🎲 Yangi bilet yaratish", callback_data="sim_new"),
            ],
        ]
    )

    await bot.send_message(chat_id, text, reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 6. CALLBACK QUERY ROUTER
# -------------------------------------------------------------
@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    lang = db.get_user_lang(user_id)
    chat_id = callback.message.chat.id

    try:
        if data.startswith("set_lang:"):
            new_lang = data.split(":")[1]
            db.set_user_lang(user_id, new_lang, callback.from_user.username or "", callback.from_user.first_name or "")
            await callback.answer("Til o'zgartirildi! / Язык изменён!")
            await callback.message.answer(
                t("welcome", new_lang),
                reply_markup=get_main_menu(new_lang),
                parse_mode=ParseMode.HTML,
            )
            return

        # Questions
        if data.startswith("q_ans:"):
            _, qid, show = data.split(":")
            await callback.answer()
            await send_question(chat_id, int(qid), show_answer=(show == "1"), message_to_edit=callback.message, lang=lang)
            return

        if data.startswith("q_nav:"):
            qid = int(data.split(":")[1])
            await callback.answer()
            await send_question(chat_id, qid, show_answer=False, message_to_edit=callback.message, lang=lang)
            return

        if data == "q_rand":
            qid = random.choice(list(QUESTIONS.keys()))
            await callback.answer()
            await send_question(chat_id, qid, show_answer=False, message_to_edit=callback.message, lang=lang)
            return

        if data.startswith("q_list:"):
            page = int(data.split(":")[1])
            await callback.answer()
            await show_list_page(callback.message, "q", page, len(QUESTIONS), lang)
            return

        # Cases
        if data.startswith("c_sol:"):
            _, cid, show = data.split(":")
            await callback.answer()
            await send_case(chat_id, int(cid), show_solution=(show == "1"), message_to_edit=callback.message, lang=lang)
            return

        if data.startswith("c_nav:"):
            cid = int(data.split(":")[1])
            await callback.answer()
            await send_case(chat_id, cid, show_solution=False, message_to_edit=callback.message, lang=lang)
            return

        if data == "c_rand":
            cid = random.choice(list(CASES.keys()))
            await callback.answer()
            await send_case(chat_id, cid, show_solution=False, message_to_edit=callback.message, lang=lang)
            return

        if data.startswith("c_list:"):
            page = int(data.split(":")[1])
            await callback.answer()
            await show_list_page(callback.message, "c", page, len(CASES), lang)
            return

        # Preparations
        if data.startswith("p_mode:"):
            _, pid, mode = data.split(":")
            await callback.answer()
            await send_preparation(chat_id, int(pid), mode=mode, lang=lang)
            return

        if data.startswith("p_nav:"):
            parts = data.split(":")
            pid = int(parts[1])
            mode = parts[2] if len(parts) > 2 else "micro"
            await callback.answer()
            await send_preparation(chat_id, pid, mode=mode, lang=lang)
            return

        if data == "p_rand":
            pid = random.choice(list(PREPARATIONS.keys()))
            await callback.answer()
            await send_preparation(chat_id, pid, mode="micro", lang=lang)
            return

        if data.startswith("p_layers:"):
            pid = int(data.split(":")[1])
            p = PREPARATIONS.get(pid)
            await callback.answer()
            if p:
                layers = localize_txt(p.get("layers", ""), lang)
                desc = localize_txt(p.get("atlas_desc", ""), lang)
                msg = f"📝 <b>#{pid}. {p.get('name', '')} — {t('show_layers', lang)}:</b>\n\n{layers}"
                if desc:
                    msg += f"\n\n📖 <i>Atlas tavsifi:</i>\n{desc}"
                chunks = split_message(msg, limit=3900)
                for chunk in chunks:
                    await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
            return

        if data.startswith("p_qa:"):
            pid = int(data.split(":")[1])
            p = PREPARATIONS.get(pid)
            await callback.answer()
            if p:
                qa = localize_txt(p.get("exam_questions", ""), lang)
                msg = f"❓ <b>#{pid}. {p.get('name', '')} — {t('show_exam_qa', lang)}:</b>\n\n{qa}"
                chunks = split_message(msg, limit=3900)
                for chunk in chunks:
                    await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
            return

        if data.startswith("p_list:"):
            page = int(data.split(":")[1])
            await callback.answer()
            await show_list_page(callback.message, "p", page, len(PREPARATIONS), lang)
            return

        # Schemes
        if data.startswith("s_ans:"):
            _, sid, show = data.split(":")
            await callback.answer()
            if show == "1":
                s = SCHEMES.get(int(sid))
                if s:
                    ans = s.get("answer_uz_clean") if lang == "uz" else s.get("answer_cyr_clean")
                    ans = localize_txt(ans or s.get("answer_clean", ""), lang)
                    title = localize_txt(s.get("title_uz") or s.get("title", ""), lang)
                    msg = f"🎯 <b>#{sid}. {title} — {t('show_structures', lang)}:</b>\n\n{ans}"
                    chunks = split_message(msg, limit=3900)
                    for chunk in chunks:
                        await bot.send_message(chat_id, chunk, parse_mode=ParseMode.HTML)
            return

        if data.startswith("s_nav:"):
            sid = int(data.split(":")[1])
            await callback.answer()
            await send_scheme(chat_id, sid, show_answer=False, lang=lang)
            return

        if data == "s_rand":
            sid = random.choice(list(SCHEMES.keys()))
            await callback.answer()
            await send_scheme(chat_id, sid, show_answer=False, lang=lang)
            return

        if data.startswith("s_list:"):
            page = int(data.split(":")[1])
            await callback.answer()
            await show_list_page(callback.message, "s", page, len(SCHEMES), lang)
            return

        if data == "sim_new":
            await callback.answer()
            await generate_ticket(chat_id, lang=lang)
            return

    except Exception as e:
        logging.error(f"Error handling callback {data}: {e}", exc_info=True)
        await callback.answer("Xatolik yuz berdi.", show_alert=False)

# -------------------------------------------------------------
# 7. LIST PAGINATION HELPER
# -------------------------------------------------------------
async def show_list_page(message: Message, item_type: str, page: int, total_items: int, lang: str):
    per_page = 15
    total_pages = (total_items + per_page - 1) // per_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page + 1
    end_idx = min(page * per_page, total_items)

    type_titles = {
        "q": "📚 Nazariy savollar ro'yxati",
        "c": "🩺 Vaziyatli masalalar ro'yxati",
        "p": "🔬 Mikroskopik preparatlar ro'yxati",
        "s": "📊 Sxemalar ro'yxati",
    }
    title = localize_txt(type_titles.get(item_type, "Ro'yxat"), lang)

    text = f"📑 <b>{title}</b>\n<i>Sahifa: {page} / {total_pages} ({start_idx} - {end_idx})</i>\n\n"
    text += "Kerakli raqamni bosing:"

    keyboard = []
    # 5 buttons per row
    row = []
    for num in range(start_idx, end_idx + 1):
        row.append(InlineKeyboardButton(text=f"{num}", callback_data=f"{item_type}_nav:{num}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Nav row
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi 15", callback_data=f"{item_type}_list:{page - 1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Keyingi 15 ➡️", callback_data=f"{item_type}_list:{page + 1}"))
    if nav_row:
        keyboard.append(nav_row)

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    try:
        await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# 8. TEXT SEARCH HANDLER
# -------------------------------------------------------------
@dp.message()
async def handle_search_query(message: Message):
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return

    lang = db.get_user_lang(message.from_user.id)
    query = text.lower()

    # Search in Questions
    q_matches = []
    for q in QUESTIONS.values():
        haystack = f"{q.get('question', '')} {q.get('question_uz', '')} {q.get('keywords', '')}".lower()
        if query in haystack:
            q_matches.append(q)

    # Search in Cases
    c_matches = []
    for c in CASES.values():
        haystack = f"{c.get('title', '')} {c.get('title_uz', '')} {c.get('case_text', '')}".lower()
        if query in haystack:
            c_matches.append(c)

    # Search in Preparations
    p_matches = []
    for p in PREPARATIONS.values():
        haystack = f"{p.get('name', '')} {p.get('name_lat', '')} {p.get('diagnostic_key', '')}".lower()
        if query in haystack:
            p_matches.append(p)

    # Search in Schemes
    s_matches = []
    for s in SCHEMES.values():
        haystack = f"{s.get('title', '')} {s.get('title_uz', '')} {s.get('question', '')} {s.get('category', '')}".lower()
        if query in haystack:
            s_matches.append(s)

    total_matches = len(q_matches) + len(c_matches) + len(p_matches) + len(s_matches)

    if total_matches == 0:
        await message.answer(
            t("search_empty", lang).format(query=text),
            parse_mode=ParseMode.HTML,
        )
        return

    res_text = t("search_results", lang).format(query=text)
    buttons = []

    if q_matches:
        res_text += f"\n📚 <b>Nazariy savollar ({len(q_matches)} ta):</b>\n"
        for q in q_matches[:4]:
            q_title = localize_txt(q.get("question_uz") or q.get("question", ""), lang)[:60]
            res_text += f"• #{q['id']}. {q_title}...\n"
            buttons.append([InlineKeyboardButton(text=f"📚 Savol #{q['id']}", callback_data=f"q_nav:{q['id']}")])

    if c_matches:
        res_text += f"\n🩺 <b>Vaziyatli masalalar ({len(c_matches)} ta):</b>\n"
        for c in c_matches[:3]:
            c_title = localize_txt(c.get("title_uz") or c.get("title", ""), lang)[:60]
            res_text += f"• #{c['id']}. {c_title}...\n"
            buttons.append([InlineKeyboardButton(text=f"🩺 Masala #{c['id']}", callback_data=f"c_nav:{c['id']}")])

    if p_matches:
        res_text += f"\n🔬 <b>Mikroskopik preparatlar ({len(p_matches)} ta):</b>\n"
        for p in p_matches[:3]:
            p_title = localize_txt(p.get("name", ""), lang)[:60]
            res_text += f"• #{p['id']}. {p_title} ({p.get('name_lat', '')})\n"
            buttons.append([InlineKeyboardButton(text=f"🔬 Preparat #{p['id']}", callback_data=f"p_nav:{p['id']}:micro")])

    if s_matches:
        res_text += f"\n📊 <b>Sxemalar ({len(s_matches)} ta):</b>\n"
        for s in s_matches[:3]:
            s_title = localize_txt(s.get("title_uz") or s.get("title", ""), lang)[:60]
            res_text += f"• #{s['id']}. {s_title}...\n"
            buttons.append([InlineKeyboardButton(text=f"📊 Sxema #{s['id']}", callback_data=f"s_nav:{s['id']}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer(res_text, reply_markup=kb, parse_mode=ParseMode.HTML)

# -------------------------------------------------------------
# MAIN RUNNER
# -------------------------------------------------------------
async def main():
    logging.info("Starting Gistologiya Telegram Bot (@Gistalogiya_bot)...")
    # Delete webhook to ensure polling works cleanly
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
