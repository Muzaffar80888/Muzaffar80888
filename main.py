import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
import wikipedia

# Wikipedia tili o'zbekchaga o'rnatiladi
wikipedia.set_lang('uz')

# Bot token
TOKEN = 'botini apisini yozasanla'

# Dispatcher yaratish
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Assalomu alaykum, {html.bold(message.from_user.full_name)}!")


# Qur'on bot komandasi
@dp.message(Command('quron'))
async def quron_bot(message: Message) -> None:
    await message.answer("Iltimos, sura va oyat raqamini kiriting (masalan: 1 1)")


# Wikipedia bot komandasi
@dp.message(Command('wikipediya'))
async def wiki_bot(message: Message) -> None:
    await message.answer("Iltimos, qidiriladigan matnni kiriting.")


# Foydalanuvchi xabar yuborganda, uni ko'rib chiqadigan funksiya
@dp.message()
async def message_handler(message: Message) -> None:
    # Agar foydalanuvchi Qur'on raqamlari yuborgan bo'lsa
    try:
        # Qur'on qidiruvi
        if message.text.isdigit() or len(message.text.split()) == 2:
            son = message.text.split()
            if len(son) != 2:
                await message.reply("Sura va oyat raqamlarini to'g'ri formatda kiriting. (masalan: 1 1)")
                return

            surah = son[0]  # Sura raqami
            ayah = son[1]  # Oyat raqami

            # Qur'on API orqali sura va oyat tarjimasini olish
            url_uz = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/uzb-alauddinmansour/{surah}/{ayah}.json"
            url_arb = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/ara-quranuthmanihaf/{surah}/{ayah}.json"
            r = requests.get(url_uz)
            r_a = requests.get(url_arb)
            res = r.json()
            res_a = r_a.json()


            if 'text' in res:
                await message.reply(f"Qur'on {surah}-suvra {ayah}-oyat\n\n{html.bold(res_a['text'])}\n\n\n"
                                    f"Qur'on {surah}-suvra {ayah}-oyat\n\n{res['text']}")
            else:
                await message.reply("Oyat topilmadi. Iltimos, to'g'ri raqamlarni kiriting.")
            return

        # Agar foydalanuvchi boshqa ma'lumot qidirsa (Wikipedia qidiruvi)
        query = message.text
        summary = wikipedia.summary(query, sentences=3)
        await message.reply(summary)

    except wikipedia.exceptions.DisambiguationError as e:
        await message.reply(f"Ko'p ma'lumot topildi: {e.options}")
    except wikipedia.exceptions.PageError:
        await message.reply("Maqola topilmadi.")
    except Exception as e:
        logging.error(e)
        await message.reply("Xatolik yuz berdi, keyinroq qayta urinib ko'ring.")


# Asosiy funksiya
async def main() -> None:
    # Botni yaratish
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Polling orqali botni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
