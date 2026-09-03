import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

DB = "bot.db"

DROP_CHANNEL_ID = 1544750555015155742
DROP_ROLE_NAME = "Дроп"

active_drop = None
drop_task = None

case_open_lock = asyncio.Lock()


items = {
    "🧦 Чулок": {"price": 25, "rarity": "⚪ Обычный"},
    "💾 Ubuntu": {"price": 50, "rarity": "⚪ Обычный"},
    "💾 Debian": {"price": 75, "rarity": "⚪ Обычный"},
    "💾 Fedora": {"price": 100, "rarity": "🟢 Необычный"},
    "💾 Linux Mint": {"price": 125, "rarity": "🟢 Необычный"},
    "💾 Manjaro": {"price": 175, "rarity": "🔵 Редкий"},
    "💾 Arch Linux": {"price": 250, "rarity": "🔵 Редкий"},
    "💾 Gentoo": {"price": 500, "rarity": "🟣 Эпический"},
    "💜 Аметист": {"price": 150, "rarity": "🔵 Редкий"},
    "⚡ Lit Energy": {"price": 75, "rarity": "⚪ Обычный"},
    "⚡ Monster": {"price": 125, "rarity": "🟢 Необычный"},
    "⚡ Red Bull": {"price": 150, "rarity": "🔵 Редкий"},
    "⚡ Burn": {"price": 200, "rarity": "🔵 Редкий"},
    "🎮 Godot": {"price": 125, "rarity": "🟢 Необычный"},
    "🎮 Unity": {"price": 250, "rarity": "🔵 Редкий"},
    "🎮 Unreal Engine": {"price": 500, "rarity": "🟣 Эпический"},
    "🎮 Source Engine": {"price": 750, "rarity": "🟣 Эпический"},
    "🎮 CryEngine": {"price": 1000, "rarity": "🟠 Легендарный"},
    "🦴 Dragonclaw Hook": {"price": 375, "rarity": "🟣 Эпический"},
    "🚜 МТЗ-82": {"price": 250, "rarity": "🟢 Необычный"},
    "🚜 Беларус-1221": {"price": 500, "rarity": "🔵 Редкий"},
    "🚜 John Deere": {"price": 1000, "rarity": "🟣 Эпический"},
    "🚜 Fendt": {"price": 1750, "rarity": "🟠 Легендарный"},
    "🚜 К-700": {"price": 2500, "rarity": "🟠 Легендарный"},
    "🚜 К-744": {"price": 3750, "rarity": "🔴 Артефакт"},
    "🧱 Кирпич из Минска": {"price": 60, "rarity": "⚪ Обычный"},
    "🐸 Жаба": {"price": 300, "rarity": "🔵 Редкий"},
    "🧠 нейрон": {"price": 450, "rarity": "🟣 Эпический"},
    "🔥 Лицензия на огонь": {"price": 900, "rarity": "🟣 Эпический"},
    "💎 Алмазная анальная пробка": {"price": 2250, "rarity": "🟠 Легендарный"},
    "👑 Атом Лёхи Пружины": {"price": 5000, "rarity": "🔴 Артефакт"},
    "📖 26 том магической битвы": {"price": 200, "rarity": "🔵 Редкий"}
}


cases = {
    "🗑️ Мусор дроп": {
        "price": 5,
        "money": (0, 3),
        "weight": 45,
        "item_chance": 0.18,
        "unlock_level": 1,
        "loot": [
            ("🧦 Чулок", 40),
            ("💾 Ubuntu", 10),
            ("💾 Debian", 5),
            ("⚡ Lit Energy", 3)
        ]
    },

    "🥔 Кейс лукашенко": {
        "price": 20,
        "money": (0, 10),
        "weight": 25,
        "item_chance": 0.22,
        "unlock_level": 2,
        "loot": [
            ("🧱 Кирпич из Минска", 40),
            ("⚡ Lit Energy", 20),
            ("⚡ Monster", 15),
            ("🚜 МТЗ-82", 5),
            ("🚜 Беларус-1221", 4),
            ("🚜 John Deere", 1)
        ]
    },

    "🐸 Кейс жаби жаби": {
        "price": 50,
        "money": (1, 20),
        "weight": 16,
        "item_chance": 0.25,
        "unlock_level": 3,
        "loot": [
            ("🐸 Жаба", 38),
            ("💜 Аметист", 27),
            ("⚡ Monster", 20),
            ("⚡ Red Bull", 11),
            ("💾 Fedora", 4)
        ]
    },

    "💀 Кейс головного мозга": {
        "price": 100,
        "money": (2, 35),
        "weight": 8,
        "item_chance": 0.28,
        "unlock_level": 4,
        "loot": [
            ("🧠 нейрон", 39),
            ("🎮 Godot", 27),
            ("💾 Manjaro", 17),
            ("🦴 Dragonclaw Hook", 8),
            ("🎮 Unity", 6),
            ("💾 Arch Linux", 3)
        ]
    },

    "🔥 Хз огонь": {
        "price": 250,
        "money": (5, 80),
        "weight": 4,
        "item_chance": 0.31,
        "unlock_level": 5,
        "loot": [
            ("🔥 Лицензия на огонь", 29),
            ("🎮 Unity", 23),
            ("🎮 Unreal Engine", 19),
            ("🎮 Source Engine", 13),
            ("💾 Arch Linux", 9),
            ("💾 Gentoo", 5),
            ("🎮 CryEngine", 2)
        ]
    },

    "💎 Кейс алмазик": {
        "price": 500,
        "money": (10, 150),
        "weight": 1.5,
        "item_chance": 0.34,
        "unlock_level": 7,
        "loot": [
            ("💎 Алмазная анальная пробка", 25),
            ("🚜 Fendt", 22),
            ("🚜 К-700", 18),
            ("🚜 К-744", 7),
            ("🎮 CryEngine", 12),
            ("🦴 Dragonclaw Hook", 10),
            ("💾 Gentoo", 6)
        ]
    },

    "👑 Кейс Лёхи Пружины": {
        "price": 1000,
        "money": (20, 300),
        "weight": 0.5,
        "item_chance": 0.38,
        "unlock_level": 10,
        "loot": [
            ("👑 Атом Лёхи Пружины", 8),
            ("🚜 К-744", 15),
            ("💎 Алмазная анальная пробка", 20),
            ("🎮 CryEngine", 18),
            ("🦴 Dragonclaw Hook", 17),
            ("💾 Gentoo", 22)
        ]
    }
}


materials = {
    "скрап": {
        "name": "🪨 Скрап",
        "value": 5
    },
    "метал": {
        "name": "🔩 Метал",
        "value": 15
    },
    "мвк": {
        "name": "⚙️ МВК",
        "value": 40
    }
}


