# main.py
import asyncio
from hydrogram import Client, filters
from hydrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ChatMemberUpdated
)
from hydrogram.enums import ChatMemberStatus, ChatType

import config
import database as db
from ai_engine import ask_gemini

app = Client(
    "AlOmaraa_Bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# ==========================================
# 1. كيبورد المطور الخاص (Private Dev Panel)
# ==========================================
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

# ==========================================
# 2. أمر البداية (/start)
# ==========================================
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    # إذا كان المرسل هو المطور الأساسي
    if user_id == config.DEV_ID:
        caption = (
            "▽ : اهلا بك عزيزي المطور\n"
            "▽ : اليك اوامر الكيبورد الخاصه بك\n"
            f"▽ : قناة السورس والتحديثات\n"
            f"- {config.SOURCE_CHANNEL}"
        )
        return await message.reply_text(caption, reply_markup=DEV_KEYBOARD)

    # للأعضاء العاديين
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
            InlineKeyboardButton("قناه البوت ↗️", url=config.SOURCE_CHANNEL)
        ],
        [
            InlineKeyboardButton("لتنصيب بوت ↗️", url=f"https://t.me/{config.DEV_USER}"),
            InlineKeyboardButton("المطور ↗️", url=f"https://t.me/{config.DEV_USER}")
        ],
        [
            InlineKeyboardButton("اوامر الاعضاء", callback_data="member_cmds")
        ],
        [
            InlineKeyboardButton("سورس الأمراء ™️", url=config.SOURCE_CHANNEL)
        ]
    ])
    
    await message.reply_text(welcome_text, reply_markup=buttons)

# ==========================================
# 3. أمر المطور
# ==========================================
@app.on_message(filters.command(["المطور", "مطور"], prefixes="") & filters.group)
async def dev_command(client: Client, message: Message):
    try:
        dev_chat = await client.get_chat(config.DEV_ID)
        caption = (
            "- 𝗠𝗲𝗲𝘁 𝗧𝗵𝗲 𝗖𝗿𝗲𝗮𝘁𝗼𝗿 🌟 :\n\n"
            f"» 𝗡𝗮𝗺𝗲: {config.DEV_NAME} 𓆩\n"
            f"» 𝗨𝘀𝗲𝗿: @{config.DEV_USER}\n"
            f"» 𝗕𝗶𝗼: {dev_chat.bio or 'إِنَّ رَبِّي لَطِيفٌ لِّمَا يَشَاءُ إِنَّهُ هُوَ الْعَلِيمُ الْحَكِيمُ'}\n\n"
            "- 𝗦𝗲𝗲 𝗮 𝘀𝘁𝗼𝗿𝘆 𝘁𝗵𝗿𝗼𝘂𝗴𝗵 𝗵𝗶𝘀 𝘄𝗼𝗿𝗱𝘀 🌠."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("لحظات الأمراء | moments princes ↗️", url=config.SOURCE_CHANNEL)]
        ])
        
        photos = [p async for p in client.get_chat_photos(config.DEV_ID, limit=1)]
        if photos:
            await message.reply_photo(photo=photos[0].file_id, caption=caption, reply_markup=buttons)
        else:
            await message.reply_text(caption, reply_markup=buttons)
    except Exception as e:
        await message.reply_text(f"المطور: @{config.DEV_USER}")

# ==========================================
# 4. أمر المالك
# ==========================================
@app.on_message(filters.command(["المالك", "مالك"], prefixes="") & filters.group)
async def owner_command(client: Client, message: Message):
    owner = None
    try:
        async for m in client.get_chat_administrators(message.chat.id):
            if m.status == ChatMemberStatus.OWNER:
                owner = m.user
                break
        
        if not owner:
            return await message.reply_text("تعذر جلب مالك المجموعة.")
        
        owner_chat = await client.get_chat(owner.id)
        caption = (
            "- 𝗢𝘄𝗻𝗲𝗿'𝘀 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 🥇 :\n\n"
            f"» 𝗡𝗮𝗺𝗲: {owner.first_name}\n"
            f"» 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{owner.username or 'لا يوجد'}\n"
            f"» 𝗕𝗶𝗼: {owner_chat.bio or 'لا يوجد بايو'}\n\n"
            "- 𝗦𝗲𝗲 𝘄𝗵𝗼 𝗹𝗲𝗮𝗱𝘀 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 👑."
        )
        
        group_url = f"https://t.me/{message.chat.username}" if message.chat.username else config.SOURCE_CHANNEL
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"+ 🏴‍☠️ {message.chat.title} ま + 🏴‍☠️", url=group_url)]
        ])
        
        photos = [p async for p in client.get_chat_photos(owner.id, limit=1)]
        if photos:
            await message.reply_photo(photo=photos[0].file_id, caption=caption, reply_markup=buttons)
        else:
            await message.reply_text(caption, reply_markup=buttons)
    except Exception as e:
        await message.reply_text("حدث خطأ أثناء جلب معلومات المالك.")

# ==========================================
# 5. التفعيل والتعطيل والأوامر الأساسية
# ==========================================
@app.on_message(filters.command(["تفعيل"], prefixes="") & filters.group)
async def activate_grp(client: Client, message: Message):
    await db.set_group_status(message.chat.id, message.chat.title, True)
    await message.reply_text(f"✓ تم تفعيل المجموعة بنجاح وتثبيت حماية {config.BOT_NAME} 🛡️")

@app.on_message(filters.command(["تعطيل"], prefixes="") & filters.group)
async def deactivate_grp(client: Client, message: Message):
    await db.set_group_status(message.chat.id, message.chat.title, False)
    await message.reply_text("✗ تم تعطيل البوت في هذه المجموعة.")

# ==========================================
# 6. التفاعل الذكي (Google Gemini AI)
# ==========================================
@app.on_message(filters.group & ~filters.bot)
async def ai_chat_handler(client: Client, message: Message):
    # زيادة عداد رسائل العضو في القاعدة
    if message.from_user:
        await db.add_user_messages(message.from_user.id, 1)

    if not message.text:
        return

    text = message.text.strip()
    bot_name = config.BOT_NAME
    bot_username = client.me.username

    # التحقق هل المنشن أو الرسالة موجهة للبوت
    is_reply_to_bot = (
        message.reply_to_message and 
        message.reply_to_message.from_user and 
        message.reply_to_message.from_user.id == client.me.id
    )
    is_called_by_name = text.startswith(bot_name) or f"@{bot_username}" in text

    if is_reply_to_bot or is_called_by_name:
        # إزالة اسم البوت من النص المرسل للذكاء الاصطناعي
        clean_text = text.replace(bot_name, "").replace(f"@{bot_username}", "").strip()
        if not clean_text:
            clean_text = "هلا شكو ماكو؟"
        
        # إرسال إشعار الكتابة
        await client.send_chat_action(message.chat.id, action=enums.ChatAction.TYPING)
        
        # استدعاء Gemini والرد
        reply = await ask_gemini(clean_text)
        await message.reply_text(reply)

# ==========================================
# 7. تشغيل البوت
# ==========================================
async def main():
    print("⏳ جاري فحص الاتصال بقاعدة بيانات MongoDB...")
    db_connected = await db.ping_db()
    if not db_connected:
        print("❌ فشل الاتصال بقاعدة البيانات! يرجى التحقق من الرابط.")
        return
    
    print("✅ تم الاتصال بقاعدة البيانات بنجاح!")
    print("🚀 جاري إطلاق سورس الأمراء...")
    await app.start()
    print(f"🤖 البوت شغال الآن بمعرف: @{app.me.username}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    from hydrogram import enums
    asyncio.run(main())
