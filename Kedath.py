import cassiopeia as cass
import random

from settings import API

cass.set_riot_api_key(API)
cass.set_default_region("EUW")

summoner = cass.get_summoner(name="Azzeccagarbugli")
print("{name} è al livello {level}, evocatore nella regione {region}. ID = {id}.".format(name=summoner.name,
                                                                                      level=summoner.level,
                                                                                      region=summoner.region,
                                                                                      id=summoner.id))

champions = cass.get_champions()
random_champion = random.choice(champions)
print("Campione casuale giocato nell'ultimo periodo: {name}.".format(name=random_champion.name))