hats = {
    "🧢 Кепка разведчика (шапка)": {
        "material": "скрап",
        "weight": 30
    },
    "🪖 Каска инженера (шапка)": {
        "material": "скрап",
        "weight": 25
    },
    "🎖️ Фуражка солдата (шапка)": {
        "material": "скрап",
        "weight": 20
    },
    "🩺 Шапка медика (шапка)": {
        "material": "скрап",
        "weight": 15
    },
    "🕶️ Очки снайпера (шапка)": {
        "material": "скрап",
        "weight": 7
    },
    "🧰 Гаечная корона инженера (шапка)": {
        "material": "скрап",
        "weight": 3
    },

    "🎩 Цилиндр шпиона (шапка)": {
        "material": "метал",
        "weight": 28
    },
    "🥽 Очки подрывника (шапка)": {
        "material": "метал",
        "weight": 23
    },
    "🧢 Кепка медика (шапка)": {
        "material": "метал",
        "weight": 18
    },
    "🪖 Военная каска (шапка)": {
        "material": "метал",
        "weight": 14
    },
    "🤠 Шляпа стрелка (шапка)": {
        "material": "метал",
        "weight": 10
    },
    "💼 Чемодан на голове (шапка)": {
        "material": "метал",
        "weight": 5
    },
    "👑 Корона Mann Co. (шапка)": {
        "material": "метал",
        "weight": 2
    },

    "🧢 Кепка разведчика Deluxe (шапка)": {
        "material": "мвк",
        "weight": 22
    },
    "🪖 Шлем тяжёлого (шапка)": {
        "material": "мвк",
        "weight": 18
    },
    "🎩 Цилиндр джентльмена (шапка)": {
        "material": "мвк",
        "weight": 15
    },
    "🎃 Тыква на голове (шапка)": {
        "material": "мвк",
        "weight": 12
    },
    "🐴 Маска лошади (шапка)": {
        "material": "мвк",
        "weight": 9
    },
    "🗿 Маска Моаи (шапка)": {
        "material": "мвк",
        "weight": 7
    },
    "🧠 Мозг на голове (шапка)": {
        "material": "мвк",
        "weight": 5
    },
    "🔥 Горящая голова (шапка)": {
        "material": "мвк",
        "weight": 3
    },
    "💎 Алмазная шапка (шапка)": {
        "material": "мвк",
        "weight": 1.5
    },
    "👑 Корона директора Mann Co. (шапка)": {
        "material": "мвк",
        "weight": 0.5
    }
}


craft_chances = {
    "скрап": 0.70,
    "метал": 0.55,
    "мвк": 0.40
}


anime_titles = [
    ("🗿 Абсолют", 30),
    ("🕳️ Дэд инсайд", 25),
    ("🧍 NPC", 20),
    ("🥶 Сигма", 10),
    ("🧠 200 IQ", 6),
    ("🤫 Анимешник", 4),
    ("⚡ Протагонист", 3),
    ("💀 Последний нейрон", 1),
    ("🔥 Главный герой", 0.8),
    ("👑 Избранный", 0.2)
]


def db():
    return sqlite3.connect(DB)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 1000,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            title TEXT,
            showcase_item TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            scrap INTEGER DEFAULT 0,
            metal INTEGER DEFAULT 0,
            mvk INTEGER DEFAULT 0,
            hat TEXT
        )
    """)

    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]

    migrations = {
        "level": "INTEGER DEFAULT 1",
        "xp": "INTEGER DEFAULT 0",
        "scrap": "INTEGER DEFAULT 0",
        "metal": "INTEGER DEFAULT 0",
        "mvk": "INTEGER DEFAULT 0",
        "hat": "TEXT"
    }

    for column, definition in migrations.items():
        if column not in columns:
            cur.execute(
                f"ALTER TABLE users ADD COLUMN {column} {definition}"
            )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item TEXT,
            amount INTEGER,
            PRIMARY KEY(user_id, item)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS titles (
            user_id INTEGER,
            title TEXT,
            PRIMARY KEY(user_id, title)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hats (
            user_id INTEGER,
            hat TEXT,
            amount INTEGER,
            PRIMARY KEY(user_id, hat)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            author TEXT,
            content TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id INTEGER PRIMARY KEY,
            work_until INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def ensure_user(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user_id,)
    )

    if not cur.fetchone():
        cur.execute(
            """
            INSERT INTO users
            (user_id, coins, level, xp, scrap, metal, mvk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, 50, 1, 0, 0, 0, 0)
        )

    conn.commit()
    conn.close()


def get_user(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            user_id,
            coins,
            wins,
            losses,
            title,
            showcase_item,
            level,
            xp,
            scrap,
            metal,
            mvk,
            hat
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    row = cur.fetchone()
    conn.close()

    return row


def add_coins(user_id, amount):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET coins = coins + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()


def remove_coins(user_id, amount):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT coins FROM users WHERE user_id = ?",
        (user_id,)
    )

    row = cur.fetchone()

    if not row or row[0] < amount:
        conn.close()
        return False

    cur.execute(
        "UPDATE users SET coins = coins - ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

    return True


def xp_needed(level):
    return 100 + (level - 1) * 25


def add_xp(user_id, amount):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT level, xp FROM users WHERE user_id = ?",
        (user_id,)
    )

    level, xp = cur.fetchone()

    xp += amount
    leveled_up = False

    while xp >= xp_needed(level):
        xp -= xp_needed(level)
        level += 1
        leveled_up = True

    cur.execute(
        "UPDATE users SET level = ?, xp = ? WHERE user_id = ?",
        (level, xp, user_id)
    )

    conn.commit()
    conn.close()

    return level, xp, leveled_up


