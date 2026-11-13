import re

CYR_TO_LAT = {
    'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo', 'Ж': 'J', 'ж': 'j', 'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i', 'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f', 'Х': 'X', 'х': 'x', 'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Sh', 'щ': 'sh',
    'Ъ': "'", 'ъ': "'", 'Ь': "", 'ь': "", 'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya', 'я': 'ya',
    'Ў': "O'", 'ў': "o'", 'Қ': 'Q', 'қ': 'q', 'Ғ': "G'", 'ғ': "g'",
    'Ҳ': 'H', 'ҳ': 'h'
}

def cyr_to_lat(text: str) -> str:
    if not text:
        return ""
    # Compound checks
    t = text
    t = re.sub(r'\bЕ', 'Ye', t)
    t = re.sub(r'\bе', 'ye', t)
    res = []
    for char in t:
        res.append(CYR_TO_LAT.get(char, char))
    return ''.join(res)

LAT_TO_CYR_COMPOUND = [
    ("O'", "Ў"), ("o'", "ў"), ("O`", "Ў"), ("o`", "ў"), ("Oʻ", "Ў"), ("oʻ", "ў"),
    ("G'", "Ғ"), ("g'", "ғ"), ("G`", "Ғ"), ("g`", "ғ"), ("Gʻ", "Ғ"), ("gʻ", "ғ"),
    ("Sh", "Ш"), ("SH", "Ш"), ("sh", "ш"),
    ("Ch", "Ч"), ("CH", "Ч"), ("ch", "ч"),
    ("Yo", "Ё"), ("YO", "Ё"), ("yo", "ё"),
    ("Yu", "Ю"), ("YU", "Ю"), ("yu", "ю"),
    ("Ya", "Я"), ("YA", "Я"), ("ya", "я"),
    ("Ts", "Ц"), ("TS", "Ц"), ("ts", "ц"),
    ("Ye", "Е"), ("YE", "Е"), ("ye", "е"),
]

LAT_TO_CYR_SINGLE = {
    'A': 'А', 'a': 'а', 'B': 'Б', 'b': 'б', 'D': 'Д', 'd': 'д',
    'E': 'Э', 'e': 'е', 'F': 'Ф', 'f': 'ф', 'G': 'Г', 'g': 'г',
    'H': 'Ҳ', 'h': 'ҳ', 'I': 'И', 'i': 'и', 'J': 'Ж', 'j': 'ж',
    'K': 'К', 'k': 'к', 'L': 'Л', 'l': 'л', 'M': 'М', 'm': 'м',
    'N': 'Н', 'n': 'н', 'O': 'О', 'o': 'о', 'P': 'П', 'p': 'п',
    'Q': 'Қ', 'q': 'қ', 'R': 'Р', 'r': 'р', 'S': 'С', 's': 'с',
    'T': 'Т', 't': 'т', 'U': 'У', 'u': 'у', 'V': 'В', 'v': 'в',
    'X': 'Х', 'x': 'х', 'Y': 'Й', 'y': 'й', 'Z': 'З', 'z': 'з'
}

def lat_to_cyr(text: str) -> str:
    if not text:
        return ""
    t = text
    for lat, cyr in LAT_TO_CYR_COMPOUND:
        t = t.replace(lat, cyr)
    res = []
    for char in t:
        res.append(LAT_TO_CYR_SINGLE.get(char, char))
    return ''.join(res)

def split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    lines = text.split('\n')
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > limit:
            if current:
                parts.append(current)
                current = ""
            if len(line) > limit:
                # hard split long line
                for i in range(0, len(line), limit):
                    parts.append(line[i:i+limit])
            else:
                current = line
        else:
            if current:
                current += "\n" + line
            else:
                current = line
    if current:
        parts.append(current)
    return parts

