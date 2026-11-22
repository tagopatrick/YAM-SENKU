import random, datetime
pubs=[
"On ne vise pas la lune pour tomber, on vise la lune pour apprendre a voler.",
"La route est longue ? Normal, c'est celle qui mene au sommet.",
"Aujourd'hui tu codes dans le bruit, demain on ecoutera ton histoire.",
"Les etoiles ne sont pas loin, ce sont tes excuses qui sont lourdes.",
"Travaille en silence. Ta fusee fera le bruit au decollage.",
"Parti de Ouaga, objectif : Espace.",
"YAM MODE : On ne recule pas, on ajuste la trajectoire."
]
p=random.choice(pubs)
print(f"\n--- PUB DU {datetime.datetime.now().strftime('%d/%m %H:%M')} ---\n{p}\n\n#Motivation #YAM\n")

