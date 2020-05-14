@REM Pour Windows - testé sous W10
@REM Fichier de commande pour lancer le script de surveillance

@REM Définition de l'envrironnement virtuel, inclusion dans le path
@path = %CD%\venv\Scripts;%path%

REM Lancement du bot ...
python bot_surveillance_discord.py