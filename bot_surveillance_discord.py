import time
import discord
from discord.ext import commands, tasks
from itertools import cycle
from discord.utils import get
from discord import guild
import csv
import os

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)



# il y a des imports inutiles à ce jour, c'est en anticipation de futures améliorations
 
client = commands.Bot(command_prefix = '!')
status = cycle(['en maintenance','en maintenance'])


#Cette commande permet d'afficher sur le terminal, quand est-ce que le bot est prêt à éxecuter des commandes après son démarrage

@client.event
async def on_ready():
    change_status.start()

    print('Bot is ready') #Print renvoie sur le terminal

#Simple commande pour vérifier, si le bot est toujours capable de répondre en cas d'erreurs

@client.command()
async def p(ctx):
    await ctx.send("je suis prêt !") #ctx.send renvoie sur Discord

#L'argument ctx (contexte) permet comme son nom l'indique d'obtenir des informations sur la personne éxecutant la commande (auteur, salon dans lequel la commande a été demandée, ...)

#Cette commande, outre le fait qu'elle puisse diffuser des message plus ou moins intéressant, permet de vérifier si le bot s'actualise bien, parfois la durée est supérieure à celle choisie

@tasks.loop(seconds=3.1415)
async def change_status():
     await client.change_presence(activity=discord.Game(next(status)))

#Cette commande, permet de compte le nombre de présents dans le salon vocal de la personne éxécutant la commande



@client.command()
async def cb(ctx, *args):
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
async def ca(ctx):
    global liste_p
    global liste_p_t
    global y
    personne = str(ctx.message.author)
    if personne in Liste_autorisee:

        try:
            y = ctx.author.voice.channel.members
            await ctx.send("*!ca : Bien reçu !*")
            liste_p = []
            liste_p_t = []
            conec.start(ctx)
        except AttributeError:         #Gestion d'erreur
            await ctx.send("Vous devez être dans un salon vocal avant d'utiliser cette commande !")

#Boucle temporelle qui effectue le suivi

@tasks.loop(seconds = 2, count = 50000)
async def conec(ctx):
    
    p = ctx.author.voice.channel.members


    for i in range(len(p)):
            c = str(p[i])
           
            if c not in liste_p:
                liste_p.append(c)
                liste_p_t.append([c,0])
                
            if c in liste_p:
                liste_p_t[liste_p.index(c)][1] = liste_p_t[liste_p.index(c)][1]+2

#Commande permettant d'afficher une liste de suivi avec pour format [identifiant, temps de présence]    

@client.command()
async def up(ctx):
    
    personne = str(ctx.message.author)
    if personne in Liste_autorisee: #Gestion de permissions : permet de limiter l'utilisation des commandes sous forme de whitelist
        await ctx.send("*!up : Demande envoyée !*")
        try:
            if liste_p_t != []:
                for i in range(len(liste_p_t)):
                    liste_p_t[i][1] = liste_p_t[i][1]
                print('Retour de !up')
                print(liste_p_t)
            

            else: 
                print('Retour de !up')
                print('None')
        except NameError: #Gestion d'erreur
            await ctx.send("Erreur, la commande !ca n'a pas été lancée avant")
            await ctx.send("Je m'en occupe !")
            time.sleep(2)
            await ca(ctx)
        

#Commande permettant de renvoyer l'emploi du temps de la semaine (emploi du temps sous forme d'image enregistrée dans le dossier du bot)

@client.command()
async def edt(ctx):
    await ctx.send("Date de la dernière mise à jour : 05/05")
    await ctx.send(file=discord.File('edt.PNG'))
    



client.run('NzA4MzEzMDU2ODY1NjgxNDU4.XrV4pg.pIQpbGdHhdyEJp_IPygrJ0nGnZg')