# Multilingual UI Dictionary
STRINGS = {
    "uz": {
        "welcome": "🔬 <b>Gistologiya Og'zaki Imtihon Botiga xush kelibsiz!</b>\n\nUshbu bot tibbiyot OTMlari talabalari uchun gistologiya, sitologiya va embriologiya fanidan og'zaki imtihonga mukammal tayyorlanish uchun ishlab chiqilgan.\n\n👇 <b>Quyidagi menyudan kerakli bo'limni tanlang:</b>",
        "btn_questions": "📚 Nazariy savollar (111)",
        "btn_cases": "🩺 Vaziyatli masalalar (85)",
        "btn_preps": "🔬 Preparatlar (51)",
        "btn_schemes": "📊 Sxemalar (83)",
        "btn_sim": "🎯 Imtihon trenajyori",
        "btn_search": "🔍 Qidiruv",
        "btn_lang": "🌐 Tilni tanlash",
        "btn_help": "ℹ️ Yordam va Qo'llanma",
        "show_answer": "👁️ Javobni ko'rish",
        "hide_answer": "🙈 Javobni yashirish",
        "show_solution": "💡 Masala yechimini ko'rish",
        "show_structures": "🎯 Tuzilmalar javobini ko'rish",
        "show_layers": "📝 Qatlamlar va tuzilishi",
        "show_exam_qa": "❓ Imtihon savol-javoblari",
        "show_atlas": "📖 Atlas diagrammasi",
        "show_micro": "🔬 Mikroskop fotosurati",
        "random_btn": "🎲 Tasodifiy",
        "prev_btn": "⬅️ Oldingisi",
        "next_btn": "Keyingisi ➡️",
        "list_btn": "📑 Ro'yxat",
        "menu_btn": "🏠 Asosiy menyu",
        "search_prompt": "🔍 <b>Qidiruv:</b>\n\nIzlamoqchi bo'lgan atama, a'zo yoki mavzu nomini yozib yuboring (masalan: <i>neyron, jigar, epiteliy, nefron, yurak</i>):",
        "search_empty": "❌ Kechirasiz, «{query}» bo'yicha hech qanday ma'lumot topilmadi.",
        "search_results": "🔍 <b>«{query}» bo'yicha topilgan natijalar:</b>\n",
        "ticket_title": "🎯 <b>IMTIHON BILETI #{id}</b>\n\nO'zingizni sinab ko'ring! Bilet 4 ta topshiriqdan iborat:",
        "ticket_q": "1️⃣ <b>Nazariy savol #{id}:</b>\n{text}",
        "ticket_c": "2️⃣ <b>Vaziyatli masala #{id}:</b>\n{text}",
        "ticket_p": "3️⃣ <b>Mikroskopik preparat #{id}:</b>\n{text}",
        "ticket_s": "4️⃣ <b>Imtihon sxemasi #{id}:</b>\n{text}",
        "help_text": "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n• <b>📚 Nazariy savollar:</b> 111 ta rasmiy imtihon savollari va ularning akademik batafsil javoblari.\n• <b>🩺 Vaziyatli masalalar:</b> 85 ta klinik vaziyatlar va qadamma-qadam yechimlari.\n• <b>🔬 Preparatlar:</b> 51 ta preparatning mikroskop ostidagi haqiqiy fotosuratlari, atlas diagrammalari va diagnostika belgilari.\n• <b>📊 Sxemalar:</b> 83 ta rasmiy imtihon diagrammalari va raqamlangan tuzilmalar tahlili.\n• <b>🎯 Trenajyor:</b> Haqiqiy imtihondagidek tasodifiy bilet yaratib o'z bilimingizni sinab ko'rish.\n• <b>🔍 Qidiruv:</b> Botga to'g'ridan-to'g'ri istalgan atamani yozib yuboring.\n\n<b>Tezkor buyruqlar:</b>\n/start - Botni qayta ishga tushirish\n/savol [1-111] - Masalan: /savol 12\n/masala [1-85] - Masalan: /masala 5\n/preparat [1-51] - Masalan: /preparat 1\n/sxema [1-83] - Masalan: /sxema 7\n/bilet - Tasodifiy imtihon bileti\n/til - Tilni o'zgartirish"
    },
    "uz_cyr": {
        "welcome": "🔬 <b>Гистология Оғзаки Имтиҳон Ботига хуш келибсиз!</b>\n\nУшбу бот тиббиёт ОТМлари талабалари учун гистология, цитология ва эмбриология фанидан оғзаки имтиҳонга мукаммал тайёрланиш учун ишлаб чиқилган.\n\n👇 <b>Қуйидаги менюдан керакли бўлимни танланг:</b>",
        "btn_questions": "📚 Назарий саволлар (111)",
        "btn_cases": "🩺 Вазиятли масалалар (85)",
        "btn_preps": "🔬 Препаратлар (51)",
        "btn_schemes": "📊 Схемалар (83)",
        "btn_sim": "🎯 Имтиҳон тренажёри",
        "btn_search": "🔍 Қидирув",
        "btn_lang": "🌐 Тилни танлаш",
        "btn_help": "ℹ️ Ёрдам ва Қўлланма",
        "show_answer": "👁️ Жавобни кўриш",
        "hide_answer": "🙈 Жавобни яшириш",
        "show_solution": "💡 Масала ечимини кўриш",
        "show_structures": "🎯 Тузилмалар жавобини кўриш",
        "show_layers": "📝 Қатламлар ва тузилиши",
        "show_exam_qa": "❓ Имтиҳон савол-жавоблари",
        "show_atlas": "📖 Атлас диаграммаси",
        "show_micro": "🔬 Микроскоп фотосурати",
        "random_btn": "🎲 Тасодифий",
        "prev_btn": "⬅️ Олдингиси",
        "next_btn": "Кейингиси ➡️",
        "list_btn": "📑 Рўйхат",
        "menu_btn": "🏠 Асосий меню",
        "search_prompt": "🔍 <b>Қидирув:</b>\n\nИзламоқчи бўлган атама, аъзо ёки мавзу номини ёзиб юборинг (масалан: <i>нейрон, жигар, эпителий, нефрон, юрак</i>):",
        "search_empty": "❌ Кечирасиз, «{query}» бўйича ҳеч қандай маълумот топилмади.",
        "search_results": "🔍 <b>«{query}» бўйича топилган натижалар:</b>\n",
        "ticket_title": "🎯 <b>ИМТИҲОН БИЛЕТИ #{id}</b>\n\nЎзингизни синаб кўринг! Билет 4 та топшириқдан иборат:",
        "ticket_q": "1️⃣ <b>Назарий савол #{id}:</b>\n{text}",
        "ticket_c": "2️⃣ <b>Вазиятли масала #{id}:</b>\n{text}",
        "ticket_p": "3️⃣ <b>Микроскопик препарат #{id}:</b>\n{text}",
        "ticket_s": "4️⃣ <b>Имтиҳон схемаси #{id}:</b>\n{text}",
        "help_text": "📖 <b>Ботдан фойдаланиш бўйича қўлланма:</b>\n\n• <b>📚 Назарий саволлар:</b> 111 та расмий имтиҳон саволлари ва академик жавоблар.\n• <b>🩺 Вазиятли масалалар:</b> 85 та клиник вазият ва ечимлари.\n• <b>🔬 Препаратлар:</b> 51 та микроскопик препаратнинг асл фотосуратлари, атлас расмлари ва белгилари.\n• <b>📊 Схемалар:</b> 83 та имтиҳон схемаси ва рақамланган тузилмалари.\n• <b>🎯 Тренажёр:</b> Тасодифий тўлиқ имтиҳон билети.\n• <b>🔍 Қидирув:</b> Исталган атама бўйича қидирув."
    },
    "ru": {
        "welcome": "🔬 <b>Добро пожаловать в бот устного экзамена по Гистологии!</b>\n\nБот разработан для студентов медицинских ВУЗов для полноценной подготовки к устному экзамену по гистологии, цитологии и эмбриологии.\n\n👇 <b>Выберите раздел в меню ниже:</b>",
        "btn_questions": "📚 Теоретические вопросы (111)",
        "btn_cases": "🩺 Ситуационные задачи (85)",
        "btn_preps": "🔬 Препараты (51)",
        "btn_schemes": "📊 Схемы и диаграммы (83)",
        "btn_sim": "🎯 Экзаменационный тренажёр",
        "btn_search": "🔍 Поиск",
        "btn_lang": "🌐 Выбор языка",
        "btn_help": "ℹ️ Справка и помощь",
        "show_answer": "👁️ Показать ответ",
        "hide_answer": "🙈 Скрыть ответ",
        "show_solution": "💡 Показать решение задачи",
        "show_structures": "🎯 Показать структуры схемы",
        "show_layers": "📝 Слои и строение",
        "show_exam_qa": "❓ Экзаменационные вопросы",
        "show_atlas": "📖 Схема атласа",
        "show_micro": "🔬 Микрофотография",
        "random_btn": "🎲 Случайный",
        "prev_btn": "⬅️ Назад",
        "next_btn": "Вперёд ➡️",
        "list_btn": "📑 Список",
        "menu_btn": "🏠 Главное меню",
        "search_prompt": "🔍 <b>Поиск:</b>\n\nОтправьте название термина, органа или темы (например: <i>нейрон, печень, эпителий, нефрон, сердце</i>):",
        "search_empty": "❌ По запросу «{query}» ничего не найдено.",
        "search_results": "🔍 <b>Результаты поиска по запросу «{query}»:</b>\n",
        "ticket_title": "🎯 <b>ЭКЗАМЕНАЦИОННЫЙ БИЛЕТ #{id}</b>\n\nПроверьте свои знания! Билет состоит из 4 заданий:",
        "ticket_q": "1️⃣ <b>Теоретический вопрос #{id}:</b>\n{text}",
        "ticket_c": "2️⃣ <b>Ситуационная задача #{id}:</b>\n{text}",
        "ticket_p": "3️⃣ <b>Микропрепарат #{id}:</b>\n{text}",
        "ticket_s": "4️⃣ <b>Экзаменационная схема #{id}:</b>\n{text}",
        "help_text": "📖 <b>Руководство по использованию:</b>\n\n• <b>📚 Теоретические вопросы:</b> 111 официальных экзаменационных вопросов с ответами.\n• <b>🩺 Ситуационные задачи:</b> 85 клинических задач с подробными решениями.\n• <b>🔬 Препараты:</b> 51 микропрепарат с реальными микрофотографиями и атласом.\n• <b>📊 Схемы:</b> 83 официальные экзаменационные схемы с обозначением структур.\n• <b>🎯 Тренажёр:</b> Генерация случайного экзаменационного билета.\n• <b>🔍 Поиск:</b> Мгновенный поиск по любой теме или термину."
    }
}

def t(key: str, lang: str = "uz") -> str:
    lang_dict = STRINGS.get(lang, STRINGS["uz"])
    return lang_dict.get(key, STRINGS["uz"].get(key, key))
