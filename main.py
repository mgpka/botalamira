# main.py
import os
import asyncio
import logging
from aiohttp import web
from hydrogram import Client, filters, enums, idle
from hydrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from hydrogram.enums import ChatMemberStatus

import config
import database as db
from ai_engine import ask_gemini

# ==========================================
# 0. خادم ويب داخلي مخصص لإرضاء فحص Render والسيرفرات
# ==========================================
async def start_web_server():
    async def handle(request):
        return web.Response(text="سورس الأمراء شغال أونلاين بنجاح! 🚀")

    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 تم تشغيل منفذ الويب الداخلي بنجاح على البورت: {port}")

# ==========================================
# 1. إعداد عميل البوت
# ==========================================
app = Client(
    "AlOmaraa_Bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# كيبورد المطور الخاص
DEV_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("قسم الاشتراك الاجباري ▽"), KeyboardButton("اوامر الاذاعه ▽")],
        [KeyboardButton("قسم اوامر المسح ▽")],
        [KeyboardButton("قسم التفعيل والتعطيل ▽"), KeyboardButton("قسم الاحصائيات والنسخ ▽")],
        [KeyboardButton("المطورين ▽"), KeyboardButton("المطورين الثانويين ▽")],
        [KeyboardButton("المطورين الاساسيين ▽")],
        [KeyboardButton("تغيير اسم البوت ▽"), KeyboardButton("قائمه العام ▽")],
        [KeyboardButton("تغيير المطور الاساسي ▽")],
        [KeyboardButton("اشتراك البوت ▽"), KeyboardButton("ضع تاريخ الاشتراك ▽")],
        [KeyboardButton("معلومات التنصيب ▽"), KeyboardButton("ضع صوره للترحيب ▽")],
        [KeyboardButton("تغيير كليشه ستارت ▽"), KeyboardButton("تغيير كليشه المطور ▽")],
        [KeyboardButton("تنظيف المشتركين ▽"), KeyboardButton("تنظيف المجموعات ▽")],
        [KeyboardButton("اعلان البوت ▽")],
        [KeyboardButton("الردود العامه ▽"), KeyboardButton("اضف رد عام ▽")],
        [KeyboardButton("تحديث السورس ▽"), KeyboardButton("تحديث الملفات ▽")],
        [KeyboardButton("مسح تخزين البوت ▽")]
    ],
    resize_keyboard=True
)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    print(f"📩 وصل أمر ستارت من المستخدم: {message.from_user.id}")
    try:
        user_id = message.from_user.id
        dev_id = int(config.DEV_ID)

        # تنظيف المعرفات تلقائياً من علامة @ لضمان صحة روابط تيليجرام
        raw_dev = str(config.DEV_USER).replace("@", "").strip()
        raw_channel = str(config.SOURCE_CHANNEL).replace("@", "").strip()
        channel_url = f"https://t.me/{raw_channel}" if not str(config.SOURCE_CHANNEL).startswith("http") else str(config.SOURCE_CHANNEL)
        dev_url = f"https://t.me/{raw_dev}"

        if user_id == dev_id:
            caption = (
                "▽ : اهلا بك عزيزي المطور\n"
                "▽ : اليك اوامر الكيبورد الخاصه بك\n"
                f"▽ : قناة السورس والتحديثات\n"
                f"- {channel_url}"
            )
            return await message.reply_text(caption, reply_markup=DEV_KEYBOARD)

        welcome_text = (
            f"▽ : أهلا بك في بوت {config.BOT_NAME}\n"
            "▽ : لحماية المجموعات من التفليش\n"
            "▽ : يمكنك تفعيل البوت كالاتي :\n"
            "▽ : اضف البوت وارفعه مشرف في مجموعتك\n"
            "▽ : ارسل {{ تفعيل }} ليتم تفعيل المجموعه\n"
            f"▽ : يوزر البوت ← @{client.me.username}"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ اضفني لمجموعتك", url=f"https://t.me/{client.me.username}?startgroup=true"),
                InlineKeyboardButton("قناه البوت ↗️", url=channel_url)
            ],
            [
                InlineKeyboardButton("لتنصيب بوت ↗️", url=dev_url),
                InlineKeyboardButton("المطور ↗️", url=dev_url)
            ],
            [InlineKeyboardButton("سورس الأمراء ™️", url=channel_url)]
        ])
        await message.reply_text(welcome_text, reply_markup=buttons)
    except Exception as e:
        print(f"❌ حدث خطأ أثناء معالجة أمر ستارت: {e}")
        await message.reply_text("أهلاً بك في البوت! (تم استلام الأمر بنجاح).")

