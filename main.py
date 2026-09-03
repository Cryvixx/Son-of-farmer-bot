import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
import time
import os
import re
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
    "🧦 Чулок": {"price": 25, "rarity": "common"},
    "💾 Ubuntu": {"price": 50, "rarity": "common"},
    "💾 Debian": {"price": 75, "rarity": "common"},
    "💾 Fedora": {"price": 100, "rarity": "uncommon"},
    "💾 Linux Mint": {"price": 125, "rarity": "uncommon"},
    "💾 Manjaro": {"price": 175, "rarity": "rare"},
    "💾 Arch Linux": {"price": 250, "rarity": "rare"},
    "💾 Gentoo": {"price": 500, "rarity": "epic"},
    "💜 Аметист": {"price": 150, "rarity": "rare"},
    "⚡ Lit Energy": {"price": 75, "rarity": "common"},
    "⚡ Monster": {"price": 125, "rarity": "uncommon"},
    "⚡ Red Bull": {"price": 150, "rarity": "rare"},
    "⚡ Burn": {"price": 200, "rarity": "rare"},
    "🎮 Godot": {"price": 125, "rarity": "uncommon"},
    "🎮 Unity": {"price": 250, "rarity": "rare"},
    "🎮 Unreal Engine": {"price": 500, "rarity": "epic"},
    "🎮 Source Engine": {"price": 750, "rarity": "epic"},
    "🎮 CryEngine": {"price": 1000, "rarity": "legendary"},
    "🦴 Dragonclaw Hook": {"price": 375, "rarity": "epic"},
    "🚜 МТЗ-82": {"price": 250, "rarity": "uncommon"},
    "🚜 Беларус-1221": {"price": 500, "rarity": "rare"},
    "🚜 John Deere": {"price": 1000, "rarity": "epic"},
    "🚜 Fendt": {"price": 1750, "rarity": "legendary"},
    "🚜 К-700": {"price": 2500, "rarity": "legendary"},
    "🚜 К-744": {"price": 3750, "rarity": "artifact"},
    "🧱 Кирпич из Минска": {"price": 60, "rarity": "common"},
    "🐸 Жаба": {"price": 300, "rarity": "rare"},
    "🧠 нейрон": {"price": 450, "rarity": "epic"},
    "🔥 Лицензия на огонь": {"price": 900, "rarity": "epic"},
    "💎 Алмазная анальная пробка": {"price": 2250, "rarity": "legendary"},
    "👑 Атом Лёхи Пружины": {"price": 5000, "rarity": "artifact"},
    "📖 26 том магической битвы": {"price": 200, "rarity": "rare"}
}


