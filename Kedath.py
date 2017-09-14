import os
import telepot
import cassiopeia as cass

from time import sleep
from settings import API, TOKEN, start_msg, help_msg

# Machine state variable
machine_state = 0

# Summoner Name
summoner = ""

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    global machine_state
    global summoner

    chat_id = msg['chat']['id']
    command_input = msg['text']

    cass.set_riot_api_key(API)
    cass.set_default_region("EUW")

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
        summoner_name = command_input
        summoner = cass.get_summoner(name=summoner_name)
        # masteries_champion = summoner.champion_masteries.filter(lambda cm: cm.level = 7)
        # list_champion_masteries = 
        if summoner.exists == True:
            check_msg = "Il tuo nome evocatore è stato riconosciuto. \nBenvenuto *{0}*! Il tuo livello attuale è: *{1}*"\
                        "\n\nI tuoi main champion sono attualmente: {3}".format(summoner.name, summoner.level)
            bot.sendMessage(chat_id, check_msg, parse_mode = "Markdown")
            machine_state = 2
        else:
            check_msg = "Il tuo nome evocatore non esiste, prova nuovamente usando il comando /set_username"
            bot.sendMessage(chat_id, check_msg)
            machine_state = 0
    
    # elif machine_state = 2 and content_type == "text":
        
       
    # summoner = cass.get_summoner(name="Azzeccagarbugli")

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

def get_champion_masteries(name)
    masteries_champion = summoner.champion_masteries.filter(lambda cm: cm.level == 7)
    listcm.champion.name for cm in masteries_champion 

# PID file
pid = str(os.getpid())
pidfile = "/tmp/unimensabot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)
f.close()


try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    print('Vediamo quello che succede...')

    while 1:
        sleep(10)

finally:
    # Remove PID file on exit
    os.unlink(pidfile)