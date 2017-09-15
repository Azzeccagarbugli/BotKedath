import os
import sys
import telepot
import cassiopeia
from time import sleep
from settings_dist import API, TOKEN, start_msg, help_msg

# Cassiopeia settings
cassiopeia.set_riot_api_key(API)
cassiopeia.set_default_region("EUW")

# Machine state variable
machine_state = 0

# Summoner Name
summoner = ""

def handle(msg):
    global machine_state
    global summoner

    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    if machine_state == 0 and content_type == "text":
        if command_input == "/start" or command_input == "/start@KedathBot":
            bot.sendMessage(chat_id, start_msg)

        elif command_input == "/help" or command_input == "/help@KedathBot":
            bot.sendMessage(chat_id, help_msg)

        elif command_input == "/set_username" or command_input == "/set_username@KedathBot":
            set_username_msg = "Inserisci il tuo nome evocatore"
            bot.sendMessage(chat_id, set_username_msg)
            machine_state = 1
    
    elif machine_state == 1 and content_type == "text":
        # Take some time to get all the info from RIOT
        bot.sendMessage(chat_id, "Stiamo elaborando i tuoi dati...", parse_mode = "Markdown")

        summoner_name = command_input
        summoner = cassiopeia.get_summoner(name = summoner_name)

        if summoner.exists == True:
            try:
                masteries = get_champion_masteries(summoner_name)
            except IndexError:
                check_msg = "Il tuo nome evocatore è stato riconosciuto.\n"\
                            "Benvenuto *{0}*!\nIl tuo livello attuale è il: *{1}*".format(summoner.name,
                                                                                                summoner.level)
                bot.sendMessage(chat_id, check_msg, parse_mode = "Markdown")

            check_msg = "Il tuo nome evocatore è stato riconosciuto.\n"\
                        "Benvenuto *{0}*!\nIl tuo livello attuale è il: *{1}*\n\n"\
                        "I tuoi main champion sono attualmente:\n_{2}_\n_{3}_\n_{4}_\n".format(summoner.name,
                                                                                               summoner.level,
                                                                                               masteries[0],
                                                                                               masteries[1],
                                                                                               masteries[2])
            bot.sendMessage(chat_id, check_msg, parse_mode = "Markdown")
            machine_state = 2
        else:
            check_msg = "Il tuo nome evocatore non esiste, prova nuovamente usando il comando /set_username"
            bot.sendMessage(chat_id, check_msg)
            machine_state = 0
    
    # elif machine_state = 2 and content_type == "text":
        
       
    # summoner = cassiopeia.get_summoner(name="Azzeccagarbugli")

    # last_match = summoner.match_history()[0]

    # for player in last_match.participants:
    #     if player.summoner.name == "Azzeccagarbugli":
    #         try: 
    #             kills = player.stats.kills
    #             deaths = player.stats.deaths
    #             assists = player.stats.assists
    #             print("K:{0}\nD:{1}\nA:{2}".format(kills, deaths, assists))
    #             print("KDA: {0}\n".format((kills + assists) / deaths))
    #             break
    #         except ZeroDivisionError:
    #             print("Perfect KDA")
    #             break


def get_champion_masteries(summoner_name):
    """
    Return given summoner champions with mastery = 7
    """
    rv = []

    summoner = cassiopeia.get_summoner(name = summoner_name)
    masteries_champion = summoner.champion_masteries.filter(lambda cm: cm.level == 7)

    for champion in masteries_champion:
        rv.append(champion.champion.name)

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

    while 1:
        sleep(10)

finally:
    # Remove PID file on exit
    os.unlink(pidfile)