cases = {
    "🗑️ Мусор дроп": {
        "price": 5,
        "money": (0, 3),
        "weight": 45,
        "item_chance": 0.18,
        "unlock": 1,
        "loot": {
            "🧦 Чулок": 40,
            "💾 Ubuntu": 10,
            "💾 Debian": 5,
            "⚡ Lit Energy": 3
        }
    },
    "🥔 Кейс лукашенко": {
        "price": 20,
        "money": (0, 10),
        "weight": 25,
        "item_chance": 0.22,
        "unlock": 2,
        "loot": {
            "🧱 Кирпич из Минска": 40,
            "⚡ Lit Energy": 20,
            "⚡ Monster": 15,
            "🚜 МТЗ-82": 5,
            "🚜 Беларус-1221": 4,
            "🚜 John Deere": 1
        }
    },
    "🐸 Кейс жаби жаби": {
        "price": 50,
        "money": (1, 20),
        "weight": 16,
        "item_chance": 0.25,
        "unlock": 3,
        "loot": {
            "🐸 Жаба": 38,
            "💜 Аметист": 27,
            "⚡ Monster": 20,
            "⚡ Red Bull": 11,
            "💾 Fedora": 4
        }
    },
    "💀 Кейс головного мозга": {
        "price": 100,
        "money": (2, 35),
        "weight": 8,
        "item_chance": 0.28,
        "unlock": 4,
        "loot": {
            "🧠 нейрон": 39,
            "🎮 Godot": 27,
            "💾 Manjaro": 17,
            "🦴 Dragonclaw Hook": 8,
            "🎮 Unity": 6,
            "💾 Arch Linux": 3
        }
    },
    "🔥 Хз огонь": {
        "price": 250,
        "money": (5, 80),
        "weight": 4,
        "item_chance": 0.31,
        "unlock": 5,
        "loot": {
            "🔥 Лицензия на огонь": 29,
            "🎮 Unity": 23,
            "🎮 Unreal Engine": 19,
            "🎮 Source Engine": 13,
            "💾 Arch Linux": 9,
            "💾 Gentoo": 5,
            "🎮 CryEngine": 2
        }
    },
    "💎 Кейс алмазик": {
        "price": 500,
        "money": (10, 150),
        "weight": 1.5,
        "item_chance": 0.34,
        "unlock": 7,
        "loot": {
            "💎 Алмазная анальная пробка": 25,
            "🚜 Fendt": 22,
            "🚜 К-700": 18,
            "🚜 К-744": 7,
            "🎮 CryEngine": 12,
            "🦴 Dragonclaw Hook": 10,
            "💾 Gentoo": 6
        }
    },
    "👑 Кейс Лёхи Пружины": {
        "price": 1000,
        "money": (20, 300),
        "weight": 0.5,
        "item_chance": 0.38,
        "unlock": 10,
        "loot": {
            "👑 Атом Лёхи Пружины": 8,
            "🚜 К-744": 15,
            "💎 Алмазная анальная пробка": 20,
            "🎮 CryEngine": 18,
            "🦴 Dragonclaw Hook": 17,
            "💾 Gentoo": 22
        }
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
        "weight": 30,
        "value": 15
    },
    "🪖 Каска инженера (шапка)": {
        "material": "скрап",
        "weight": 25,
        "value": 20
    },
    "🎖️ Фуражка солдата (шапка)": {
        "material": "скрап",
        "weight": 20,
        "value": 25
    },
    "🩺 Шапка медика (шапка)": {
        "material": "скрап",
        "weight": 15,
        "value": 30
    },
    "🕶️ Очки снайпера (шапка)": {
        "material": "скрап",
        "weight": 7,
        "value": 60
    },
    "🧰 Гаечная корона инженера (шапка)": {
        "material": "скрап",
        "weight": 3,
        "value": 150
    },

    "🎩 Цилиндр шпиона (шапка)": {
        "material": "метал",
        "weight": 28,
        "value": 100
    },
    "🥽 Очки подрывника (шапка)": {
        "material": "метал",
        "weight": 23,
        "value": 125
    },
    "🧢 Кепка медика (шапка)": {
        "material": "метал",
        "weight": 18,
        "value": 150
    },
    "🪖 Военная каска (шапка)": {
        "material": "метал",
        "weight": 14,
        "value": 200
    },
    "🤠 Шляпа стрелка (шапка)": {
        "material": "метал",
        "weight": 10,
        "value": 300
    },
    "💼 Чемодан на голове (шапка)": {
        "material": "метал",
        "weight": 5,
        "value": 750
    },
    "👑 Корона Mann Co. (шапка)": {
        "material": "метал",
        "weight": 2,
        "value": 2000
    },

    "🧢 Кепка разведчика Deluxe (шапка)": {
        "material": "мвк",
        "weight": 22,
        "value": 500
    },
    "🪖 Шлем тяжёлого (шапка)": {
        "material": "мвк",
        "weight": 18,
        "value": 600
    },
    "🎩 Цилиндр джентльмена (шапка)": {
        "material": "мвк",
        "weight": 15,
        "value": 750
    },
    "🎃 Тыква на голове (шапка)": {
        "material": "мвк",
        "weight": 12,
        "value": 1000
    },
    "🐴 Маска лошади (шапка)": {
        "material": "мвк",
        "weight": 9,
        "value": 1500
    },
    "🗿 Маска Моаи (шапка)": {
        "material": "мвк",
        "weight": 7,
        "value": 2500
    },
    "🧠 Мозг на голове (шапка)": {
        "material": "мвк",
        "weight": 5,
        "value": 4000
    },
    "🔥 Горящая голова (шапка)": {
        "material": "мвк",
        "weight": 3,
        "value": 7000
    },
    "💎 Алмазная шапка (шапка)": {
        "material": "мвк",
        "weight": 1.5,
        "value": 15000
    },
    "👑 Корона директора Mann Co. (шапка)": {
        "material": "мвк",
        "weight": 0.5,
        "value": 35000
    }
}


anime_titles = {
    "🗿 Абсолют": 30,
    "🕳️ Дэд инсайд": 25,
    "🧍 NPC": 20,
    "🥶 Сигма": 10,
    "🧠 200 IQ": 6,
    "🤫 Анимешник": 4,
    "⚡ Протагонист": 3,
    "💀 Последний нейрон": 1,
    "🔥 Главный герой": 0.8,
    "👑 Избранный": 0.2
}


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
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

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item TEXT,
            amount INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, item)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS titles (
            user_id INTEGER,
            title TEXT,
            PRIMARY KEY(user_id, title)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS hats (
            user_id INTEGER,
            hat TEXT,
            amount INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, hat)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            author TEXT,
            content TEXT UNIQUE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id INTEGER PRIMARY KEY,
            work_until INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def ensure_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user_id,)
    )

    if c.fetchone() is None:
        c.execute("""
            INSERT INTO users
            (user_id, coins, level, xp, scrap, metal, mvk)
            VALUES (?, 50, 1, 0, 0, 0, 0)
        """, (user_id,))

    conn.commit()
    conn.close()


def get_balance(user_id):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT coins FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = c.fetchone()
    conn.close()

    return result[0]


def add_coins(user_id, amount):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE users SET coins = coins + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()


def remove_coins(user_id, amount):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT coins FROM users WHERE user_id = ?",
        (user_id,)
    )

    balance = c.fetchone()[0]

    if balance < amount:
        conn.close()
        return False

    c.execute(
        "UPDATE users SET coins = coins - ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

    return True


def add_item(user_id, item, amount=1):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO inventory (user_id, item, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item)
        DO UPDATE SET amount = amount + excluded.amount
    """, (user_id, item, amount))

    conn.commit()
    conn.close()


def add_hat(user_id, hat, amount=1):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO hats (user_id, hat, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, hat)
        DO UPDATE SET amount = amount + excluded.amount
    """, (user_id, hat, amount))

    conn.commit()
    conn.close()


def get_hat_inventory(user_id):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT hat, amount FROM hats WHERE user_id = ? AND amount > 0",
        (user_id,)
    )

    result = c.fetchall()
    conn.close()

    return result


def has_hat(user_id, hat):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT amount FROM hats WHERE user_id = ? AND hat = ?",
        (user_id, hat)
    )

    result = c.fetchone()
    conn.close()

    return result is not None and result[0] > 0


