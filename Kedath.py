import os
import sys
import math
import telepot
import cassiopeia
from time import sleep
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
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    if command_input == "/start" or command_input == "/start@KedathBot":
        bot.sendMessage(chat_id, start_msg)

    elif command_input == "/help" or command_input == "/help@KedathBot":
        bot.sendMessage(chat_id, help_msg)

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

    elif user_state[chat_id] == 1:
        # Set user server
        user_server[chat_id] = server_dict[command_input]

        msg = "Inserisci il tuo nome evocatore"
        # Remove markup keyboard
        bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        # Set user state
        user_state[chat_id] = 2

    elif user_state[chat_id] == 2:
        try: 
            summoner = get_summoner(command_input, user_server[chat_id])

            # Take some time to get all the info from RIOT
            bot.sendMessage(chat_id, "Stiamo elaborando i tuoi dati...", parse_mode="Markdown")

            # Get masteries
            masteries = get_champion_masteries(summoner)

            # TODO
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

        except Exception as e: 
            msg = "Evocatore non trovato."
            keyboard = ''
            print(e)

        finally:
            bot.sendMessage(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

            # Return to 0 state
            user_state[chat_id] = 0

    
def get_summoner(summoner_name, server):
    """
    Check if a summoner exists and if exists return a 'summoner' instance
    """
    # Set user server
    cassiopeia.set_default_region(server)

    # Get summoner
    summoner = cassiopeia.get_summoner(name = summoner_name)

    if summoner.exists == True:
        return summoner
    else:
        raise Exception('SummonerNotFound')
        
        
# TODO
def get_last_kda(summoner):
    """
    Get given summoner last KDA 
    """
    rv = ''

    # Get last match
    last_match = summoner.match_history()[0]

    for player in last_match.participants:
        if player.summoner.name == summoner.name:
            kills = player.stats.kills
            deaths = player.stats.deaths
            assists = player.stats.assists
            rv += "*{0}* last match score:\n*K*: {1}\n*D*: {2}\n*A*: {3}\n".format(summoner.name, kills, deaths, assists)

            try: 
                rv += "*KDA*: {0}\n".format((kills + assists) / deaths)
                break
            except ZeroDivisionError:
                rv += "*KDA: Perfect*"
                break
    
    return rv

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

    if not os.path.exists("users"):
        os.makedirs("users")

    f = open("users/" + data, "w")
    f.close()

    bot.sendMessage(from_id, add_msg)


def update():
    """
    This function will check every X minutes for new matches
    """

    for notifcation_request in os.listdir("users"):
        chat_id, summoner_name, server = notifcation_request.split('-')

        # Get summoner on 'server'
        summoner = get_summoner(summoner_name, server)

        # Get last match id
        match_id = summoner.match_history[0].id

        with open("users/" + notifcation_request, "r") as f:
            last_match_id = f.readline()

            if str(match_id) != last_match_id:
                # Send last statistics
                msg = get_last_kda(summoner)
                bot.sendMessage(chat_id, msg, parse_mode="Markdown")

                # Overwrite last match ID
                f = open("users/" + notifcation_request, "w")
                f.write(str(match_id))
                f.close()

    sleep(update_time)


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
    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})

    # Set Riot API
    cassiopeia.set_riot_api_key(API)

    while 1:
        update()

finally:
    # Remove PID file on exit
    os.unlink(pidfile)