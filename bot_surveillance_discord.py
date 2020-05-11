# ## TestSuiviPresenceInStreamBot
# Essai de bot discord pour suivre la présence des participants

import discord
from discord.ext import commands, tasks
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from dotenv import load_dotenv


## Environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOTADMIN=os.getenv('BOTADMIN')
Liste_autorisee = [BOTADMIN]

# chemin vers le script du bot ; utilisé pour la sauvegarde des fichiers (images, ...)
BOTPATH=os.path.dirname(os.path.realpath(__file__))


## variables globales
# l'intervalle de temps entre deux mesures
time_interval = 2

# pour contenir le nombre d'utilisateurs dans le salon vocal en fonction du temps (en unité 'time_interval')
liste_effectifs = []

# dictionnaire des durées cumulées pour chaque utilisateur
dict_uptime = {}

## command prefix
client = commands.Bot(command_prefix = '!')

## gestion des droits
# seul l'admin du bot peut emmetre les commandes
def is_admin(ctx):
	personne = str(ctx.message.author)
	return personne in Liste_autorisee 
	
## coroutines ----------------------------------

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="le serveur vocal"))

	for guild in client.guilds:
		if guild.name == GUILD:
			break

	print(
		f'{client.user} est connecté au serveur : '
		f'{guild.name}(id: {guild.id})\n'
	)
	print(f'Participants inscrits dans le serveur :')
	for member in guild.members:
		print(f'- {member.name}')
	print("* Surveillance en attente (ouvrir un salon vocal avant !start ) *")


#Cette commande, permet de compte le nombre de présents dans le salon vocal de la personne éxécutant la commande
@client.command()
async def cb(ctx, *args):
	if not is_admin(ctx): return

	if ctx.message.author.voice == None:
		await ctx.send("*Pas de salon vocal ouvert ...*")
	else:
		personnes = ctx.message.author.voice.channel.members
		x = len(personnes)
		if x == 1:
			await ctx.send("Une seule personne est connectée sur ce salon vocal")
		else:
			a = str(x)
			mess = "Nous sommes actuellement"+ " "+  a + " " +"personnes connectées sur ce salon vocal"
			await ctx.send(mess)
	
#Cette commande, permet de démarrer le suivi de présence dans le salon vocal de la personne éxécutant la commande
@client.command()
async def start(ctx):

	if not is_admin(ctx): return

	if ctx.message.author.voice == None:
		await ctx.send("*Pas de salon vocal ouvert ...*")
		return
	
	await ctx.send("**Surveillance en cours ...**")
	conec.start(ctx)

#Boucle temporelle qui effectue le suivi
@tasks.loop(seconds = time_interval, count = 50000 / time_interval)
async def conec(ctx):
	if ctx.message.author.voice == None:
		print("pas de suivi : Admin hors du salon vocal après démarrage de la surveillance...")
		return

	# print(datetime.datetime.now().strftime('%Hh %Mm %Ss %f'))
	p = ctx.author.voice.channel.members
	
	# enregistrement du nombre de présents à la date courante
	liste_effectifs.append(len(p))
	
	# incrémentation de la durée de présence de chaque utilisateur présent
	for user in p:
			c = str(user)
			#print(c)
			if c not in dict_uptime:
				dict_uptime[c] = 0
			else:
				dict_uptime[c] += time_interval

#Commande permettant d'afficher une liste de suivi avec pour format [identifiant, temps de présence]    
@client.command()
async def up(ctx):
	if not is_admin(ctx): return

	print('---------------------------------------')
	for u,t in dict_uptime.items():
		print(f'{u} présent pendant {t*time_interval} s')

#Commande permettant de renvoyer l'emploi du temps de la semaine (emploi du temps sous forme d'image enregistrée dans le dossier du bot)
@client.command()
async def edt(ctx):
	await ctx.send("Date de la dernière mise à jour : 05/05")
	await ctx.send(file=discord.File('edt/edt.png'))
	
## graphiques
# 1 - durée par utilisateur
# 1.a - la commande permettant l'inclusion du graphique dans discord

@client.command()
async def graph_users(ctx):
	if not is_admin(ctx): return
	
	f_name = save_graph_users()
	await ctx.send(file=discord.File(f_name))
	# suppression du fichier
	os.remove(f_name)

# 1.b sauvegarde du graphique dans le répertoire courant
def save_graph_users():

	def format_time(x, pos):
		'The two args are the value and tick position'
		return '%1.1f min' % (x /60)

	formatter = FuncFormatter(format_time)

	current_date_time = datetime.datetime.now().strftime('%y-%m-%d (%Hh %Mm %Ss)')
	
	lx = [] ; ly = []
	for u,t in dict_uptime.items():
		lx.append(u)
		ly.append(t)
	
	fig, ax = plt.subplots()
	ax.yaxis.set_major_formatter(formatter)
	plt.bar(lx,ly)
	ax.set( xlabel = "Pseudo", 
			title=f"Durée de présence {current_date_time}")
	ax.set_xticklabels(lx,rotation=-45, rotation_mode='anchor',
	horizontalalignment='left', verticalalignment='top')
	ax.tick_params(axis='x', labelsize=9)
	ax.grid()
	ax.autoscale()
	plt.tight_layout()
	
	f_name = f'{BOTPATH}/u_{current_date_time}.png'
	fig.savefig(f_name)
	return f_name
	
# 2 - Effectif en fonction du temps
# 2.a - la commande permettant l'inclusion du graphique dans discord

@client.command()
async def graph_headcount(ctx):
	if not is_admin(ctx): return
	
	f_name = save_graph_headcount()
	await ctx.send(file=discord.File(f_name))
	os.remove(f_name)

# 2.b la sauvegarde de l'image dans le répertoire courant
def save_graph_headcount():
	current_date_time = datetime.datetime.now().strftime('%y-%m-%d (%Hh %Mm %Ss)')
	n = len(liste_effectifs)
	lx = [i * time_interval for i in range(n)]
	
	fig, ax = plt.subplots()
	plt.plot(lx,liste_effectifs)
	ax.set( xlabel = "Temps (s)", 
			title=f"Effectif total {current_date_time}")
	ax.grid()
	ax.autoscale()
	plt.tight_layout()
	f_name = f'{BOTPATH}/eff_{current_date_time}.png'
	fig.savefig(f_name)
	return f_name
	
## sauvegarde des données

# écriture d'un fichier texte dans le répertoire du bot
def save_data():
	current_date_time = datetime.datetime.now().strftime('%y-%m-%d (%Hh %Mm %Ss)')
	f_name = f'{BOTPATH}/data_{current_date_time}.csv'
	with open(f_name,"w", encoding="utf8") as f:
		t = 0
		f.write(f'date (s)\teffectif\n')
		for eff in liste_effectifs:
			f.write(f'{t}\t{eff}\n')
			t += time_interval
		f.write('\npseudo\tdurée (s)\n')
		for u,t in dict_uptime.items():
			f.write(f'{u}\t{t}\n')

def save_graphs_and_data():	
	save_graph_users()
	save_graph_headcount()
	save_data()

# une commande discord pour tout sauver. Utile ?
@client.command()
async def save_all(ctx):
	save_graphs_and_data()

## Fermeture du bot
@client.command()
async def bye(ctx):
	if not is_admin(ctx): return
	
	save_graphs_and_data()
	await ctx.send("**Extinction du bot !**")
	await client.close()


## Le lancement du bot
client.run(TOKEN)
