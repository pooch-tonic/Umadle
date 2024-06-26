import pandas as pd
import random
import discord
from utils import clean_string, convert_birthday

NAME_COL = 'Name'
ROMAJI_COL = 'Romaji'
IMAGE_COL = 'Image URL'
TITLE_COL = 'Title'
BIRTHDAY_COL = 'Birthday'
RELEASE_COL = 'Release date'
COMPARE_START_COL = 4
SESSION_CHARINDEX = 0
SESSION_TURNINDEX = 1

sessions = {}

# Fonction pour comparer les caractéristiques du personnage choisi par l'utilisateur avec le personnage cible
def compare_characters(user_character, target_character, characters_df):
    comparison = {}
    for column in characters_df.columns[COMPARE_START_COL:]:
        is_numeric = True

        try:
            user_value = pd.to_numeric(user_character[column])
            target_value = pd.to_numeric(target_character[column])
        except ValueError:
            if column == BIRTHDAY_COL:
                is_numeric = True
                user_value = convert_birthday(user_character[column])
                target_value = convert_birthday(target_character[column])
            elif column == RELEASE_COL:
                is_numeric = True
                user_value = user_character[column]
                target_value = target_character[column]
            else:
                is_numeric = False
                user_value = user_character[column]
                target_value = target_character[column]

        if is_numeric:
            if user_value == target_value:
                comparison[column] = (user_character[column],"[=]")
            elif user_value > target_value:
                comparison[column] = (user_character[column],"[-]")
            else:
                comparison[column] = (user_character[column],"[+]")
        else:
            if user_value == target_value:
                comparison[column] = (user_character[column],"[=]")
            else:
                comparison[column] = (user_character[column],"[!]")
            
    return comparison


# Boucle principale du jeu
async def play_game(ctx, user_id, characters_df):
    # print("Bienvenue dans Umadle ! Tentez de deviner le personnage du jour !")

    # Afficher les caractéristiques du personnage cible
    #print("Caractéristiques du personnage cible :")
    #print(target_character)

    startMsg = "New game started. Type `/game answer` to begin."
    msg = ""

    if (user_id in sessions):
        msg = "Discarded previous game session. " + startMsg
    else:
        msg = startMsg

    target_character_index = characters_df.sample(n=1).index[0]
    turns = 0

    sessions[user_id] = [target_character_index, turns]

    await ctx.respond(msg)

async def handle_answer(ctx, user_id, name, characters_df, autocomplete_names):
    if (user_id not in sessions):
        await ctx.respond("You don't have any game in progress. Type `/game play` to start one.", ephemeral=True)
        return
    
    if (name not in autocomplete_names):
        await ctx.respond(f"`{name}` is not a valid name. Try again with the correct spelling.", ephemeral=True)
        return
    
    target_character = characters_df.iloc[sessions[user_id][SESSION_CHARINDEX]]
    sessions[user_id][SESSION_TURNINDEX] += 1
    turns = sessions[user_id][SESSION_TURNINDEX]

    msg = f"**Turn {turns}: {name}**```"

    # Vérifier si le nom est correct
    if name == target_character[ROMAJI_COL]:
        for column in characters_df.columns[COMPARE_START_COL:]:
            msg += (f"\n[=] {column}: {target_character[column]}")

        turn_str = "turns" if turns > 1 else "turn"
        msg += f"```\nCongratulations! You guessed **{target_character[NAME_COL]}** - **{target_character[ROMAJI_COL]}** in **{turns}** {turn_str}."
        sessions.pop(user_id)

        embed = discord.Embed(
            title = target_character[ROMAJI_COL],
            description = target_character[NAME_COL]
        )
        imageurl = target_character[IMAGE_COL]
        embed.set_image(url = imageurl)
        embed.set_author(name = target_character[TITLE_COL])

        await ctx.respond(embed=embed, content=msg)
    else:
        # Trouver le personnage choisi par l'utilisateur dans le DataFrame
        user_character = characters_df[characters_df[ROMAJI_COL] == name].iloc[0]
        # Comparer les caractéristiques du personnage choisi par l'utilisateur avec le personnage cible
        comparison_result = compare_characters(user_character, target_character, characters_df)
        # Afficher le résultat de la comparaison
        #print("Différences entre les caractéristiques :")
        for key, value in comparison_result.items():
            if value[1] != user_character[key]:
                msg += (f"\n{value[1]} {key}: {value[0]}")
        msg += "\n----------\n"
        
        if turns < 10:
            msg += f"Title reveal in {11 - turns} turns."
        elif turns == 10:
            msg += f"Title reveal on next turn."
        else:
            msg += f"Title: {target_character[TITLE_COL]}"

        msg += "```"
        await ctx.respond(msg)
