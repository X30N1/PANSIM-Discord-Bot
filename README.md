# Pansim-BOT

bot do powiadomień o spotkaniach koła naukowego informatyki stosowanej

**Funkcjonalność:**
- Samodzielnie zbiera informacje o nadchodzących wydarzeniach
- Wysyła notifikacje w określonym kanale
- Pozwala administratorowi dynamicznie zmieniać dzień i godznę powiadomienia
- Pozwala użytkownikom sprawdzać nadchodzące wydarzenia wraz z miejscem oraz czas nadchodzących powiadomień
- Oferuje kilka komend do podania informacji systemowych oraz operacyjnych
- Pozwala na ustawienie dowolnego statusu (w limicie API Discorda)

## 1. Instalacja

> [!TIP]
> Do poprawnego działania zalecane jest użycie środowiska wirtualnego (venv)!

Do uruchomienia potrzebujesz następujących zależności:

- py-cord
- dotenv
- pytz

> [!CAUTION]
> Pakiet pytz jest przestarzały (deprecated), skrypt dalej działa, ale miej na to uwagę.

> [!NOTE]
> W ramach problemów bądź do szybkiej instalacji  ostatnia dobra wersja zależności została wstawiona do dependencies.txt

Po konfiguracji (**wymagane**) można łatwo uruchomić bota za pomocą komendy:

```python
python bot.py
```

## 2. Konfiguracja

### 2.1 Dodanie bota do serwera
> [!CAUTION]  
> Bot oryginalnie operuje na uprawnieniach administratora, oraz ma dostęp do wszystkich intencji API (presence, server members oraz message content), redukcja uprawnień jest możliwa ale może zepsuć część bądź całą funkcjonalność bota

> [!WARNING]  
> Z powodu korzystania z intencji bot może tylko działać w maks. 100 serwerach bez przechodzenia przez proces weryfikacji

Na samym początku należy stworzyć aplikację oraz bota na [portalu deweloperskim discorda](https://discord.com/developers/applications), po czym ustawiamy intencje "PRESENCE INTENT", "SERVER MEMBERS INTENT" i "MESSAGE CONTENT INTENT" w sekcji "Privileged Gateway Intents".
Można na tym etapie także ustawić nazwę oraz ikonę bota.

Następnie należy wygenerować link zaproszenia, aby dodać bota do serwera (gildi), można to zrobić poprzez wejście na tab OAuth2 -> OAuth2 URL Generator. Następnie należy zaznaczyć bot -> Administrator.\
Po tym powinien wyświetlić się link w polu "GENERATED URL", który można następnie użyć na dowolnej przeglądarce z zalogowanym kontem który ma rolę owner, administrator bądź manage server, aby dodać bota do wszystkich serwerów gdzie mamy co najmniej jedno z tych uprawnień.

Po dodaniu bota powinien on się wyświetlić na liście użytkowników wraz z powiadomieniem o dołączeniu (jeżeli są one włączone na danym serwerze) oraz nową rolą w liście ról która ma uprawnienia które zostały nadane. 

> [!NOTE]
> Rola nadana przez serwer przy dodaniu bota nie może być odebrana w inny sposób niż usunięcie samego bota.

### 2.2 Konfiguracja skryptu bota

Aby bot mógł poprawnie działać należy podać mu wymagane zmienne:
- Wstępny czas powiadomień w formacie odstępu czasowego od wydarzenia (timedelta)
- ID serwera, na którym ma działać
- ID kanału, na którym ma wysyłać ogłoszenia
- ID roli administratora, który może zmieniać odstęp czasowy
- Status bota

Bot do sprawdzania czasu powiadomień iteruje przez zmienną REMINDER_TIME.\
Zmienną tą można zostawić tak jak jest (wtedy powiadomienie przyjdzie 1 dzień i 2 godziny przed każdym wydarzeniem), bądź zmienić w następujący sposób:

```python
REMINDER_TIME = [timedelta(days=[ILOŚĆ_DNI]), timedelta(hours=[ILOŚĆ_GODZIN])]
```

Aby uzyskać klucz API, należy wrócić się na [portal deweloperski discorda](https://discord.com/developers/applications), i w sekcji bot aplikacji skopiować string w sekcji "TOKEN". Jeżeli klucz ten jest ukryty (np. po zmianie zakładek bądź zamknięciu przeglądarki), można wygenerować nowy za pomocą przycisku "Reset Token". Token ten należy umieścić w .env w następujący sposób:

> [!CAUTION]  
> **NIGDY** nie podawaj klucza bota w widocznym publicznie miejscu bądź osobom nieznanym. Zaniechanie tego ostrzeżenia może zakończyć się zablokowaniem aplikacji oraz twojego konta

```env
TOKEN = [TOKEN]
```

Następnie należy ustawić zmienne specyficzne dla każdego serwera. Aby to zrobić, w ustawieniach discorda włączyć tryb deweloperski. Można to zrobić w zakładce Advanced -> Developer mode. Po zrobieniu tego ID obiektów (takich jak użytkownicy, kanały i serwery) można skopiować wciskając prawy przycisk myszy i wybierając "Copy [OBIEKT] ID".

Zmienne te **trzeba** wstawić do skryptu w następujący sposób (można tu też ustawić status bota w polu name):

> [!NOTE]
> Wszystkie zmienne oprócz dni i godziny powiadomień można tylko zmienić poprzez wstawienie nowych zmiennych do skryptu i restart bota

```python
@bot.event
async def on_ready():
    global guild, botchannel, admin
    await bot.change_presence(activity=discord.Game(name="[STATUS]")) # Status
    guild = bot.get_guild([ID SERWERA]) # Numer ID serwera
    botchannel = bot.get_channel([ID KANAŁU OGŁOSZENIOWEGO]) # Numer ID kanału ogłoszeniowego
    admin = guild.get_role([ID ROLI ADMINISTRATORA]) # Numer ID roli administratora

    await botchannel.send("Uruchomiono bota!")
    print("Uruchomiono bota")
```

Po wstawieniu tych zmiennych bot jest gotowy do uruchomienia.