def add_xp(user_id, amount):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT level, xp FROM users WHERE user_id = ?",
        (user_id,)
    )

    level, xp = c.fetchone()
    xp += amount

    while xp >= level * 100:
        xp -= level * 100
        level += 1

    c.execute(
        "UPDATE users SET level = ?, xp = ? WHERE user_id = ?",
        (level, xp, user_id)
    )

    conn.commit()
    conn.close()


def get_scrap_reward(item):
    rarity = items[item]["rarity"]

    if rarity == "common":
        return 2, 0, 0

    if rarity == "uncommon":
        return 2, 1, 0

    if rarity == "rare":
        return 0, 3, 0

    if rarity == "epic":
        return 0, 1, 1

    if rarity == "legendary":
        return 0, 0, 2

    if rarity == "artifact":
        return 0, 0, 4

    return 0, 0, 0


def case_value(money, item):
    value = money

    if item:
        value += items[item]["price"] * 0.7

    return value


def roll_case(case_name):
    case = cases[case_name]

    money = random.randint(
        case["money"][0],
        case["money"][1]
    )

    item = None

    if random.random() <= case["item_chance"]:
        names = list(case["loot"].keys())
        weights = list(case["loot"].values())
        item = random.choices(names, weights=weights, k=1)[0]

    return money, item


def roll_hat(material):
    available = [
        hat for hat, data in hats.items()
        if data["material"] == material
    ]

    weights = [
        hats[hat]["weight"]
        for hat in available
    ]

    return random.choices(
        available,
        weights=weights,
        k=1
    )[0]


def normalize_name(text):
    text = text.strip().lower()
    text = re.sub(r"\s*\(шапка\)\s*$", "", text)
    text = " ".join(text.split())

    parts = text.split(" ", 1)

    if len(parts) == 2:
        first = parts[0]
        if any(ord(char) > 10000 for char in first):
            text = parts[1]

    return text


def find_item_in_inventory(user_id, input_name):
    normalized = normalize_name(input_name)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT item, amount FROM inventory WHERE user_id = ? AND amount > 0",
        (user_id,)
    )

    inventory = c.fetchall()
    conn.close()

    for item, amount in inventory:
        if normalize_name(item) == normalized:
            return item, amount

    return None, 0


def find_hat_in_inventory(user_id, input_name):
    normalized = normalize_name(input_name)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT hat, amount FROM hats WHERE user_id = ? AND amount > 0",
        (user_id,)
    )

    inventory = c.fetchall()
    conn.close()

    for hat, amount in inventory:
        if normalize_name(hat) == normalized:
            return hat, amount

    return None, 0


def find_case(input_name):
    normalized = normalize_name(input_name)

    for case_name in cases:
        if normalize_name(case_name) == normalized:
            return case_name

    return None


def get_title_inventory(user_id):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT title FROM titles WHERE user_id = ?",
        (user_id,)
    )

    result = [row[0] for row in c.fetchall()]
    conn.close()

    return result