@app.on_message(filters.command(["المطور", "مطور"], prefixes="") & filters.group)
async def dev_command(client: Client, message: Message):
    try:
        raw_channel = str(config.SOURCE_CHANNEL).replace("@", "").strip()
        channel_url = f"https://t.me/{raw_channel}" if not str(config.SOURCE_CHANNEL).startswith("http") else str(config.SOURCE_CHANNEL)
        
        dev_chat = await client.get_chat(int(config.DEV_ID))
        caption = (
            "- 𝗠𝗲𝗲𝘁 𝗧𝗵𝗲 𝗖𝗿𝗲𝗮𝘁𝗼𝗿 🌟 :\n\n"
            f"» 𝗡𝗮𝗺𝗲: {config.DEV_NAME} 𓆩\n"
            f"» 𝗨𝘀𝗲𝗿: @{str(config.DEV_USER).replace('@', '')}\n"
            f"» 𝗕𝗶𝗼: {dev_chat.bio or 'إِنَّ رَبِّي لَطِيفٌ لِّمَا يَشَاءُ إِنَّهُ هُوَ الْعَلِيمُ الْحَكِيمُ'}\n\n"
            "- 𝗦𝗲𝗲 𝗮 𝘀𝘁𝗼𝗿𝘆 𝘁𝗵𝗿𝗼𝘂𝗴𝗵 𝗵𝗶𝘀 𝘄𝗼𝗿𝗱𝘀 🌠."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("لحظات الأمراء | moments princes ↗️", url=channel_url)]
        ])
        photos = [p async for p in client.get_chat_photos(int(config.DEV_ID), limit=1)]
        if photos:
            await message.reply_photo(photo=photos[0].file_id, caption=caption, reply_markup=buttons)
        else:
            await message.reply_text(caption, reply_markup=buttons)
    except Exception as e:
        await message.reply_text(f"المطور: @{str(config.DEV_USER).replace('@', '')}")

@app.on_message(filters.command(["تفعيل"], prefixes="") & filters.group)
async def activate_grp(client: Client, message: Message):
    await db.set_group_status(message.chat.id, message.chat.title, True)
    await message.reply_text(f"✓ تم تفعيل المجموعة بنجاح وتثبيت حماية {config.BOT_NAME} 🛡️")

@app.on_message(filters.command(["تعطيل"], prefixes="") & filters.group)
async def deactivate_grp(client: Client, message: Message):
    await db.set_group_status(message.chat.id, message.chat.title, False)
    await message.reply_text("✗ تم تعطيل البوت في هذه المجموعة.")

@app.on_message(filters.group & ~filters.bot)
async def ai_chat_handler(client: Client, message: Message):
    if message.from_user:
        await db.add_user_messages(message.from_user.id, 1)

    if not message.text:
        return

    text = message.text.strip()
    bot_name = config.BOT_NAME
    bot_username = client.me.username

    is_reply_to_bot = (
        message.reply_to_message and 
        message.reply_to_message.from_user and 
        message.reply_to_message.from_user.id == client.me.id
    )
    is_called_by_name = text.startswith(bot_name) or f"@{bot_username}" in text

    if is_reply_to_bot or is_called_by_name:
        clean_text = text.replace(bot_name, "").replace(f"@{bot_username}", "").strip()
        if not clean_text:
            clean_text = "هلا شكو ماكو؟"
        await client.send_chat_action(message.chat.id, action=enums.ChatAction.TYPING)
        reply = await ask_gemini(clean_text)
        await message.reply_text(reply)

# ==========================================
# 2. دالة التشغيل الرئيسية
# ==========================================
async def main():
    await start_web_server()

    print("⏳ جاري فحص الاتصال بقاعدة بيانات MongoDB...")
    try:
        db_connected = await asyncio.wait_for(db.ping_db(), timeout=5)
        if db_connected:
            print("✅ تم الاتصال بقاعدة بيانات MongoDB بنجاح!")
    except Exception as e:
        print(f"⚠️ تنبيه قاعدة البيانات: {e}")

    print("🚀 جاري إطلاق سورس الأمراء...")
    await app.start()
    print(f"🤖 البوت شغال الآن بمعرف: @{app.me.username}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
