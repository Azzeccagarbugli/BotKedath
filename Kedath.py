import cassiopeia as cass
import random

from settings import API

cass.set_riot_api_key(API)
cass.set_default_region("EUW")

summoner = cass.get_summoner(name="Azzeccagarbugli")
#print("{name} è al livello {level}, evocatore nella regione {region}. ID = {id}.".format(name=summoner.name,
#                                                                                     level=summoner.level,
#                                                                                     region=summoner.region,
#                                                                                     id=summoner.id))

last_match = summoner.match_history()[0]

for player in last_match.participants:
    if player.summoner.name == "Azzeccagarbugli":
        try: 
            kills = player.stats.kills
            deaths = player.stats.deaths
            assists = player.stats.assists

            print("K:{0}\nD:{1}\nA:{2}".format(kills, deaths, assists))
            print("KDA: {0}\n".format((kills + assists) / deaths))
            break
        except ZeroDivisionError:
            print("Perfect KDA")
            break


#   champions = cass.get_champions()
#   random_champion = random.choice(champions)
#   print("Campione casuale giocato nell'ultimo periodo: {name}.".format(name=random_champion.name))