def get_work_cooldown(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT work_until FROM cooldowns WHERE user_id = ?",
        (user_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return 0

    return row[0]


def set_work_cooldown(user_id, timestamp):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM cooldowns WHERE user_id = ?",
        (user_id,)
    )

    if cur.fetchone():
        cur.execute(
            "UPDATE cooldowns SET work_until = ? WHERE user_id = ?",
            (timestamp, user_id)
        )
    else:
        cur.execute(
            "INSERT INTO cooldowns (user_id, work_until) VALUES (?, ?)",
            (user_id, timestamp)
        )

    conn.commit()
    conn.close()


def add_win(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET wins = wins + 1 WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def add_loss(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET losses = losses + 1 WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def add_item(user_id, item):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT amount FROM inventory WHERE user_id = ? AND item = ?",
        (user_id, item)
    )

    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE inventory
            SET amount = amount + 1
            WHERE user_id = ? AND item = ?
            """,
            (user_id, item)
        )
    else:
        cur.execute(
            """
            INSERT INTO inventory
            (user_id, item, amount)
            VALUES (?, ?, 1)
            """,
            (user_id, item)
        )

    conn.commit()
    conn.close()


def remove_item(user_id, item, amount=1):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT amount
        FROM inventory
        WHERE user_id = ? AND item = ?
        """,
        (user_id, item)
    )

    row = cur.fetchone()

    if not row or row[0] < amount:
        conn.close()
        return False

    new_amount = row[0] - amount

    if new_amount <= 0:
        cur.execute(
            """
            DELETE FROM inventory
            WHERE user_id = ? AND item = ?
            """,
            (user_id, item)
        )
    else:
        cur.execute(
            """
            UPDATE inventory
            SET amount = ?
            WHERE user_id = ? AND item = ?
            """,
            (new_amount, user_id, item)
        )

    conn.commit()
    conn.close()

    return True


def get_inventory(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT item, amount
        FROM inventory
        WHERE user_id = ?
        ORDER BY amount DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def add_title(user_id, title):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO titles
        (user_id, title)
        VALUES (?, ?)
        """,
        (user_id, title)
    )

    conn.commit()
    conn.close()


def get_titles(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT title FROM titles WHERE user_id = ?",
        (user_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return [row[0] for row in rows]


def set_title(user_id, title):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET title = ? WHERE user_id = ?",
        (title, user_id)
    )

    conn.commit()
    conn.close()


def set_showcase(user_id, item):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET showcase_item = ?
        WHERE user_id = ?
        """,
        (item, user_id)
    )

    conn.commit()
    conn.close()


def clear_showcase(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET showcase_item = NULL
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()


def set_hat(user_id, hat):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET hat = ? WHERE user_id = ?",
        (hat, user_id)
    )

    conn.commit()
    conn.close()


def clear_hat(user_id):
    set_hat(user_id, None)


def get_materials(user_id):
    row = get_user(user_id)

    return {
        "скрап": row[8],
        "метал": row[9],
        "мвк": row[10]
    }


def add_material(user_id, material, amount):
    ensure_user(user_id)

    column = {
        "скрап": "scrap",
        "метал": "metal",
        "мвк": "mvk"
    }.get(material)

    if not column:
        return

    conn = db()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE users SET {column} = {column} + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()


def remove_material(user_id, material, amount):
    materials_data = get_materials(user_id)

    if materials_data.get(material, 0) < amount:
        return False

    column = {
        "скрап": "scrap",
        "метал": "metal",
        "мвк": "mvk"
    }.get(material)

    if not column:
        return False

    conn = db()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE users SET {column} = {column} - ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

    return True


def get_hat_inventory(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT hat, amount
        FROM hats
        WHERE user_id = ?
        ORDER BY amount DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def add_hat(user_id, hat):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT amount FROM hats WHERE user_id = ? AND hat = ?",
        (user_id, hat)
    )

    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE hats
            SET amount = amount + 1
            WHERE user_id = ? AND hat = ?
            """,
            (user_id, hat)
        )
    else:
        cur.execute(
            """
            INSERT INTO hats
            (user_id, hat, amount)
            VALUES (?, ?, 1)
            """,
            (user_id, hat)
        )

    conn.commit()
    conn.close()


def has_hat(user_id, hat):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT amount
        FROM hats
        WHERE user_id = ? AND hat = ?
        """,
        (user_id, hat)
    )

    row = cur.fetchone()
    conn.close()

    return bool(row and row[0] > 0)


def add_quote(user_id, author, content):
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO quotes
            (user_id, author, content)
            VALUES (?, ?, ?)
            """,
            (user_id, author, content)
        )

        conn.commit()
        added = True

    except sqlite3.IntegrityError:
        added = False

    conn.close()

    return added


def get_random_quote():
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT author, content
        FROM quotes
        ORDER BY RANDOM()
        LIMIT 1
        """
    )

    row = cur.fetchone()
    conn.close()

    return row


def find_case(name):
    name = name.lower().strip()

    for case_name in cases:
        if name == case_name.lower():
            return case_name

    for case_name in cases:
        if name in case_name.lower():
            return case_name

    return None


def roll_case_item(case_name):
    loot = cases[case_name]["loot"]

    total = sum(
        weight
        for item, weight in loot
    )

    roll = random.uniform(0, total)
    current = 0

    for item, weight in loot:
        current += weight

        if roll <= current:
            return item

    return loot[-1][0]


def roll_case(case_name):
    data = cases[case_name]

    money = random.randint(
        data["money"][0],
        data["money"][1]
    )

    item = None

    if random.random() < data["item_chance"]:
        item = roll_case_item(case_name)

    return money, item


def case_value(money, item):
    value = money

    if item:
        value += int(
            items[item]["price"] * 0.7
        )

    return value


def get_scrap_reward(item):
    rarity = items[item]["rarity"]

    if "Обычный" in rarity:
        return {
            "скрап": 2
        }

    if "Необычный" in rarity:
        return {
            "скрап": 2,
            "метал": 1
        }

    if "Редкий" in rarity:
        return {
            "метал": 3
        }

    if "Эпический" in rarity:
        return {
            "метал": 1,
            "мвк": 1
        }

    if "Легендарный" in rarity:
        return {
            "мвк": 2
        }

    if "Артефакт" in rarity:
        return {
            "мвк": 4
        }

    return {}


def format_materials(rewards):
    result = []

    for material, amount in rewards.items():
        result.append(
            f"{materials[material]['name']} × **{amount}**"
        )

    return "\n".join(result)


def roll_hat(material):
    available = []

    for hat, data in hats.items():
        if data["material"] == material:
            available.append(
                (hat, data["weight"])
            )

    if not available:
        return None

    total = sum(
        weight
        for hat, weight in available
    )

    roll = random.uniform(0, total)
    current = 0

    for hat, weight in available:
        current += weight

        if roll <= current:
            return hat

    return available[-1][0]


async def money_drop_loop():
    global active_drop

    await bot.wait_until_ready()

    while not bot.is_closed():
        await asyncio.sleep(
            random.randint(
                600,
                2400
            )
        )

        channel = bot.get_channel(
            DROP_CHANNEL_ID
        )

        if not channel:
            continue

        roll = random.random()

        if roll < 0.003:
            amount = random.randint(
                200,
                400
            )

            drop_type = "👑 **УЛЬТРА-ДРОП!**"

        elif roll < 0.015:
            amount = random.randint(
                80,
                180
            )

            drop_type = "💎 **МЕГА-ДРОП!**"

        elif roll < 0.06:
            amount = random.randint(
                30,
                80
            )

            drop_type = "🔥 **ЖИРНЫЙ ДРОП!**"

        else:
            amount = random.randint(
                5,
                30
            )

            drop_type = "💸 **ДЕНЕЖНЫЙ ДРОП!**"

        active_drop = {
            "amount": amount,
            "claimed": False
        }

        role = discord.utils.get(
            channel.guild.roles,
            name=DROP_ROLE_NAME
        )

        if role:
            ping = role.mention
        else:
            ping = ""

        await channel.send(
            f"{ping}\n"
            f"{drop_type}\n"
            f"Кто первый напишет `!забрать`, тот получает "
            f"**{amount:,} монет**!\n"
            f"⏳ У вас **30 секунд**!"
        )

        await asyncio.sleep(30)

        if active_drop and not active_drop["claimed"]:
            active_drop = None

            await channel.send(
                "💨 **Дроп протух.** Никто не успел его забрать."
            )


class InventoryView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(
            timeout=120
        )

        self.user_id = user_id

    @discord.ui.button(
        label="Продать всё",
        style=discord.ButtonStyle.green,
        emoji="💸"
    )
    async def sell_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Это не твой инвентарь.",
                ephemeral=True
            )
            return

        inventory = get_inventory(
            self.user_id
        )

        total = 0
        sold = 0

        for item, amount in inventory:
            if item not in items:
                continue

            sell_price = int(
                items[item]["price"] * 0.7
            )

            total += sell_price * amount
            sold += amount

        if sold == 0:
            await interaction.response.send_message(
                "❌ Продавать нечего.",
                ephemeral=True
            )
            return

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM inventory WHERE user_id = ?",
            (self.user_id,)
        )

        conn.commit()
        conn.close()

        add_coins(
            self.user_id,
            total
        )

        await interaction.response.send_message(
            f"💸 **ПРОДАНО ВСЁ!**\n\n"
            f"📦 Предметов: **{sold}**\n"
            f"💰 Получено: **{total:,} монет**\n\n"
            f"👑 Титулы и 🧢 шапки продажей не затронуты."
        )