def add_title(user_id, title):
    ensure_user(user_id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO titles (user_id, title)
        VALUES (?, ?)
    """, (user_id, title))

    conn.commit()
    conn.close()


class InventoryView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(
        label="Продать всё",
        style=discord.ButtonStyle.green
    )
    async def sell_all(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Это не твой инвентарь.",
                ephemeral=True
            )
            return

        ensure_user(self.user_id)

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "SELECT item, amount FROM inventory WHERE user_id = ? AND amount > 0",
            (self.user_id,)
        )

        inventory = c.fetchall()

        if not inventory:
            conn.close()

            await interaction.response.send_message(
                "❌ У тебя нет обычных предметов для продажи.",
                ephemeral=True
            )
            return

        total = 0

        for item, amount in inventory:
            if item in items:
                total += items[item]["price"] * amount

        c.execute(
            "DELETE FROM inventory WHERE user_id = ?",
            (self.user_id,)
        )

        c.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (total, self.user_id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"💰 Продано всех обычных предметов на **{total}** монет.\n"
            f"🏆 Титулы и 🎩 шапки не затронуты."
        )


class MogBattleView(discord.ui.View):
    def __init__(self, challenger, opponent, case_name):
        super().__init__(timeout=60)

        self.challenger = challenger
        self.opponent = opponent
        self.case_name = case_name
        self.accepted = None

    @discord.ui.button(
        label="Принять",
        style=discord.ButtonStyle.green
    )
    async def accept(self, interaction, button):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message(
                "❌ Это приглашение не для тебя.",
                ephemeral=True
            )
            return

        if self.accepted is not None:
            await interaction.response.send_message(
                "❌ Баттл уже обработан.",
                ephemeral=True
            )
            return

        self.accepted = True

        case_price = cases[self.case_name]["price"]

        if get_balance(self.challenger.id) < case_price:
            await interaction.response.edit_message(
                content="❌ У вызывающего больше нет денег на кейс.",
                view=None
            )
            self.stop()
            return

        if get_balance(self.opponent.id) < case_price:
            await interaction.response.edit_message(
                content="❌ У соперника недостаточно денег на кейс.",
                view=None
            )
            self.stop()
            return

        remove_coins(self.challenger.id, case_price)
        remove_coins(self.opponent.id, case_price)

        challenger_money, challenger_item = roll_case(self.case_name)
        opponent_money, opponent_item = roll_case(self.case_name)

        if challenger_money:
            add_coins(self.challenger.id, challenger_money)

        if opponent_money:
            add_coins(self.opponent.id, opponent_money)

        if challenger_item:
            add_item(self.challenger.id, challenger_item)

        if opponent_item:
            add_item(self.opponent.id, opponent_item)

        challenger_value = case_value(
            challenger_money,
            challenger_item
        )

        opponent_value = case_value(
            opponent_money,
            opponent_item
        )

        pot = case_price * 2

        if challenger_value > opponent_value:
            winner = self.challenger
            loser = self.opponent

        elif opponent_value > challenger_value:
            winner = self.opponent
            loser = self.challenger

        else:
            add_coins(self.challenger.id, case_price)
            add_coins(self.opponent.id, case_price)

            await interaction.response.edit_message(
                content=(
                    f"⚔️ **МОГ-БАТТЛ**\n\n"
                    f"🎁 Кейс: **{self.case_name}**\n\n"
                    f"{self.challenger.mention}: "
                    f"**{challenger_value:.0f}**\n"
                    f"{self.opponent.mention}: "
                    f"**{opponent_value:.0f}**\n\n"
                    f"🤝 Ничья! Ставки возвращены."
                ),
                view=None
            )

            self.stop()
            return

        add_coins(winner.id, pot)

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "UPDATE users SET wins = wins + 1 WHERE user_id = ?",
            (winner.id,)
        )

        c.execute(
            "UPDATE users SET losses = losses + 1 WHERE user_id = ?",
            (loser.id,)
        )

        conn.commit()
        conn.close()

        add_xp(winner.id, 15)
        add_xp(loser.id, 5)

        challenger_drop = (
            challenger_item if challenger_item else "💰 Только деньги"
        )

        opponent_drop = (
            opponent_item if opponent_item else "💰 Только деньги"
        )

        await interaction.response.edit_message(
            content=(
                f"⚔️ **МОГ-БАТТЛ**\n\n"
                f"🎁 Кейс: **{self.case_name}**\n"
                f"💰 Банк: **{pot}**\n\n"
                f"{self.challenger.mention}\n"
                f"└ {challenger_drop} + {challenger_money} монет\n"
                f"└ Стоимость: **{challenger_value:.0f}**\n\n"
                f"{self.opponent.mention}\n"
                f"└ {opponent_drop} + {opponent_money} монет\n"
                f"└ Стоимость: **{opponent_value:.0f}**\n\n"
                f"🏆 Победитель: **{winner.mention}**\n"
                f"💰 Получает весь банк: **{pot}**"
            ),
            view=None
        )

        self.stop()

    async def on_timeout(self):
        self.accepted = False
        self.stop()


@bot.event
async def on_ready():
    global drop_task

    init_db()

    print(f"Бот запущен: {bot.user} | ID: {bot.user.id}")

    if drop_task is None or drop_task.done():
        drop_task = asyncio.create_task(money_drop_loop())


@bot.command()
async def команды(ctx):
    await ctx.send(
        "**📜 КОМАНДЫ**\n\n"
        "`!баланс` — баланс\n"
        "`!дать @user количество` — передать деньги\n"
        "`!выдать @user количество` — выдать деньги\n"
        "`!работа` — работа\n"
        "`!топ` — топ игроков\n"
        "`!кейсы` — список кейсов\n"
        "`!кейс название` — открыть кейс\n"
        "`!инвентарь` — инвентарь\n"
        "`!продать предмет` — продать предмет или шапку\n"
        "`!утилизировать предмет` — утилизировать обычный предмет\n"
        "`!ресурсы` — ресурсы\n"
        "`!крафт шапка скрап/метал/мвк` — создать шапку\n"
        "`!шапка название` — надеть шапку\n"
        "`!шапка убрать` — снять шапку\n"
        "`!витрина предмет` — поставить предмет на витрину\n"
        "`!витрина убрать` — убрать витрину\n"
        "`!профиль` — профиль\n"
        "`!титулы` — список титулов\n"
        "`!титул название` — установить титул\n"
        "`!титул убрать` — убрать титул\n"
        "`!аниме_кейс` — получить титул\n"
        "`!кубик` — бросить кубик\n"
        "`!монетка` — монетка\n"
        "`!угадай` — угадать число\n"
        "`!цитата` — случайная цитата\n"
        "`!могбатл @user название кейса` — вызвать на мог-баттл\n"
        "`!забрать` — забрать дроп\n"
        "`!дроппинг` — подписка на дропы"
    )


@bot.command()
async def баланс(ctx):
    balance = get_balance(ctx.author.id)

    await ctx.send(
        f"💰 **{ctx.author.display_name}** имеет **{balance}** монет."
    )


@bot.command()
async def дать(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        await ctx.send("Использование: `!дать @user количество`")
        return

    if member.id == ctx.author.id:
        await ctx.send("❌ Нельзя передавать деньги самому себе.")
        return

    if amount <= 0:
        await ctx.send("❌ Количество должно быть положительным.")
        return

    if not remove_coins(ctx.author.id, amount):
        await ctx.send("❌ Недостаточно денег.")
        return

    add_coins(member.id, amount)

    await ctx.send(
        f"💸 {ctx.author.mention} передал "
        f"{member.mention} **{amount}** монет."
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def выдать(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        await ctx.send("Использование: `!выдать @user количество`")
        return

    if amount <= 0:
        await ctx.send("❌ Количество должно быть положительным.")
        return

    add_coins(member.id, amount)

    await ctx.send(
        f"💰 {member.mention} выдано **{amount}** монет."
    )


@bot.command()
async def работа(ctx):
    ensure_user(ctx.author.id)

    now = int(time.time())

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT work_until FROM cooldowns WHERE user_id = ?",
        (ctx.author.id,)
    )

    result = c.fetchone()
    work_until = result[0] if result else 0

    if now < work_until:
        remaining = work_until - now
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        conn.close()

        await ctx.send(
            f"⏳ Работа будет доступна через "
            f"**{hours}ч {minutes}м**."
        )
        return

    reward = random.randint(5, 25)
    xp = random.randint(5, 9)

    c.execute("""
        INSERT INTO cooldowns (user_id, work_until)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET work_until = excluded.work_until
    """, (ctx.author.id, now + 21600))

    conn.commit()
    conn.close()

    add_coins(ctx.author.id, reward)
    add_xp(ctx.author.id, xp)

    message = (
        f"💼 Ты поработал и получил **{reward}** монет "
        f"и **{xp} XP**."
    )

    if random.random() < 0.05:
        add_item(
            ctx.author.id,
            "📖 26 том магической битвы"
        )

        message += (
            "\n📖 А ещё ты каким-то образом нашёл "
            "**26 том магической битвы**!"
        )

    await ctx.send(message)


@bot.command()
async def топ(ctx):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT user_id, coins
        FROM users
        ORDER BY coins DESC
        LIMIT 10
    """)

    rows = c.fetchall()
    conn.close()

    text = "🏆 **ТОП БОГАЧЕЙ**\n\n"

    for index, (user_id, coins) in enumerate(rows, 1):
        user = ctx.guild.get_member(user_id)

        name = user.display_name if user else f"ID {user_id}"

        text += f"**{index}.** {name} — **{coins}** монет\n"

    await ctx.send(text)


