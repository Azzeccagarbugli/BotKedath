import os
import sys
import telepot
import cassiopeia
from time import sleep
from telepot.namedtuple import ReplyKeyboardMarkup
from settings import API, TOKEN, start_msg, help_msg

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

    elif command_input == "/set_summoner" or command_input == "/set_summoner@KedathBot":
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
                    ], one_time_keyboard=True)

        msg = "Seleziona la tua regione"
        bot.sendMessage(chat_id, msg, reply_markup=markup)

        # Set user state
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        # Set user server
        user_server[chat_id] = server_dict[command_input]

        msg = "Inserisci il tuo nome evocatore"
        bot.sendMessage(chat_id, msg, parse_mode="Markdown")

        # Set user state
        user_state[chat_id] = 2

    elif user_state[chat_id] == 2:
        try: 
            summoner = get_summoner(command_input, user_server[chat_id])

            # Take some time to get all the info from RIOT
            bot.sendMessage(chat_id, "Stiamo elaborando i tuoi dati...", parse_mode="Markdown")

            # Get masteries
            masteries = get_champion_masteries(summoner)

            try:
                msg = "Il tuo nome evocatore è stato riconosciuto.\n"\
                      "Benvenuto *{0}*!\nIl tuo livello attuale è: *{1}*\n\n"\
                      "I tuoi main champion sono attualmente:\n_{2}_\n_{3}_\n_{4}_\n".format(summoner.name,
                                                                                             summoner.level,
                                                                                             masteries[0],
                                                                                             masteries[1],
                                                                                             masteries[2])
            except IndexError:
                msg = "Il tuo nome evocatore è stato riconosciuto.\n"\
                      "Benvenuto *{0}*!\nIl tuo livello attuale è: *{1}*".format(summoner.name,
                                                                                 summoner.level)

        except Exception as e: 
            msg = "Evocatore non trovato."
            print(e)

        finally:
            bot.sendMessage(chat_id, msg, parse_mode="Markdown")

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
    Get given user last KDA 
    """
    rv = []

    # Get last match
    last_match = summoner.match_history()[0]

    for player in last_match.participants:
        if player.summoner.name == summoner.name:
            kills = player.stats.kills
            deaths = player.stats.deaths
            assists = player.stats.assists
            rv.append("K: {0}\nD: {1}\nA: {2}".format(kills, deaths, assists))

            try: 
                rv.append("KDA: {0}\n".format((kills + assists) / deaths))
                break
            except ZeroDivisionError:
                rv.append("KDA: Perfect")
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
        rv.append("{0} ({1})".format(champion.champion.name, champion.points))
        # TODO: inserire il puinteggio in fomratto ridotto, convertire il numero in stringa e vedere la 
        # sua lunghezza e a quel punto basarsi su quella per inserire la 'k' o la 'm'
        # ES: 231k oppure 3m
        
        # a = str(champion.points)
        # print(len(a))

    return rv


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
    bot.message_loop(handle)

    # Set Riot API
    cassiopeia.set_riot_api_key(API)

    while 1:
        sleep(10)
finally:
    # Remove PID file on exit
    os.unlink(pidfile)