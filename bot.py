import discord
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Importujemy prywatny token, ukryty w .env z oczywistych powodów
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

# Deklarujemy zmienne
guild = 1181311403164958742 # Numer ID serwera
botchannel = bot.get_channel(1353825094211735633)
admin = 1181311635449720832
REMINDER_TIME = [timedelta(days=1), timedelta(hours=2)]

# Zmienna do śledzenia czy powiadomienia były wysyłane
sent_reminders = {}

@bot.event
async def on_ready():
    await bot.sync_commands()
    print("Uruchomiono bota")

@bot.loop(minutes=5)
async def check_reminders():
    now = datetime.now(timezone.utc)
    events = await bot.get_guild(guild).fetch_scheduled_events()
    for event in events:
        if event.status == discord.ScheduledEventStatus.scheduled:
            time_until_start = event.start_time - now
        for reminder in REMINDER_TIME:
            time_diff = abs(time_until_start - reminder)

            if time_diff < timedelta(minutes=5) and (event.id, reminder) not in sent_reminders:
                await send_reminder(event, reminder)
                sent_reminders[(event.id, reminder)] = True

async def send_reminder(event, reminder):
    timestr = format_timedelta(reminder)
    await botchannel.send(f"Uwaga: Wydarzenie '{event.name}' rozpoczyna się za {timestr}!")

async def format_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days} {'dzień' if days == 1 else 'dni'}")
    if hours > 0:
        parts.append(f"{hours} godzin{'ę' if hours == 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minut{'ę' if minutes == 1 else ''}")
    return ', '.join(parts)

@bot.slash_command(name="test-czasu", description="Podaj obecny czas wg. skryptu (DEBUG)")
async def print_time(ctx: discord.ApplicationContext):
    await ctx.respond(datetime.now(timezone.utc))

bot.run(os.getenv("TOKEN"))