import os
import sys
import math
import telepot
import cassiopeia
from time import sleep
from datetime import datetime
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from settings import API, TOKEN, start_msg, help_msg, add_msg, update_time

# Server list
server_dict = {
    "Brazil" : "BR",
    "Europe North Est" : "EUNE",
    "Europe West" : "EUW",
    "Japan" : "JP",
    "Korea" : "KR",
    "Latin North America" : "LAN",
    "Latin South America" : "LAS",
    "North America" : "NA",
    "Oceania" : "OCE",
    "Trukey" : "TR",
    "Russia" : "RU",
    "PBE" : "PBE"
}

# State for user
user_state = {}

# User server state
user_server = {}


def handle(msg):
    """
    Handle messages recevied from users
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    command_input = msg['text']

    # Check user state
    try:
        user_state[chat_id] = user_state[chat_id]
    except:
        user_state[chat_id] = 0

    if command_input == "/start" or command_input == "/start@KedathBot":
        log_print("{0} /start".format(chat_id))
        bot.sendMessage(chat_id, start_msg)

    elif command_input == "/help" or command_input == "/help@KedathBot":
        log_print("{0} /help".format(chat_id))
        bot.sendMessage(chat_id, help_msg)

    # Search summoner - 1
    elif command_input == "/search_summoner" or command_input == "/search_summoner@KedathBot":
        markup = ReplyKeyboardMarkup(keyboard=[
            ["Brazil"],
            ["Europe North Est"],
            ["Europe West"],
            ["Japan"],
            ["Korea"],
            ["Latin North America"],
            ["Latin South America"],
            ["North America"],
            ["Oceania"],
            ["Turkey"],
            ["Russia"],
            ["PBE"]
        ])

        msg = "Seleziona la tua regione"
        bot.sendMessage(chat_id, msg, reply_markup=markup)

        # Set user state
        user_state[chat_id] = 1

        log_print("{0} /search_summoner".format(chat_id))

    # Search summoner - 2
    elif user_state[chat_id] == 1:
        # Set user server
        user_server[chat_id] = server_dict[command_input]

        # Set user state
        user_state[chat_id] = 2

        # Remove markup keyboard
        bot.sendMessage(chat_id,
                        "Inserisci il tuo nome evocatore",
                        parse_mode="Markdown",
                        reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

    # Search summoner - 3
    elif user_state[chat_id] == 2:
        # Return to 0 state
        user_state[chat_id] = 0

        summoner = get_summoner(command_input, user_server[chat_id])

        if not summoner:
            msg = "Evocatore non trovato."
            keyboard = ''
        else:
            # Take some time to get all the info from RIOT
            bot.sendMessage(chat_id, "Stiamo elaborando i tuoi dati...", parse_mode="Markdown")

            # Get masteries
            masteries = get_champion_masteries(summoner)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Attiva notifiche',
                                    callback_data="{0}-{1}-{2}".format(chat_id, summoner.name, user_server[chat_id]))],
            ])

            try:
                msg = "Benvenuto *{0}*!\nIl tuo livello attuale è: *{1}*".format(summoner.name, summoner.level)
                msg += "\n\nI tuoi main champion sono attualmente:\n_• {0}_".format(masteries[0])
                msg += "\n_• {0}_".format(masteries[1])
                msg += "\n_• {0}_".format(masteries[2])

            except IndexError:
                pass

        bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    # Stop notifications - 1
    elif command_input == "/stop_notification" or command_input == "/stop_notification@KedathBot":
        # Set user state
        user_state[chat_id] = 3

        entries = []

        for notification_request in os.listdir("users"):
            user, summoner_name, server = notification_request.split('-')

            if user == str(chat_id):
                entries.append(["{0}-{1}".format(summoner_name, server)])

        markup = ReplyKeyboardMarkup(keyboard=entries)

        if entries == []:
            msg = "Nessuna notifica abilitata!"
        else:
            msg = "Seleziona le notifiche da disabilitare"

        bot.sendMessage(chat_id, msg, reply_markup=markup)

        log_print("{0} /stop_notification".format(chat_id))

    # Stop notifications - 2
    elif user_state[chat_id] == 3:
        # Return to 0 state
        user_state[chat_id] = 0

        try:
            os.unlink("users/" + str(chat_id) + "-" + command_input)

            # Remove markup keyboard
            msg = "*Le notifiche per {0} sono state disabilitate*".format(command_input)
        except:
            msg = "*Errore nella rimozione*"

        bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    
    # Get last KDA 
    elif command_input == "/get_last_kda" or command_input == "/get_last_kda@KedathBot":
        # TODO
        bot.sendMessage(chat_id, "Funzione ancora non disponibile!")

def get_summoner(summoner_name, server):
    """
    Check if a summoner exists and if exists return a 'summoner' instance
    """
    # Set user server
    cassiopeia.set_default_region(server)

    # Get summoner
    summoner = cassiopeia.get_summoner(name=summoner_name)

    if summoner.exists is True:
        return summoner
    else:
        return 0

def get_last_kda(summoner):
    """
    Get given summoner last KDA
    """
    # Get last match
    last_match = summoner.match_history()[0]

    for player in last_match.participants:
        if player.summoner.name == summoner.name:
            kills = player.stats.kills
            deaths = player.stats.deaths
            assists = player.stats.assists

            msg = ("Nell'ultimo game *{0}* ha registrato uno score pari a:\n"
                   "*K*: {1}\n*D*: {2}\n*A*: {3}\n".format(summoner.name,
                                                           kills,
                                                           deaths,
                                                           assists))

            if deaths == 0:
                msg += "\n*PERFECT: * In questo game hai ottenuto un *KDA* perfetto, ottima prestazione complimenti!"
            else:
                kda = ((kills + assists) / deaths)
                msg += "Con un *KDA* effettivo uguale a {0}\n\n".format(kda)

                if kda < 2:
                    msg += "*NOT GOOD*: In questo game, secondo il tuo KDA, non hai contribuito in maniera evidente. Prova "\
                            "a migliorati nel prossimo game, la landa ti aspetta!"
                elif kda >= 2 and kda < 5:
                    msg += "*GOOD*: In questo game, secondo il tuo KDA, hai contribuito in maniera sostanziosa allo sviluppo del game "\
                            "mostrando a tutti i tuoi avversari di che pasta sei fatto!"
                elif kda >= 5 and kda < 8:
                    msg += "*VERY GOOD*: In questo game, secondo il tuo KDA, hai sviluppato delle ottime meccaniche di gioco. Continua in "\
                            "questo modo e la conquista delle divisioni più prestigiose della landa sarà tua!"
                elif kda >= 8:
                    msg += "*JUST A GOD*: In questo game, secondo il tuo KDA, hai semplicemente dimostrato che Faker in realtà è una femminuccia!"
            break

    return msg

def get_champion_masteries(summoner):
    """
    Return given summoner champions with mastery = 7
    """
    rv = []

    # Get masteries = 7
    masteries_champion = summoner.champion_masteries.filter(lambda cm: cm.level == 7)

    for champion in masteries_champion:
        rv.append("{0} ({1})".format(champion.champion.name, millify(champion.points)))

    return rv


def millify(num):
    """
    Convert long numbers to human readable
    https://stackoverflow.com/questions/3154460/python-human-readable-large-numbers#3155023
    """
    millnames = ['', 'k', 'm']

    num = float(num)
    millidx = max(0,min(len(millnames)-1, int(math.floor(0 if num == 0 else math.log10(abs(num))/3))))

    return '{:.0f}{}'.format(num / 10**(3 * millidx), millnames[millidx])


def on_callback_query(msg):
    """
    Register notification for a specif summoner to user
    """
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')

    f = open("users/" + data, "w")
    user, summoner_name, server = data.split('-')

    # Get summoner on 'server'
    summoner = get_summoner(summoner_name, server)

    if not summoner:
        bot.sendMessage(from_id, "Evocatore non trovato!")
        bot.answerCallbackQuery(query_id)
    else:
        # Get last match id
        match_id = summoner.match_history[0].id

    # Get last match id
    match_id = summoner.match_history[0].id

    f.write(str(match_id))
    f.close()

    bot.sendMessage(from_id, add_msg)
    bot.answerCallbackQuery(query_id)

    log_print("{0} enabled notifications".format(from_id))


def update():
    """
    This function will check every X minutes for new matches
    """
    for notification_request in os.listdir("users"):
        user, summoner_name, server = notification_request.split('-')

        # Get summoner on 'server'
        summoner = get_summoner(summoner_name, server)

        # Summoner not found
        if not summoner:
            os.unlink("users/" + notification_request)
        else:
            # Get last match id
            match_id = summoner.match_history[0].id

            with open("users/" + notification_request, "r") as f:
                last_match_id = f.readline()

                if str(match_id) != last_match_id:
                    # Overwrite last match ID
                    f = open("users/" + notification_request, "w")
                    f.write(str(match_id))
                    f.close()

                    # Send last statistics
                    msg = get_last_kda(summoner)

                    try:
                        bot.sendMessage(user, msg, parse_mode="Markdown")
                    except telepot.exception.BotWasBlockedError:
                        os.unlink("users/" + notification_request)

    # Return to sleep
    sleep(update_time)

# Log function
def log_print(txt):
    """
    Write to 'log.txt' adding current date
    Debug purpose
    """
    try:
        log = open("log.txt", "a")
    except IOError:
        log = open("log.txt", "w")

    log.write("[{0}] {1}\n".format(datetime.now().strftime("%m-%d-%Y %H:%M"), txt))

    log.close()


# PID file
pid = str(os.getpid())
pidfile = "/tmp/kedathbot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)
f.close()

print('Vediamo quello che succede...')

try:
    bot = telepot.Bot(TOKEN)

    # Ensure storage dir exists
    if not os.path.exists("users"):
        os.makedirs("users")

    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    # Set Riot API
    cassiopeia.set_riot_api_key(API)

    while 1:
        update()

finally:
    # Remove PID file on exit
    os.unlink(pidfile)