class MogBattleView(discord.ui.View):
    def __init__(
        self,
        challenger,
        opponent,
        case_name
    ):
        super().__init__(
            timeout=30
        )

        self.challenger = challenger
        self.opponent = opponent
        self.case_name = case_name
        self.accepted = None
        self.message = None

    @discord.ui.button(
        label="Принять",
        style=discord.ButtonStyle.green,
        emoji="⚔️"
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message(
                "❌ Это не твой вызов.",
                ephemeral=True
            )
            return

        if self.accepted is not None:
            await interaction.response.send_message(
                "❌ Этот мог-батл уже обработан.",
                ephemeral=True
            )
            return

        self.accepted = False

        user1 = get_user(
            self.challenger.id
        )

        user2 = get_user(
            self.opponent.id
        )

        price = cases[
            self.case_name
        ]["price"]

        required_level = cases[
            self.case_name
        ]["unlock_level"]

        if user1[6] < required_level:
            await interaction.response.edit_message(
                content=(
                    f"❌ {self.challenger.mention} больше не имеет "
                    f"доступа к этому кейсу."
                ),
                view=None
            )

            self.stop()
            return

        if user2[6] < required_level:
            await interaction.response.edit_message(
                content=(
                    f"❌ {self.opponent.mention} ещё не достиг "
                    f"**{required_level} уровня**."
                ),
                view=None
            )

            self.stop()
            return

        if user1[1] < price:
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(
                content=(
                    f"❌ {self.challenger.mention} уже не может оплатить "
                    f"**{price:,} монет** за этот мог-батл."
                ),
                view=self
            )

            self.stop()
            return

        if user2[1] < price:
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(
                content=(
                    f"❌ {self.opponent.mention} не может оплатить "
                    f"**{price:,} монет** за этот мог-батл."
                ),
                view=self
            )

            self.stop()
            return

        self.accepted = True

        remove_coins(
            self.challenger.id,
            price
        )

        remove_coins(
            self.opponent.id,
            price
        )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=(
                f"⚔️ **МОГ-БАТЛ НАЧИНАЕТСЯ!**\n\n"
                f"📦 Кейс: **{self.case_name}**\n"
                f"💰 Ставка каждого: **{price:,} монет**\n"
                f"🏆 Банк: **{price * 2:,} монет**\n\n"
                f"🎲 Открываем кейсы..."
            ),
            view=self
        )

        await asyncio.sleep(1.5)

        money1, item1 = roll_case(
            self.case_name
        )

        money2, item2 = roll_case(
            self.case_name
        )

        value1 = case_value(
            money1,
            item1
        )

        value2 = case_value(
            money2,
            item2
        )

        result1 = f"💰 {money1:,} монет"

        if item1:
            result1 += (
                f"\n🎁 {item1}"
                f"\n{items[item1]['rarity']}"
            )

        result2 = f"💰 {money2:,} монет"

        if item2:
            result2 += (
                f"\n🎁 {item2}"
                f"\n{items[item2]['rarity']}"
            )

        if item1:
            add_item(
                self.challenger.id,
                item1
            )

        if item2:
            add_item(
                self.opponent.id,
                item2
            )

        add_coins(
            self.challenger.id,
            money1
        )

        add_coins(
            self.opponent.id,
            money2
        )

        xp_gain = max(
            2,
            min(
                10,
                price // 100
            )
        )

        level1, xp1, leveled1 = add_xp(
            self.challenger.id,
            xp_gain
        )

        level2, xp2, leveled2 = add_xp(
            self.opponent.id,
            xp_gain
        )

        bank = price * 2

        if value1 > value2:
            winner = self.challenger
            loser = self.opponent

            add_coins(
                winner.id,
                bank
            )

            add_win(
                winner.id
            )

            add_loss(
                loser.id
            )

            result = (
                f"🏆 **{winner.mention} МОГНУЛ!**\n"
                f"💰 Забирает весь банк: **{bank:,} монет**"
            )

        elif value2 > value1:
            winner = self.opponent
            loser = self.challenger

            add_coins(
                winner.id,
                bank
            )

            add_win(
                winner.id
            )

            add_loss(
                loser.id
            )

            result = (
                f"🏆 **{winner.mention} МОГНУЛ!**\n"
                f"💰 Забирает весь банк: **{bank:,} монет**"
            )

        else:
            add_coins(
                self.challenger.id,
                price
            )

            add_coins(
                self.opponent.id,
                price
            )

            result = (
                "🤝 **НИЧЬЯ!**\n"
                f"💸 Каждый получил обратно свои "
                f"**{price:,} монет**."
            )

        await interaction.followup.send(
            f"⚔️ **МОГ-БАТЛ ЗАВЕРШЁН!**\n\n"
            f"📦 Кейс: **{self.case_name}**\n\n"
            f"👤 {self.challenger.mention}\n"
            f"{result1}\n"
            f"📊 Ценность дропа: **{value1:,}**\n\n"
            f"👤 {self.opponent.mention}\n"
            f"{result2}\n"
            f"📊 Ценность дропа: **{value2:,}**\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"{result}"
        )

        self.stop()

    @discord.ui.button(
        label="Отказаться",
        style=discord.ButtonStyle.red,
        emoji="💀"
    )
    async def decline(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message(
                "❌ Это не твой вызов.",
                ephemeral=True
            )
            return

        if self.accepted is not None:
            await interaction.response.send_message(
                "❌ Этот мог-батл уже обработан.",
                ephemeral=True
            )
            return

        self.accepted = False

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=(
                f"💀 {self.opponent.mention} "
                f"**отказался от мог-батла.**\n"
                f"{self.challenger.mention}, тебя не признали достойным."
            ),
            view=self
        )

        self.stop()

    async def on_timeout(self):
        if self.accepted is not None:
            return

        self.accepted = False

        for child in self.children:
            child.disabled = True

        try:
            await self.message.edit(
                content=(
                    f"⏱️ **Вызов истёк.**\n"
                    f"{self.opponent.mention} слишком долго думал."
                ),
                view=self
            )
        except:
            pass


@bot.event
async def on_ready():
    global drop_task

    print(
        f"Бот запущен как {bot.user}"
    )

    if drop_task is None or drop_task.done():
        drop_task = asyncio.create_task(
            money_drop_loop()
        )


@bot.event
async def on_raw_reaction_add(payload):
    if bot.user and payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != "🐊":
        return

    channel = bot.get_channel(
        payload.channel_id
    )

    if not channel:
        return

    try:
        message = await channel.fetch_message(
            payload.message_id
        )
    except:
        return

    if message.author.bot:
        return

    crocodiles = 0

    for reaction in message.reactions:
        if str(reaction.emoji) == "🐊":
            crocodiles = reaction.count
            break

    if crocodiles < 2:
        return

    quote = message.content.strip()

    if not quote:
        return

    added = add_quote(
        message.author.id,
        str(message.author),
        quote
    )

    if added:
        try:
            await channel.send(
                f"📜 **ЦИТАТА ЗАФИКСИРОВАНА**\n"
                f"> {quote[:1500]}\n"
                f"— {message.author.mention}"
            )
        except:
            pass


