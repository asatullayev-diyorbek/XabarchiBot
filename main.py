import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env faylini yuklash
load_dotenv()

# Bot uchun token va admin ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Admin ID

# Botni sozlash
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ma'lumotlar bazasi sozlamalari
DATABASE_URL = os.getenv("DATABASE_URL")  # .env fayldan olish
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Guruh modelini yaratish
class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True)

Base.metadata.create_all(engine)

# Guruhni bazaga qo'shish funksiyasi
def add_group(chat_id):
    if not session.query(Group).filter_by(chat_id=str(chat_id)).first():
        new_group = Group(chat_id=str(chat_id))
        session.add(new_group)
        session.commit()
        return True
    return False

# /activate buyrug'ini qayta ishlash
@dp.message(Command("activate"))
async def activate_group(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Siz ushbu buyruqni ishlata olmaysiz.")
        return

    chat_id = message.chat.id
    if add_group(chat_id):
        await message.reply("Guruh muvaffaqiyatli faollashtirildi!")
    else:
        await message.reply("Ushbu guruh allaqachon faollashtirilgan.")

# Guruhlarga xabar yuborish funksiyasi
async def send_periodic_message():
    while True:
        groups = session.query(Group).all()
        for group in groups:
            try:
                await bot.send_message(
                    group.chat_id,
                    "🚖 <b>Tez va qulay taksi xizmati kerakmi?</b>\n\n"
                    "🛣 Sizni qulay va tez manzilingizga yetkazib qo'yamiz! Endi buyurtma berish yanada oson.\n\n"
                    "🔗 Taksi buyurtma qilish uchun 👉 <a href='https://t.me/BTTaxiBot'>@BTTaxiBot</a> dan foydalaning.\n\n"
                    "✅ Tez, qulay va ishonchli xizmat — siz uchun har doim tayyor!",
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text="🚕 Taksi buyurtma qilish",
                                    url="https://t.me/BTTaxiBot"
                                )
                            ]
                        ]
                    )
                )
            except Exception as e:
                print(f"Guruhga xabar yuborishda xato ({group.chat_id}): {e}")
        await asyncio.sleep(20)  # 10 daqiqa kutish

# Botni ishga tushirish
async def main():
    # Xabar yuborishni fon jarayonida ishga tushirish
    asyncio.create_task(send_periodic_message())

    # Dispatcher polling ni boshlash
    print("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
