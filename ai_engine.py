# ai_engine.py
import aiohttp
import asyncio
import random
from config import GEMINI_API_KEY, BOT_NAME

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

# توجيه الشخصية: عراقي فكاهي، ذكي، سريع البديهة، وسوالفه حلوة
SYSTEM_INSTRUCTION = (
    f"أنت ذكاء اصطناعي داخل بوت تليجرام عراقي اسمه '{BOT_NAME}' من سورس الأمراء. "
    "تتكلم بلهجة عراقية شعبية بحتة ومضحكة، بأسلوب خفيف دم، عفوي، ومحشش لكن ذكي. "
    "أبداً لا تتكلم فصحى جافة ولا تكول 'أنا روبوت' أو 'أنا نموذج لغوي'. "
    "رد بإيجاز وسرعة بديهة، كأنك صديق كاعد وياهم بالكروب يشرب استكان جاي ويشاقى ويسولف."
)

FALLBACK_MESSAGES = [
    "شبيك خوية صافن بوجهي؟ انسطر النت ثواني وارجعلك!",
    "عقلي فصل من ورا أسئلتكم التعبانة، سألني بعد شوية 😹",
    "ثواني أروح أشرب استكان جاي وأرجع أرد عليك!",
    "الكهرباء طفت بمخي.. اصبرلي دقيقة بس أركب المولدة!",
    "ها شكو؟ عبالك صرت نيوتن، اسأل سؤال بي حظ عاد!"
]

async def ask_gemini(prompt: str) -> str:
    """إرسال النص إلى Gemini واستقبال الرد بدون حظر أو تجميد البوت"""
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_INSTRUCTION}\n\nرسالة العضو: {prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 300
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GEMINI_URL, 
                json=payload, 
                headers=headers, 
                timeout=aiohttp.ClientTimeout(total=7)  # مهلة أقصاها 7 ثوانٍ
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                
                # في حال رجع السيرفر كود آخر غير 200
                return random.choice(FALLBACK_MESSAGES)

    except asyncio.TimeoutError:
        return "النت عند السيرفر شوية نام، عيده بالله؟"
    except Exception as e:
        print(f"Gemini Error: {e}")
        return random.choice(FALLBACK_MESSAGES)
