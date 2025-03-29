import discord
import os
import pytz
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Importujemy prywatny token, ukryty w .env z oczywistych powodów
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

# Deklarujemy zmienne
guild = bot.get_guild(1181311403164958742) # Numer ID serwera
botchannel = bot.get_channel(1353825094211735633)
admin = guild.get_role(1181311635449720832)
REMINDER_TIME = [timedelta(days=1), timedelta(hours=2)]

# Zmienna do śledzenia czy powiadomienia były wysyłane
sent_reminders = {}

@bot.event
async def on_ready():
    await bot.change_presence(activity="Patrzy jak farba schnie")
    await botchannel.send("Uruchomiono bota!")
    print("Uruchomiono bota")

@bot.loop(minutes=30)
async def check_reminders():
    now = datetime.now(timezone.utc)
    events = guild.fetch_scheduled_events()
    clear_old_reminders(events)
    for event in events:
        if event.status == discord.ScheduledEventStatus.scheduled:
            time_until_start = event.start_time - now
        for reminder in REMINDER_TIME:
            time_diff = abs(time_until_start - reminder)
        
            if time_diff < timedelta(minutes=5) and (event.id, reminder) not in sent_reminders:
                await send_reminder(event, reminder)
                sent_reminders[(event.id, reminder)] = True

async def clear_old_reminders(passed_events):
    events = passed_events
    for event in sent_reminders:
        if event.id not in events:
            for time in REMINDER_TIME:
                sent_reminders.pop((event.id, time))

async def send_reminder(passed_event, reminder):
    event = passed_event
    days = reminder.days
    hours, remainder = divmod(reminder.seconds, 3600)
    minutes = divmod(remainder, 60)
    await botchannel.send(f"@everyone \nUwaga! Wydarzenie {event.name} rozpoczyna się za {days} dni, {hours} godzin i {minutes} minut!")

@bot.slash_command(name="test-czasu", description="Podaj obecny czas wg. skryptu (DEBUG)")
async def print_time(ctx: discord.ApplicationContext):
    await ctx.respond(datetime.now(timezone.utc))

@bot.slash_command(name="info-dump", description="Zwraca czas odpowiedzi i jaki czas widzi (w CET/CEST)")
async def print_time(ctx: discord.ApplicationContext):
    await ctx.respond(f" Czas odpowiedzi: {round(bot.latency())} \n Czas rejestrowany przez bota: {datetime.now(pytz.timezone("Europe/Warsaw"))}")

@bot.slash_command(name="check-time", description="Sprawdź, kiedy dostaniesz powiadomienie o wydarzeniach")
async def print_time(ctx: discord.ApplicationContext):
    await ctx.respond(f"{REMINDER_TIME}")

bot.run(os.getenv("TOKEN"))