@bot.command()
async def кейсы(ctx):
    text = "📦 **КЕЙСЫ**\n\n"

    for name, data in cases.items():
        text += (
            f"{name}\n"
            f"💰 Цена: **{data['price']}**\n"
            f"🔓 Уровень: **{data['unlock']}**\n\n"
        )

    await ctx.send(text)


@bot.command()
async def кейс(ctx, *, case_name=None):
    if not case_name:
        await ctx.send(
            "Использование: `!кейс название кейса`"
        )
        return

    found_case = find_case(case_name)

    if found_case is None:
        await ctx.send("❌ Такого кейса нет.")
        return

    ensure_user(ctx.author.id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT level FROM users WHERE user_id = ?",
        (ctx.author.id,)
    )

    level = c.fetchone()[0]
    conn.close()

    case_data = cases[found_case]

    if level < case_data["unlock"]:
        await ctx.send(
            f"🔒 Этот кейс открывается с **{case_data['unlock']} уровня**."
        )
        return

    if not remove_coins(ctx.author.id, case_data["price"]):
        await ctx.send("❌ Недостаточно денег.")
        return

    async with case_open_lock:
        money, item = roll_case(found_case)

        if money:
            add_coins(ctx.author.id, money)

        if item:
            add_item(ctx.author.id, item)

        add_xp(ctx.author.id, 5)

    text = (
        f"📦 **{found_case}** открыт!\n"
        f"💰 Деньги: **{money}**"
    )

    if item:
        text += f"\n🎁 Предмет: **{item}**"
    else:
        text += "\n🎁 Предмет: ничего"

    await ctx.send(text)


@bot.command()
async def инвентарь(ctx):
    ensure_user(ctx.author.id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT item, amount FROM inventory WHERE user_id = ? AND amount > 0",
        (ctx.author.id,)
    )

    inventory = c.fetchall()

    c.execute(
        "SELECT scrap, metal, mvk, hat, showcase_item, title "
        "FROM users WHERE user_id = ?",
        (ctx.author.id,)
    )

    user_data = c.fetchone()
    conn.close()

    scrap, metal, mvk, equipped_hat, showcase, title = user_data

    text = f"🎒 **Инвентарь {ctx.author.display_name}**\n\n"

    if inventory:
        text += "**📦 Предметы:**\n"

        for item, amount in inventory:
            text += f"{item} ×{amount}\n"
    else:
        text += "📦 Предметов нет.\n"

    text += (
        f"\n**♻️ Ресурсы:**\n"
        f"🪨 Скрап: **{scrap}**\n"
        f"🔩 Метал: **{metal}**\n"
        f"⚙️ МВК: **{mvk}**\n"
    )

    user_hats = get_hat_inventory(ctx.author.id)

    text += "\n**🎩 Шапки:**\n"

    if user_hats:
        for hat, amount in user_hats:
            value = hats[hat]["value"]
            text += f"{hat} ×{amount} — 💰 {value}\n"
    else:
        text += "Нет шапок.\n"

    if equipped_hat:
        text += f"\n🎩 Надета: **{equipped_hat}**"

    if title:
        text += f"\n🏆 Титул: **{title}**"

    if showcase:
        text += f"\n🖼️ Витрина: **{showcase}**"

    await ctx.send(
        text,
        view=InventoryView(ctx.author.id)
    )


@bot.command()
async def продать(ctx, *, item_name=None):
    if not item_name:
        await ctx.send(
            "Использование: `!продать название предмета`"
        )
        return

    ensure_user(ctx.author.id)

    if "титул" in item_name.lower():
        await ctx.send("❌ Титулы продавать нельзя.")
        return

    item, amount = find_item_in_inventory(
        ctx.author.id,
        item_name
    )

    if item is not None:
        price = items[item]["price"]
        total = price * amount

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "DELETE FROM inventory WHERE user_id = ? AND item = ?",
            (ctx.author.id, item)
        )

        c.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (total, ctx.author.id)
        )

        conn.commit()
        conn.close()

        await ctx.send(
            f"💰 Продано **{item}** ×{amount} "
            f"за **{total}** монет."
        )
        return

    hat, hat_amount = find_hat_in_inventory(
        ctx.author.id,
        item_name
    )

    if hat is not None:
        price = hats[hat]["value"]
        total = price * hat_amount

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "DELETE FROM hats WHERE user_id = ? AND hat = ?",
            (ctx.author.id, hat)
        )

        c.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (total, ctx.author.id)
        )

        conn.commit()
        conn.close()

        await ctx.send(
            f"💰 Продана **{hat}** ×{hat_amount} "
            f"за **{total}** монет."
        )
        return

    await ctx.send(
        "❌ У тебя нет такого предмета или шапки."
    )


