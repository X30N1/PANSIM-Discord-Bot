import discord
import os
import pytz
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import tasks

# Importujemy prywatny token, ukryty w .env z oczywistych powodów
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

# Deklarujemy zmienne
REMINDER_TIME = [timedelta(days=1), timedelta(hours=2)]

# Zmienna do śledzenia czy powiadomienia były wysyłane
guild = None
botchannel = None
admin = None
sent_reminders = {}

@bot.event
async def on_ready():
    global guild, botchannel, admin
    await bot.change_presence(activity=discord.Game(name="Patrzy jak farba schnie")) # Status
    guild = bot.get_guild(1181311403164958742) # Numer ID serwera
    botchannel = bot.get_channel(1353825094211735633) # Numer ID kanału ogłoszeniowego
    admin = guild.get_role(1181311635449720832) # Numer ID roli administratora

    await botchannel.send("Uruchomiono bota!")
    print("Uruchomiono bota")

@tasks.loop(minutes=10)
async def check_reminders():
    now = datetime.now(timezone.utc)
    events = await guild.fetch_scheduled_events()
    await clear_old_reminders(events)
    
    for event in events:
        if event.status == discord.ScheduledEventStatus.scheduled:
            time_until_start = event.start_time - now
            for reminder in REMINDER_TIME:
                time_diff = abs(time_until_start - reminder)
                if time_diff <= timedelta(minutes=5) and (event.id, reminder) not in sent_reminders:
                    event_channel = guild.get_channel(event.location.value.id)
                    await send_reminder(event, reminder, event_channel)
                    sent_reminders[(event.id, reminder)] = True

async def clear_old_reminders(current_events):
    current_event_ids = {event.id for event in current_events}
    to_remove = []
    
    for (event_id, reminder_time) in sent_reminders.keys():
        if event_id not in current_event_ids:
            to_remove.append((event_id, reminder_time))
    
    for key in to_remove:
        sent_reminders.pop(key, None)

async def send_reminder(passed_event, reminder, event_channel):
    days = reminder.days
    hours, remainder = divmod(reminder.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    await botchannel.send(f"@everyone \nUwaga! Wydarzenie **{passed_event.name}** rozpoczyna się za **{days} dni, {hours} godziny i {minutes} minuty!** na kanale **{event_channel}**")

@check_reminders.before_loop
async def before_check_reminders():
    await bot.wait_until_ready()

@bot.slash_command(name="info-dump", description="Zwraca czas odpowiedzi i jaki czas widzi (w CET/CEST)")
async def print_time(ctx: discord.ApplicationContext):
    await ctx.respond(f" Czas odpowiedzi: **{str(round(bot.latency * 1000))}**ms\nCzas rejestrowany przez bota: **{datetime.now(pytz.timezone('Europe/Warsaw'))}**")

@bot.slash_command(name="get-users", description="Wypisz listę osób obecnych na kanale (tylko podczas spotkania)")
async def get_users(ctx: discord.ApplicationContext):
    events = await guild.fetch_scheduled_events()
    if not events:
        await ctx.respond("**Brak nadchodzących wydarzeń.**")

    active_event = False
    for event in events:
        if event.status != discord.ScheduledEventStatus.active:
            continue
        else:
            active_event = True
            event_channel = guild.get_channel(event.location.value.id)
            user_list = event_channel.members

    if not active_event:
        await ctx.respond("Nie ma obecnie aktywnego wydarzenia!")
    else:
        await ctx.respond(user_list)

@bot.slash_command(name="change-time", description="Komenda do zmiany czasu [TYLKO DLA ADMINISTRATORÓW]")
async def change_time(ctx: discord.ApplicationContext, dni: discord.Option(int), godziny: discord.Option(int)): # type: ignore
    if admin in ctx.author.roles:
        try:
            global REMINDER_TIME 
            REMINDER_TIME[0] = timedelta(days=dni)
            REMINDER_TIME[1] = timedelta(hours=godziny)
            await ctx.respond(f"Ustawiono powiadomienia na **{dni}** dni oraz **{godziny}** godziny!")
        except Exception:
            await ctx.respond(f"Wystąpił błąd: {Exception}")
    else:
        await ctx.respond("Tylko administratorzy mogą wykonać tą komendę!")

@bot.slash_command(name="events", description="Pokaż wszystkie nadchodzące wydarzenia")
async def list_events(ctx: discord.ApplicationContext):
    events = await guild.fetch_scheduled_events()
    if not events:
        await ctx.respond("**Brak nadchodzących wydarzeń.**")
        return
        
    response = "**Nadchodzące wydarzenia:**\n\n"
    now = datetime.now(timezone.utc)
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    
    for event in events:
        if event.status == discord.ScheduledEventStatus.scheduled:
            start_time = event.start_time.astimezone(warsaw_tz)
            event_channel = guild.get_channel(event.location.value.id) # Nie można event.value bo zwraca generyczny obiekt
            response += f"**{event.name}**\n"
            response += f"Na kanale: **{event_channel}**\n"
            response += "Powiadomienia:\n"
            for reminder in REMINDER_TIME:
                reminder_time = start_time - reminder
                if reminder_time > datetime.now(warsaw_tz):
                    response += f"- {reminder_time.strftime('%d.%m.%Y %H:%M')}"
                    if (event.id, reminder) in sent_reminders:
                        response += " (wysłano)\n"
                    else:
                        response += " (oczekuje)\n"
            response += "\n"
    
    await ctx.respond(response)

check_reminders.start()

bot.run(os.getenv("TOKEN"))