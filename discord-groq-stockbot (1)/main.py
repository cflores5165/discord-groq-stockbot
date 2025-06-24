import os
import discord
import yfinance as yf
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command(name="analyze")
async def analyze_stock(ctx, symbol: str):
    await ctx.send(f"📊 Analyzing `{symbol}`...")

    try:
        data = yf.download(symbol, period="1mo", interval="1d")
        if data.empty:
            await ctx.send("⚠️ Couldn't fetch data.")
            return

        latest_price = float(data["Close"].iloc[-1])
        prompt = (
    f"""You're a financial analyst. The stock symbol is {symbol}.
The current price is ${latest_price:.2f}.
Should I BUY, SELL, or HOLD? Respond in 1–2 sentences."""
)



        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        await ctx.send(f"🧠 {answer}")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print("Groq API Error:", e)

bot.run(DISCORD_TOKEN)