@bot.command()
async def утилизировать(ctx, *, item_name=None):
    if not item_name:
        await ctx.send(
            "Использование: `!утилизировать название предмета`"
        )
        return

    ensure_user(ctx.author.id)

    hat, hat_amount = find_hat_in_inventory(
        ctx.author.id,
        item_name
    )

    if hat is not None:
        await ctx.send(
            "❌ Шапки нельзя утилизировать.\n"
            f"💰 Продай её через `!продать {hat}` "
            f"за **{hats[hat]['value']}** монет за штуку."
        )
        return

    item, amount = find_item_in_inventory(
        ctx.author.id,
        item_name
    )

    if item is None:
        await ctx.send(
            "❌ У тебя нет такого предмета."
        )
        return

    scrap, metal, mvk = get_scrap_reward(item)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "DELETE FROM inventory WHERE user_id = ? AND item = ?",
        (ctx.author.id, item)
    )

    c.execute("""
        UPDATE users
        SET scrap = scrap + ?,
            metal = metal + ?,
            mvk = mvk + ?
        WHERE user_id = ?
    """, (
        scrap * amount,
        metal * amount,
        mvk * amount,
        ctx.author.id
    ))

    conn.commit()
    conn.close()

    rewards = []

    if scrap:
        rewards.append(f"🪨 +{scrap * amount} скрапа")

    if metal:
        rewards.append(f"🔩 +{metal * amount} металла")

    if mvk:
        rewards.append(f"⚙️ +{mvk * amount} МВК")

    await ctx.send(
        f"♻️ Утилизировано **{item}** ×{amount}.\n"
        + " | ".join(rewards)
    )


@bot.command()
async def ресурсы(ctx):
    ensure_user(ctx.author.id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT scrap, metal, mvk FROM users WHERE user_id = ?",
        (ctx.author.id,)
    )

    scrap, metal, mvk = c.fetchone()

    conn.close()

    await ctx.send(
        f"♻️ **Твои ресурсы**\n\n"
        f"🪨 Скрап: **{scrap}**\n"
        f"🔩 Метал: **{metal}**\n"
        f"⚙️ МВК: **{mvk}**"
    )


@bot.command()
async def крафт(ctx, category=None, material=None):
    if category is None or material is None:
        await ctx.send(
            "Использование: `!крафт шапка скрап/метал/мвк`"
        )
        return

    if category.lower() != "шапка":
        await ctx.send(
            "❌ Сейчас можно крафтить только шапки."
        )
        return

    material = material.lower()

    if material not in materials:
        await ctx.send(
            "❌ Материал должен быть: `скрап`, `метал` или `мвк`."
        )
        return

    ensure_user(ctx.author.id)

    column = {
        "скрап": "scrap",
        "метал": "metal",
        "мвк": "mvk"
    }[material]

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        f"SELECT {column} FROM users WHERE user_id = ?",
        (ctx.author.id,)
    )

    amount = c.fetchone()[0]

    if amount < 3:
        conn.close()

        await ctx.send(
            f"❌ Нужно **3 {material}**."
        )
        return

    c.execute(
        f"UPDATE users SET {column} = {column} - 3 WHERE user_id = ?",
        (ctx.author.id,)
    )

    conn.commit()
    conn.close()

    chances = {
        "скрап": 0.70,
        "метал": 0.55,
        "мвк": 0.40
    }

    if random.random() > chances[material]:
        await ctx.send(
            f"💥 Крафт провалился.\n"
            f"Потрачено: **3 {material}**."
        )
        return

    hat = roll_hat(material)

    add_hat(ctx.author.id, hat)

    value = hats[hat]["value"]

    await ctx.send(
        f"🎩 **КРАФТ УСПЕШЕН!**\n\n"
        f"Ты получил: **{hat}**\n"
        f"💰 Цена продажи: **{value}** монет"
    )


@bot.command()
async def шапка(ctx, *, hat_name=None):
    if not hat_name:
        await ctx.send(
            "Использование: `!шапка название` или `!шапка убрать`"
        )
        return

    ensure_user(ctx.author.id)

    if hat_name.lower() == "убрать":
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "UPDATE users SET hat = NULL WHERE user_id = ?",
            (ctx.author.id,)
        )

        conn.commit()
        conn.close()

        await ctx.send("🎩 Шапка снята.")
        return

    hat, amount = find_hat_in_inventory(
        ctx.author.id,
        hat_name
    )

    if hat is None:
        await ctx.send(
            "❌ У тебя нет такой шапки."
        )
        return

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE users SET hat = ? WHERE user_id = ?",
        (hat, ctx.author.id)
    )

    conn.commit()
    conn.close()

    await ctx.send(
        f"🎩 Теперь на тебе **{hat}**."
    )


