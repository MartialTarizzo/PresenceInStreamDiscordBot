### bot_surveillance_discord.py

#==========================================================================
# Premier essai de bot discord pour suivre la présence des participants
# Fonctionne en ligne de commande
# 
# Résumé du développement :
# 	
# 1- téléchargement des sources de la dernière version de python
# (discord ne marche que si >3.6)
# 
# 2- compilation de python, installation dans ~/python382
# 
# 3- création d'un environnement virtuel pour bosser l'esprit tranquille
# 
# 4- chargement des librairies indispensables. Voilà l'état actuel. De
# mémoire, je n'ai installé avec PIP que celles marquées d'une (*), les
# autres sont des dépendances
# aiohttp==3.6.2
# async-timeout==3.0.1
# attrs==19.3.0
# chardet==3.0.4
# cycler==0.10.0
# discord.py==1.3.3                 (*)
# idna==2.9
# kiwisolver==1.2.0
# matplotlib==3.2.1                 (*)
# multidict==4.7.5
# numpy==1.18.4
# pyparsing==2.4.7
# python-dateutil==2.8.1         (*)
# python-dotenv==0.13.0
# six==1.14.0
# websockets==8.1
# yarl==1.4.2
# 
# 5- dans le répertoire où est installé le fichier python du bot,
# écriture d'un fichier de configuration .env. Ce fichier contient des
# infos qui n'ont rien à faire dans le code (token du bot entre autre !)
# 
# 6- dans le site web discord developer, créer une application, un bot,
# et l'enregistrer dans le serveur discord
# 
# 7- lancement dans un terminal du bot par
# ~$ python3 bot_surveillance_discord.py
# Le bot doit se connecter sur le serveur et écrire dans le terminal
# un truc du genre :
# ===========================
# SuiviPresenceInStream#1969 est connecté au serveur : xxxx(id: .....)
# Participants inscrits dans le serveur :
# - ***
# - ***
# - SuiviPresenceInStream
# * Surveillance en attente (ouvrir un salon vocal avant !start ) *
# ===========================
# 
# Tout est prêt, il n'y a plus qu'à lancer les commandes du bot, une
# fois un salon vocal ouvert sur le serveur.
# 
# ***** Les commandes du bot ********
# !start
# lance la surveillance du serveur. Si un serveur vocal n'est pas
# ouvert, te prévient !
# 
# !bye
# sauve les données dans le répertoire du bot, et le ferme proprement.
# Plus précisément, sauve deux graphiques (temps de présence par
# utilisateur et nombre d'utilisateurs en fonction du temps) et un
# fichier texte csv contenant les infos permettant de reconstruire les
# graphiques. cf PJ
# 
# En plus pour le plaisir :
# !graph_users
# provoque l'inclusion dans le chat discord du graphique "temps par utilisateur"
# 
# !graph_headcount
# provoque l'inclusion dans le chat du graphique effectif=f(t)
# 
# !save_all
# sauve la même chose que !bye, mais sans arrêter le bot
#=============================================================================

# importations
import discord
from discord.ext import commands, tasks
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from dotenv import load_dotenv

## Récupération des données d'environnement
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN') 	# le token du bot
GUILD = os.getenv('DISCORD_GUILD')	# le nom du serveur
BOTADMIN=os.getenv('BOTADMIN')		# l'administrateur du bot. Seul autorisé pour les commandes

Liste_autorisee = [BOTADMIN]

# chemin vers le script du bot ; utilisé pour la sauvegarde des fichiers (images, ...)
BOTPATH=os.path.dirname(os.path.realpath(__file__))

# l'intervalle de temps entre deux mesures
time_interval = int(os.getenv('TIME_INTERVAL'))

## variables globales

# pour contenir le nombre d'utilisateurs dans le salon vocal en fonction du temps (en unité 'time_interval')
liste_effectifs = []

# dictionnaire des durées cumulées pour chaque utilisateur
dict_uptime = {}

## les commandes du bot sont préfixées par '!'
client = commands.Bot(command_prefix = '!')

## gestion des droits
# seul l'admin du bot peut emmetre les commandes
def is_admin(ctx):
	personne = str(ctx.message.author)
	return personne in Liste_autorisee 
	
## coroutines ----------------------------------

# déclenché au démarrage du bot. 
# écriture d'infos de démarrage dans le terminal
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


	
# Cette commande, permet de démarrer le suivi de présence dans le salon vocal de la personne éxécutant la commande
# la surveillance ne sera déclenchée que s'il existe un serveur vocal actif
@client.command()
async def start(ctx):

	if not is_admin(ctx): return

	if ctx.message.author.voice == None:
		await ctx.send("*Pas de salon vocal ouvert ...*")
		return
	
	await ctx.send("**Surveillance en cours ...**")
	conec.start(ctx)

# Boucle temporelle qui effectue le suivi
# TODO : il faudrait voir s'il est possible de faire autre chose que du polling
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

# Commande permettant d'imprimer dans le terminal une liste des utilisateurs présents
# avec leur durée de présence    
@client.command()
async def up(ctx):
	if not is_admin(ctx): return

	print('---------------------------------------')
	for u,t in dict_uptime.items():
		print(f'{u} présent pendant {t*time_interval} s')

	
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

# sauvegarde des graphiques et des données dans le répertoire du bot
def save_graphs_and_data():	
	save_graph_users()
	save_graph_headcount()
	save_data()

# une commande discord pour tout sauver. permet d'avoir des instantanés. Utile ?
@client.command()
async def save_all(ctx):
	save_graphs_and_data()

## Arrêt du bot
# fermeture propre du bot, avec sauvegarde automatique des graphiques et des données
@client.command()
async def bye(ctx):
	if not is_admin(ctx): return
	
	save_graphs_and_data()
	await ctx.send("**Extinction du bot !**")
	await client.close()


## Le lancement du bot
client.run(TOKEN)