@bot.command()
async def команды(ctx):
    embed = discord.Embed(
        title="💣 Бом бом",
        description="Все команды бота:",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="💰 Экономика",
        value=(
            "`!баланс`\n"
            "`!работа`\n"
            "`!дать @user сумма`\n"
            "`!выдать @user сумма`\n"
            "`!топ`"
        ),
        inline=False
    )

    embed.add_field(
        name="📦 Кейсы",
        value=(
            "`!кейсы`\n"
            "`!кейс название`"
        ),
        inline=False
    )

    embed.add_field(
        name="🎒 Инвентарь",
        value=(
            "`!инвентарь`\n"
            "`!продать предмет`\n"
            "`!витрина предмет`\n"
            "`!витрина убрать`\n"
            "Кнопка **💸 Продать всё**"
        ),
        inline=False
    )

    embed.add_field(
        name="♻️ Ресурсы",
        value=(
            "`!ресурсы`\n"
            "`!утилизировать предмет`"
        ),
        inline=False
    )

    embed.add_field(
        name="🧢 Шапки",
        value=(
            "`!крафт шапка скрап`\n"
            "`!крафт шапка метал`\n"
            "`!крафт шапка мвк`\n"
            "`!шапка название`\n"
            "`!шапка убрать`"
        ),
        inline=False
    )

    embed.add_field(
        name="👤 Профиль",
        value=(
            "`!профиль`\n"
            "`!профиль @user`\n"
            "`!титулы`\n"
            "`!титул название`\n"
            "`!титул убрать`"
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ Мог-батл",
        value=(
            "`!могбатл @user кейс`\n"
            "Вызывающий выбирает кейс.\n"
            "Оба открывают один и тот же кейс."
        ),
        inline=False
    )

    embed.add_field(
        name="🎮 Игры",
        value=(
            "`!кубик`\n"
            "`!монетка`\n"
            "`!угадай`"
        ),
        inline=False
    )

    embed.add_field(
        name="💸 Дропы",
        value=(
            "`!забрать`\n"
            "`!дроппинг`\n"
            "Денежные дропы появляются раз в 10–40 минут.\n"
            "Подписавшиеся получают пинг роли **Дроп**."
        ),
        inline=False
    )

    embed.add_field(
        name="📜 Цитаты",
        value=(
            "`!цитата`\n\n"
            "Поставь 🐊🐊 на сообщение — "
            "оно автоматически станет цитатой."
        ),
        inline=False
    )

    embed.add_field(
        name="🎌 Аниме",
        value=(
            "`!аниме_кейс`\n"
            "Ключ: `📖 26 том магической битвы`"
        ),
        inline=False
    )

    await ctx.send(
        embed=embed
    )


@bot.command()
async def баланс(ctx):
    row = get_user(
        ctx.author.id
    )

    await ctx.send(
        f"💰 {ctx.author.mention}, у тебя "
        f"**{row[1]:,} монет**."
    )


@bot.command()
async def дать(
    ctx,
    member: discord.Member = None,
    amount: int = None
):
    if not member or amount is None:
        await ctx.send(
            "❌ Используй:\n"
            "`!дать @user сумма`"
        )
        return

    if member.id == ctx.author.id:
        await ctx.send(
            "💀 Самому себе нельзя."
        )
        return

    if member.bot:
        await ctx.send(
            "🤖 Ботам деньги передавать нельзя."
        )
        return

    if amount <= 0:
        await ctx.send(
            "❌ Сумма должна быть больше нуля."
        )
        return

    if not remove_coins(
        ctx.author.id,
        amount
    ):
        await ctx.send(
            "💸 У тебя недостаточно денег."
        )
        return

    add_coins(
        member.id,
        amount
    )

    await ctx.send(
        f"💸 {ctx.author.mention} передал "
        f"{member.mention} **{amount:,} монет**."
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def выдать(
    ctx,
    member: discord.Member = None,
    amount: int = None
):
    if (
        not member
        or amount is None
        or amount <= 0
    ):
        await ctx.send(
            "❌ Используй:\n"
            "`!выдать @user сумма`"
        )
        return

    add_coins(
        member.id,
        amount
    )

    await ctx.send(
        f"👑 {member.mention} получил "
        f"**{amount:,} монет**."
    )


@bot.command()
async def работа(ctx):
    ensure_user(
        ctx.author.id
    )

    now = int(
        time.time()
    )

    cooldown_until = get_work_cooldown(
        ctx.author.id
    )

    if now < cooldown_until:
        remaining = cooldown_until - now

        hours = remaining // 3600
        minutes = (
            remaining % 3600
        ) // 60

        await ctx.send(
            f"⏳ Ты уже работал.\n"
            f"Попробуй через **{hours} ч. {minutes} мин.**"
        )

        return

    cooldown = 6 * 60 * 60

    set_work_cooldown(
        ctx.author.id,
        now + cooldown
    )

    money = random.randint(
        5,
        25
    )

    add_coins(
        ctx.author.id,
        money
    )

    xp_gain = random.randint(
        5,
        9
    )

    level, xp, leveled_up = add_xp(
        ctx.author.id,
        xp_gain
    )

    message = (
        f"💼 Ты поработал и получил "
        f"**{money:,} монет**.\n"
        f"✨ Опыт: **+{xp_gain} XP**"
    )

    if leveled_up:
        message += (
            f"\n\n🎉 **НОВЫЙ УРОВЕНЬ!**\n"
            f"Ты достиг **{level} уровня**!"
        )

    if random.random() < 0.05:
        add_item(
            ctx.author.id,
            "📖 26 том магической битвы"
        )

        message += (
            "\n\n📖 **ЧТО ЗА ХУЙНЯ**\n"
            "Ты нашёл **26 том магической битвы**."
        )

    await ctx.send(
        message
    )


@bot.command()
async def топ(ctx):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT user_id, coins
        FROM users
        ORDER BY coins DESC
        LIMIT 10
        """
    )

    rows = cur.fetchall()
    conn.close()

    text = "🏆 **ТОП БОГАЧЕЙ**\n\n"

    for i, (user_id, coins) in enumerate(
        rows,
        1
    ):
        user = bot.get_user(
            user_id
        )

        if user:
            name = user.mention
        else:
            name = f"<@{user_id}>"

        text += (
            f"**{i}.** {name} — "
            f"💰 **{coins:,}**\n"
        )

    await ctx.send(
        text
    )


@bot.command()
async def кейсы(ctx):
    row = get_user(
        ctx.author.id
    )

    level = row[6]

    text = (
        f"📦 **ДОСТУПНЫЕ КЕЙСЫ**\n"
        f"🎖️ Твой уровень: **{level}**\n\n"
    )

    for name, data in cases.items():
        required = data["unlock_level"]

        if level >= required:
            status = "✅ Доступен"
        else:
            status = f"🔒 С {required} уровня"

        text += (
            f"{name}\n"
            f"💰 Цена: **{data['price']:,}**\n"
            f"{status}\n\n"
        )

    text += (
        "Использование:\n"
        "`!кейс название`"
    )

    await ctx.send(
        text
    )


@bot.command()
async def кейс(
    ctx,
    *,
    case_name=None
):
    if not case_name:
        await ctx.send(
            "❌ Ты забыл выбрать кейс.\n\n"
            "Посмотри доступные кейсы через `!кейсы`.\n"
            "Например:\n"
            "`!кейс алмаз`"
        )
        return

    case_name = find_case(
        case_name
    )

    if not case_name:
        await ctx.send(
            "❌ Такого кейса нет.\n"
            "Посмотри список через `!кейсы`."
        )
        return

    data = cases[
        case_name
    ]

    user = get_user(
        ctx.author.id
    )

    if user[6] < data["unlock_level"]:
        await ctx.send(
            f"🔒 **{case_name}** пока заблокирован.\n\n"
            f"🎖️ Нужен **{data['unlock_level']} уровень**.\n"
            f"Твой уровень: **{user[6]}**."
        )
        return

    async with case_open_lock:
        if not remove_coins(
            ctx.author.id,
            data["price"]
        ):
            await ctx.send(
                f"💸 Для этого кейса нужно "
                f"**{data['price']:,} монет**."
            )
            return

        await asyncio.sleep(1)

        money, item = roll_case(
            case_name
        )

        add_coins(
            ctx.author.id,
            money
        )

        xp_gain = max(
            2,
            min(
                10,
                data["price"] // 100
            )
        )

        level, xp, leveled_up = add_xp(
            ctx.author.id,
            xp_gain
        )

        message = (
            f"📦 **{case_name}**\n\n"
            f"💰 Получено: **{money:,} монет**\n"
            f"✨ Опыт: **+{xp_gain} XP**"
        )

        if item:
            add_item(
                ctx.author.id,
                item
            )

            rarity = items[item]["rarity"]
            price = items[item]["price"]
            sell_price = int(
                price * 0.7
            )

            message += (
                f"\n\n🎁 **ПРЕДМЕТ!**\n"
                f"{item}\n"
                f"{rarity} • 💰 {price:,} монет\n"
                f"💸 При продаже: {sell_price:,}"
            )

        else:
            message += (
                "\n\n📦 **В кейсе ничего особенного.**"
            )

        if leveled_up:
            message += (
                f"\n\n🎉 **НОВЫЙ УРОВЕНЬ!**\n"
                f"Ты достиг **{level} уровня**!"
            )

        if random.random() < 0.005:
            add_item(
                ctx.author.id,
                "📖 26 том магической битвы"
            )

            message += (
                "\n\n📖 **ЧТО ЗА ХУЙНЯ**\n"
                "Ты каким-то образом нашёл "
                "**26 том магической битвы**.\n"
                "Он нужен для `!аниме_кейс`."
            )

        await ctx.send(
            message
        )


@bot.command()
async def инвентарь(ctx):
    inventory = get_inventory(
        ctx.author.id
    )

    materials_data = get_materials(
        ctx.author.id
    )

    hat_inventory = get_hat_inventory(
        ctx.author.id
    )

    text = (
        f"🎒 **ИНВЕНТАРЬ {ctx.author.display_name}**\n\n"
    )

    if inventory:
        for item, amount in inventory:
            rarity = items.get(
                item,
                {}
            ).get(
                "rarity",
                ""
            )

            text += (
                f"{item} × **{amount}** "
                f"{rarity}\n"
            )
    else:
        text += "📦 Обычных предметов нет.\n"

    text += "\n♻️ **РЕСУРСЫ**\n"

    text += (
        f"🪨 Скрап × **{materials_data['скрап']}**\n"
        f"🔩 Метал × **{materials_data['метал']}**\n"
        f"⚙️ МВК × **{materials_data['мвк']}**\n"
    )

    if hat_inventory:
        text += "\n🧢 **ШАПКИ**\n"

        for hat, amount in hat_inventory:
            text += (
                f"{hat} × **{amount}**\n"
            )

    await ctx.send(
        text,
        view=InventoryView(
            ctx.author.id
        )
    )


@bot.command()
async def продать(
    ctx,
    *,
    item=None
):
    if not item:
        await ctx.send(
            "❌ Напиши предмет.\n"
            "Например: `!продать Ubuntu`"
        )
        return

    if "титул" in item.lower():
        await ctx.send(
            "❌ Титулы нельзя продавать."
        )
        return

    if "шапка" in item.lower():
        await ctx.send(
            "❌ Шапки нельзя продавать."
        )
        return

    inventory = get_inventory(
        ctx.author.id
    )

    found = None

    for owned_item, amount in inventory:
        if item.lower() == owned_item.lower():
            found = owned_item
            break

    if not found:
        for owned_item, amount in inventory:
            if item.lower() in owned_item.lower():
                found = owned_item
                break

    if not found:
        await ctx.send(
            "❌ У тебя нет такого предмета."
        )
        return

    if found not in items:
        await ctx.send(
            "❌ Этот предмет нельзя продавать."
        )
        return

    price = items[found]["price"]

    sell_price = int(
        price * 0.7
    )

    if not remove_item(
        ctx.author.id,
        found
    ):
        await ctx.send(
            "❌ Не удалось продать предмет."
        )
        return

    add_coins(
        ctx.author.id,
        sell_price
    )

    await ctx.send(
        f"💸 Ты продал **{found}** "
        f"за **{sell_price:,} монет**."
    )


@bot.command()
async def утилизировать(
    ctx,
    *,
    item=None
):
    if not item:
        await ctx.send(
            "❌ Напиши предмет.\n"
            "Например: `!утилизировать Ubuntu`"
        )
        return

    inventory = get_inventory(
        ctx.author.id
    )

    found = None

    for owned_item, amount in inventory:
        if item.lower() == owned_item.lower():
            found = owned_item
            break

    if not found:
        for owned_item, amount in inventory:
            if item.lower() in owned_item.lower():
                found = owned_item
                break

    if not found:
        await ctx.send(
            "❌ У тебя нет такого предмета."
        )
        return

    rewards = get_scrap_reward(
        found
    )

    if not rewards:
        await ctx.send(
            "❌ Этот предмет нельзя утилизировать."
        )
        return

    if not remove_item(
        ctx.author.id,
        found
    ):
        await ctx.send(
            "❌ Не удалось утилизировать предмет."
        )
        return

    for material, amount in rewards.items():
        add_material(
            ctx.author.id,
            material,
            amount
        )

    await ctx.send(
        f"♻️ **ПРЕДМЕТ УТИЛИЗИРОВАН**\n\n"
        f"📦 {found}\n\n"
        f"{format_materials(rewards)}"
    )


@bot.command()
async def ресурсы(ctx):
    data = get_materials(
        ctx.author.id
    )

    await ctx.send(
        f"♻️ **ТВОИ РЕСУРСЫ**\n\n"
        f"🪨 Скрап × **{data['скрап']}**\n"
        f"🔩 Метал × **{data['метал']}**\n"
        f"⚙️ МВК × **{data['мвк']}**\n\n"
        f"💡 Для крафта шапки нужно 3 одинаковых ресурса."
    )


@bot.command()
async def крафт(
    ctx,
    *,
    recipe=None
):
    if not recipe:
        await ctx.send(
            "❌ Используй:\n"
            "`!крафт шапка скрап`\n"
            "`!крафт шапка метал`\n"
            "`!крафт шапка мвк`"
        )
        return

    recipe = recipe.lower().strip()

    if recipe.startswith("шапка "):
        material = recipe.replace(
            "шапка ",
            "",
            1
        ).strip()
    else:
        await ctx.send(
            "❌ Используй:\n"
            "`!крафт шапка скрап`\n"
            "`!крафт шапка метал`\n"
            "`!крафт шапка мвк`"
        )
        return

    if material not in materials:
        await ctx.send(
            "❌ Неизвестный материал.\n"
            "Доступно: `скрап`, `метал`, `мвк`."
        )
        return

    if not remove_material(
        ctx.author.id,
        material,
        3
    ):
        await ctx.send(
            f"❌ Нужно **3** {materials[material]['name']}."
        )
        return

    chance = craft_chances[material]

    if random.random() > chance:
        await ctx.send(
            f"💀 **КРАФТ ПРОВАЛЕН!**\n\n"
            f"Ты потратил 3 × {materials[material]['name']}.\n"
            f"Шапка не получилась.\n\n"
            f"🎲 Шанс успеха: **{int(chance * 100)}%**"
        )
        return

    result_hat = roll_hat(
        material
    )

    if not result_hat:
        await ctx.send(
            "❌ Для этого материала пока нет шапок."
        )
        add_material(
            ctx.author.id,
            material,
            3
        )
        return

    add_hat(
        ctx.author.id,
        result_hat
    )

    await ctx.send(
        f"🎉 **КРАФТ УДАЛСЯ!**\n\n"
        f"🧢 Ты получил:\n"
        f"**{result_hat}**\n\n"
        f"🎲 Шанс успеха был **{int(chance * 100)}%**."
    )


@bot.command()
async def шапка(
    ctx,
    *,
    hat=None
):
    if not hat:
        await ctx.send(
            "❌ Напиши название шапки.\n"
            "Например: `!шапка Кепка разведчика`\n"
            "Или `!шапка убрать`."
        )
        return

    if hat.lower() == "убрать":
        clear_hat(
            ctx.author.id
        )

        await ctx.send(
            "🧢 Шапка снята."
        )
        return

    found = None

    for hat_name in hats:
        if hat.lower() == hat_name.lower():
            found = hat_name
            break

    if not found:
        for hat_name in hats:
            clean_name = hat_name.replace(
                " (шапка)",
                ""
            )

            if hat.lower() in clean_name.lower():
                found = hat_name
                break

    if not found:
        await ctx.send(
            "❌ Такой шапки не существует."
        )
        return

    if not has_hat(
        ctx.author.id,
        found
    ):
        await ctx.send(
            "❌ У тебя нет этой шапки."
        )
        return

    set_hat(
        ctx.author.id,
        found
    )

    await ctx.send(
        f"🧢 Теперь на тебе **{found}**!"
    )


@bot.command()
async def витрина(
    ctx,
    *,
    item=None
):
    if not item:
        await ctx.send(
            "❌ Напиши предмет.\n"
            "Например: `!витрина Arch Linux`"
        )
        return

    if item.lower() == "убрать":
        clear_showcase(
            ctx.author.id
        )

        await ctx.send(
            "🖼️ Витрина очищена."
        )
        return

    inventory = get_inventory(
        ctx.author.id
    )

    found = None

    for owned_item, amount in inventory:
        if item.lower() == owned_item.lower():
            found = owned_item
            break

    if not found:
        for owned_item, amount in inventory:
            if item.lower() in owned_item.lower():
                found = owned_item
                break

    if not found:
        await ctx.send(
            "❌ У тебя нет такого предмета."
        )
        return

    set_showcase(
        ctx.author.id,
        found
    )

    await ctx.send(
        f"🖼️ На витрину выставлен "
        f"**{found}**."
    )


@bot.command()
async def профиль(
    ctx,
    member: discord.Member = None
):
    member = member or ctx.author

    row = get_user(
        member.id
    )

    if not row:
        await ctx.send(
            "❌ Профиль не найден."
        )
        return

    (
        user_id,
        coins,
        wins,
        losses,
        title,
        showcase,
        level,
        xp,
        scrap,
        metal,
        mvk,
        hat
    ) = row

    needed = xp_needed(
        level
    )

    embed = discord.Embed(
        title=f"👤 Профиль {member.display_name}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="💰 Баланс",
        value=f"**{coins:,}** монет",
        inline=True
    )

    embed.add_field(
        name="🎖️ Уровень",
        value=f"**{level}**",
        inline=True
    )

    embed.add_field(
        name="✨ Опыт",
        value=f"**{xp} / {needed} XP**",
        inline=True
    )

    embed.add_field(
        name="🏆 Победы",
        value=f"**{wins}**",
        inline=True
    )

    embed.add_field(
        name="💀 Поражения",
        value=f"**{losses}**",
        inline=True
    )

    embed.add_field(
        name="👑 Титул",
        value=title or "Нет",
        inline=False
    )

    embed.add_field(
        name="🖼️ Витрина",
        value=showcase or "Пусто",
        inline=False
    )

    embed.add_field(
        name="🧢 Шапка",
        value=hat or "Нет",
        inline=False
    )

    embed.add_field(
        name="♻️ Ресурсы",
        value=(
            f"🪨 {scrap}  "
            f"🔩 {metal}  "
            f"⚙️ {mvk}"
        ),
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await ctx.send(
        embed=embed
    )


@bot.command()
async def титулы(ctx):
    titles = get_titles(
        ctx.author.id
    )

    if not titles:
        await ctx.send(
            "👑 У тебя пока нет титулов."
        )
        return

    text = "👑 **ТВОИ ТИТУЛЫ**\n\n"

    for title in titles:
        text += f"{title}\n"

    await ctx.send(
        text
    )


@bot.command()
async def титул(
    ctx,
    *,
    title=None
):
    if not title:
        await ctx.send(
            "❌ Напиши титул.\n"
            "Например: `!титул Сигма`"
        )
        return

    if title.lower() == "убрать":
        set_title(
            ctx.author.id,
            None
        )

        await ctx.send(
            "👑 Титул убран."
        )
        return

    titles = get_titles(
        ctx.author.id
    )

    found = None

    for owned_title in titles:
        if title.lower() == owned_title.lower():
            found = owned_title
            break

    if not found:
        for owned_title in titles:
            if title.lower() in owned_title.lower():
                found = owned_title
                break

    if not found:
        await ctx.send(
            "❌ У тебя нет такого титула."
        )
        return

    set_title(
        ctx.author.id,
        found
    )

    await ctx.send(
        f"👑 Теперь твой титул: **{found}**"
    )


@bot.command()
async def аниме_кейс(ctx):
    key = "📖 26 том магической битвы"

    inventory = get_inventory(
        ctx.author.id
    )

    amount = 0

    for item, item_amount in inventory:
        if item == key:
            amount = item_amount
            break

    if amount <= 0:
        await ctx.send(
            "❌ У тебя нет **26 тома магической битвы**."
        )
        return

    remove_item(
        ctx.author.id,
        key
    )

    roll = random.uniform(
        0,
        sum(
            weight
            for title, weight in anime_titles
        )
    )

    current = 0
    selected = anime_titles[-1][0]

    for title, weight in anime_titles:
        current += weight

        if roll <= current:
            selected = title
            break

    add_title(
        ctx.author.id,
        selected
    )

    await ctx.send(
        f"🎌 **АНИМЕ-КЕЙС ОТКРЫТ!**\n\n"
        f"👑 Тебе выпал титул:\n"
        f"**{selected}**"
    )


@bot.command()
async def кубик(ctx):
    result = random.randint(
        1,
        6
    )

    await ctx.send(
        f"🎲 Выпало: **{result}**"
    )


@bot.command()
async def монетка(ctx):
    result = random.choice(
        [
            "Орёл 🦅",
            "Решка 🪙"
        ]
    )

    await ctx.send(
        f"🪙 **{result}**"
    )


@bot.command()
async def угадай(ctx):
    number = random.randint(
        1,
        10
    )

    await ctx.send(
        "🎯 Я загадал число от **1 до 10**.\n"
        "Напиши свой вариант."
    )

    def check(message):
        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and message.content.isdigit()
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=15,
            check=check
        )

    except asyncio.TimeoutError:
        await ctx.send(
            f"⏱️ Время вышло. "
            f"Я загадал **{number}**."
        )
        return

    guess = int(
        message.content
    )

    if guess == number:
        add_coins(
            ctx.author.id,
            50
        )

        await ctx.send(
            f"🎯 **УГАДАЛ!**\n"
            f"Число было **{number}**.\n"
            f"💰 +50 монет."
        )

    else:
        await ctx.send(
            f"❌ Не угадал.\n"
            f"Я загадал **{number}**."
        )


@bot.command()
async def цитата(ctx):
    quote = get_random_quote()

    if not quote:
        await ctx.send(
            "📜 Пока нет ни одной цитаты.\n"
            "Поставьте 🐊🐊 на какое-нибудь "
            "сообщение."
        )
        return

    author, content = quote

    await ctx.send(
        f"📜 **Случайная цитата:**\n\n"
        f"> {content}\n\n"
        f"— **{author}**"
    )


@bot.command()
async def могбатл(
    ctx,
    opponent: discord.Member = None,
    *,
    case_name=None
):
    if not opponent:
        await ctx.send(
            "❌ Укажи противника.\n\n"
            "Использование:\n"
            "`!могбатл @user название кейса`"
        )
        return

    if not case_name:
        await ctx.send(
            "❌ Ты обязан выбрать кейс.\n\n"
            "Использование:\n"
            "`!могбатл @user алмаз`"
        )
        return

    if opponent.id == ctx.author.id:
        await ctx.send(
            "💀 Нельзя вызвать самого себя."
        )
        return

    if opponent.bot:
        await ctx.send(
            "🤖 Ботов могать нельзя."
        )
        return

    case_name = find_case(
        case_name
    )

    if not case_name:
        await ctx.send(
            "❌ Такого кейса нет.\n"
            "Посмотри доступные через `!кейсы`."
        )
        return

    price = cases[
        case_name
    ]["price"]

    required_level = cases[
        case_name
    ]["unlock_level"]

    challenger = get_user(
        ctx.author.id
    )

    opponent_user = get_user(
        opponent.id
    )

    if challenger[6] < required_level:
        await ctx.send(
            f"🔒 Этот кейс открывается только "
            f"с **{required_level} уровня**.\n"
            f"Твой уровень: **{challenger[6]}**."
        )
        return

    if opponent_user[6] < required_level:
        await ctx.send(
            f"🔒 {opponent.mention} ещё не достиг "
            f"**{required_level} уровня** для этого кейса."
        )
        return

    if challenger[1] < price:
        await ctx.send(
            f"💸 У тебя недостаточно денег.\n"
            f"Нужно **{price:,} монет**."
        )
        return

    if opponent_user[1] < price:
        await ctx.send(
            f"💸 У {opponent.mention} недостаточно денег "
            f"для этого мог-батла.\n"
            f"Ему нужно **{price:,} монет**."
        )
        return

    view = MogBattleView(
        ctx.author,
        opponent,
        case_name
    )

    message = await ctx.send(
        f"⚔️ {ctx.author.mention} **вызывает на МОГ-БАТЛ** "
        f"{opponent.mention}!\n\n"
        f"📦 Кейс: **{case_name}**\n"
        f"💰 Ставка: **{price:,} монет** с каждого\n"
        f"🏆 Банк: **{price * 2:,} монет**\n\n"
        f"💀 {opponent.mention}, ты принимаешь вызов?\n"
        f"⏳ У тебя **30 секунд**.",
        view=view
    )

    view.message = message


@bot.command()
async def забрать(ctx):
    global active_drop

    if ctx.channel.id != DROP_CHANNEL_ID:
        await ctx.send(
            "❌ Забрать дроп можно только "
            "в специальном канале."
        )
        return

    if not active_drop:
        await ctx.send(
            "💨 Сейчас нет активного дропа."
        )
        return

    if active_drop["claimed"]:
        await ctx.send(
            "💨 Дроп уже забрали."
        )
        return

    amount = active_drop["amount"]

    active_drop["claimed"] = True
    active_drop = None

    add_coins(
        ctx.author.id,
        amount
    )

    await ctx.send(
        f"💰 **УСПЕЛ!**\n"
        f"{ctx.author.display_name}, ты забрал "
        f"**{amount:,} монет**!"
    )


@bot.command()
async def дроппинг(ctx):
    role = discord.utils.get(
        ctx.guild.roles,
        name=DROP_ROLE_NAME
    )

    if not role:
        await ctx.send(
            "❌ Роль `Дроп` не найдена."
        )
        return

    if role >= ctx.guild.me.top_role:
        await ctx.send(
            "❌ Я не могу управлять ролью `Дроп`.\n"
            "Подними мою роль выше роли `Дроп`."
        )
        return

    if role in ctx.author.roles:
        await ctx.author.remove_roles(
            role
        )

        await ctx.send(
            f"🔕 {ctx.author.mention}, "
            f"ты отписался от дропов."
        )

    else:
        await ctx.author.add_roles(
            role
        )

        await ctx.send(
            f"🔔 {ctx.author.mention}, "
            f"ты подписался на дропы!\n"
            f"Теперь при появлении дропа будет пинг роли."
        )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(
        error,
        commands.MissingPermissions
    ):
        await ctx.send(
            "❌ У тебя нет прав для этой команды."
        )
        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        await ctx.send(
            "❌ Не хватает аргументов.\n"
            "Используй `!команды` для справки."
        )
        return

    if isinstance(
        error,
        commands.BadArgument
    ):
        await ctx.send(
            "❌ Не удалось распознать аргумент."
        )
        return


init_db()

print(
    "TOKEN найден:",
    bool(TOKEN)
)

print(
    "Длина TOKEN:",
    len(TOKEN) if TOKEN else 0
)

bot.run(TOKEN)