@bot.command()
async def витрина(ctx, *, item_name=None):
    if not item_name:
        await ctx.send(
            "Использование: `!витрина предмет` или `!витрина убрать`"
        )
        return

    ensure_user(ctx.author.id)

    if item_name.lower() == "убрать":
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "UPDATE users SET showcase_item = NULL WHERE user_id = ?",
            (ctx.author.id,)
        )

        conn.commit()
        conn.close()

        await ctx.send("🖼️ Витрина очищена.")
        return

    item, amount = find_item_in_inventory(
        ctx.author.id,
        item_name
    )

    if item is None:
        hat, hat_amount = find_hat_in_inventory(
            ctx.author.id,
            item_name
        )

        if hat is None:
            await ctx.send(
                "❌ У тебя нет такого предмета или шапки."
            )
            return

        item = hat

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE users SET showcase_item = ? WHERE user_id = ?",
        (item, ctx.author.id)
    )

    conn.commit()
    conn.close()

    await ctx.send(
        f"🖼️ На витрину выставлено **{item}**."
    )


@bot.command()
async def профиль(ctx):
    ensure_user(ctx.author.id)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT coins, wins, losses, title, showcase_item,
               level, xp, hat
        FROM users
        WHERE user_id = ?
    """, (ctx.author.id,))

    data = c.fetchone()
    conn.close()

    coins, wins, losses, title, showcase, level, xp, hat = data

    embed = discord.Embed(
        title=f"👤 Профиль {ctx.author.display_name}"
    )

    embed.set_thumbnail(
        url=ctx.author.display_avatar.url
    )

    embed.add_field(
        name="💰 Баланс",
        value=f"{coins} монет",
        inline=True
    )

    embed.add_field(
        name="🏆 Победы",
        value=str(wins),
        inline=True
    )

    embed.add_field(
        name="💀 Поражения",
        value=str(losses),
        inline=True
    )

    embed.add_field(
        name="⭐ Уровень",
        value=f"{level} ({xp}/{level * 100} XP)",
        inline=True
    )

    embed.add_field(
        name="🎩 Шапка",
        value=hat or "Нет",
        inline=False
    )

    embed.add_field(
        name="🏆 Титул",
        value=title or "Нет",
        inline=False
    )

    embed.add_field(
        name="🖼️ Витрина",
        value=showcase or "Нет",
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def титулы(ctx):
    owned = get_title_inventory(ctx.author.id)

    text = "🏆 **ТИТУЛЫ**\n\n"

    for title, chance in anime_titles.items():
        status = "✅" if title in owned else "🔒"

        text += (
            f"{status} {title} — **{chance}%**\n"
        )

    await ctx.send(text)


@bot.command()
async def титул(ctx, *, title_name=None):
    if not title_name:
        await ctx.send(
            "Использование: `!титул название` или `!титул убрать`"
        )
        return

    ensure_user(ctx.author.id)

    if title_name.lower() == "убрать":
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "UPDATE users SET title = NULL WHERE user_id = ?",
            (ctx.author.id,)
        )

        conn.commit()
        conn.close()

        await ctx.send("🏆 Титул снят.")
        return

    owned = get_title_inventory(ctx.author.id)

    found = None

    for title in owned:
        if title.lower() == title_name.lower():
            found = title
            break

    if found is None:
        await ctx.send(
            "❌ У тебя нет такого титула."
        )
        return

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE users SET title = ? WHERE user_id = ?",
        (found, ctx.author.id)
    )

    conn.commit()
    conn.close()

    await ctx.send(
        f"🏆 Теперь твой титул: **{found}**"
    )


@bot.command()
async def аниме_кейс(ctx):
    roll = random.random() * 100

    current = 0
    result = None

    for title, chance in anime_titles.items():
        current += chance

        if roll <= current:
            result = title
            break

    if result is None:
        result = "🗿 Абсолют"

    add_title(ctx.author.id, result)

    await ctx.send(
        f"🎴 **АНИМЕ-КЕЙС**\n\n"
        f"Ты получил титул: **{result}**"
    )


@bot.command()
async def кубик(ctx):
    number = random.randint(1, 6)

    await ctx.send(
        f"🎲 Выпало: **{number}**"
    )


@bot.command()
async def монетка(ctx):
    result = random.choice(
        ["🪙 Орёл", "🪙 Решка"]
    )

    await ctx.send(
        f"Монетка: **{result}**"
    )


@bot.command()
async def угадай(ctx):
    number = random.randint(1, 10)

    await ctx.send(
        f"🔮 Я загадал число от **1 до 10**.\n"
        f"Попробуй угадать командой `!угадай число`."
    )

    def check(message):
        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and message.content.startswith("!угадай ")
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=30,
            check=check
        )

        try:
            guess = int(message.content.split()[1])
        except:
            await ctx.send("❌ Нужно написать число.")
            return

        if guess == number:
            await ctx.send(
                f"🎉 Угадал! Это было **{number}**!"
            )
        else:
            await ctx.send(
                f"❌ Не угадал. Было **{number}**."
            )

    except asyncio.TimeoutError:
        await ctx.send(
            f"⏰ Время вышло. Я загадал **{number}**."
        )


@bot.command()
async def цитата(ctx):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT author, content
        FROM quotes
        ORDER BY RANDOM()
        LIMIT 1
    """)

    quote = c.fetchone()
    conn.close()

    if quote is None:
        await ctx.send("📖 Цитат пока нет.")
        return

    author, content = quote

    await ctx.send(
        f"📖 **ЦИТАТА**\n\n"
        f"> {content}\n\n"
        f"— {author}"
    )


@bot.command()
async def могбатл(
    ctx,
    opponent: discord.Member = None,
    *,
    case_name=None
):
    if opponent is None or case_name is None:
        await ctx.send(
            "Использование:\n"
            "`!могбатл @user название кейса`"
        )
        return

    if opponent.bot:
        await ctx.send(
            "❌ Нельзя вызвать бота на мог-баттл."
        )
        return

    if opponent.id == ctx.author.id:
        await ctx.send(
            "❌ Нельзя вызвать самого себя."
        )
        return

    found_case = find_case(case_name)

    if found_case is None:
        await ctx.send(
            "❌ Такого кейса нет. Посмотри `!кейсы`."
        )
        return

    price = cases[found_case]["price"]

    if get_balance(ctx.author.id) < price:
        await ctx.send(
            f"❌ У тебя недостаточно денег. "
            f"Нужно **{price}** монет."
        )
        return

    if get_balance(opponent.id) < price:
        await ctx.send(
            f"❌ У {opponent.mention} недостаточно денег "
            f"для этого баттла."
        )
        return

    view = MogBattleView(
        ctx.author,
        opponent,
        found_case
    )

    await ctx.send(
        f"⚔️ **{ctx.author.mention} вызывает "
        f"{opponent.mention} на МОГ-БАТТЛ!**\n\n"
        f"📦 Кейс: **{found_case}**\n"
        f"💰 Ставка каждого: **{price}**\n"
        f"🏦 Банк: **{price * 2}**\n\n"
        f"Соперник должен нажать **Принять**.",
        view=view
    )


async def money_drop_loop():
    global active_drop

    await bot.wait_until_ready()

    while not bot.is_closed():
        await asyncio.sleep(
            random.randint(600, 2400)
        )

        channel = bot.get_channel(DROP_CHANNEL_ID)

        if channel is None:
            continue

        roll = random.random()

        if roll < 0.003:
            amount = random.randint(200, 400)
            drop_type = "💎 УЛЬТРА-ДРОП"

        elif roll < 0.018:
            amount = random.randint(80, 180)
            drop_type = "🔥 МЕГА-ДРОП"

        elif roll < 0.078:
            amount = random.randint(30, 80)
            drop_type = "💰 ЖИРНЫЙ ДРОП"

        else:
            amount = random.randint(5, 30)
            drop_type = "💸 ДРОП"

        role = discord.utils.get(
            channel.guild.roles,
            name=DROP_ROLE_NAME
        )

        mention = role.mention if role else ""

        active_drop = {
            "amount": amount,
            "channel_id": channel.id,
            "expires": time.time() + 30
        }

        await channel.send(
            f"{mention}\n"
            f"🎁 **{drop_type}**\n"
            f"💰 На земле лежит **{amount}** монет!\n\n"
            f"Первый пишет `!забрать` — тот забирает дроп.\n"
            f"⏳ У тебя 30 секунд!"
        )

        await asyncio.sleep(30)

        if active_drop is not None:
            active_drop = None

            await channel.send(
                "💨 Дроп исчез — никто не успел его забрать."
            )


@bot.command()
async def забрать(ctx):
    global active_drop

    if active_drop is None:
        await ctx.send(
            "❌ Сейчас нет активного дропа."
        )
        return

    if active_drop["channel_id"] != ctx.channel.id:
        await ctx.send(
            "❌ Этот дроп находится в другом канале."
        )
        return

    if time.time() > active_drop["expires"]:
        active_drop = None

        await ctx.send(
            "❌ Дроп уже исчез."
        )
        return

    amount = active_drop["amount"]
    active_drop = None

    add_coins(ctx.author.id, amount)

    await ctx.send(
        f"🎉 {ctx.author.mention} забрал дроп!\n"
        f"💰 Получено: **{amount}** монет."
    )


@bot.command()
async def дроппинг(ctx):
    if ctx.guild is None:
        return

    role = discord.utils.get(
        ctx.guild.roles,
        name=DROP_ROLE_NAME
    )

    if role is None:
        await ctx.send(
            f"❌ Роль **{DROP_ROLE_NAME}** не найдена."
        )
        return

    if role in ctx.author.roles:
        try:
            await ctx.author.remove_roles(role)
            await ctx.send(
                "🔕 Ты больше не подписан на дропы."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ Боту не хватает прав для изменения роли."
            )
    else:
        try:
            await ctx.author.add_roles(role)
            await ctx.send(
                "🔔 Ты подписался на дропы!"
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ Боту не хватает прав для изменения роли."
            )


@bot.event
async def on_raw_reaction_add(payload):
    if bot.user is None:
        return

    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != "🐊":
        return

    channel = bot.get_channel(payload.channel_id)

    if channel is None:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except:
        return

    count = 0

    for reaction in message.reactions:
        if str(reaction.emoji) == "🐊":
            count = reaction.count
            break

    if count < 2:
        return

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT id FROM quotes WHERE content = ?",
        (message.content,)
    )

    if c.fetchone() is not None:
        conn.close()
        return

    author = message.author.display_name

    c.execute(
        """
        INSERT INTO quotes (user_id, author, content)
        VALUES (?, ?, ?)
        """,
        (
            message.author.id,
            author,
            message.content
        )
    )

    conn.commit()
    conn.close()

    await channel.send(
        f"📖 **ЦИТАТА ЗАФИКСИРОВАНА**\n"
        f"> {message.content}\n"
        f"— {author}"
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ У тебя нет прав для этой команды."
        )
        return

    if isinstance(error, commands.MemberNotFound):
        await ctx.send(
            "❌ Пользователь не найден."
        )
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Неверный аргумент команды."
        )
        return

    if isinstance(error, commands.CommandOnCooldown):
        return

    print(f"Ошибка команды {ctx.command}: {error}")


init_db()

bot.run(TOKEN)
