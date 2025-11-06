import os
import discord
import asyncio
import googletrans
#pip install googletrans==3.1.0a0
from googletrans import Translator
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import json
import hanzidentifier
from fastapi import FastAPI
from typing import List, Union
import logging
import re

logging.basicConfig(level=logging.INFO)

app = FastAPI()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
client = discord.Client(intents=intents)

translator = Translator()

url = "https://ko.wiktionary.org/wiki/"


def clean_text(text: str) -> str:
    """Nettoie les textes avec retours, tabulations, etc."""
    return re.sub(r"\s+", " ", text).strip()


def get_hanja(word):
  url = "https://koreanhanja.app/" + word
  reponse = requests.get(url)
  reponse.encoding = reponse.apparent_encoding

  if reponse.status_code == 200:
    html = reponse.text

    soup = BeautifulSoup(html, 'html5lib')
    if soup.find("a"):
      hanja = soup.find("a").text
      return hanja
    else:
      return "pas de hanja trouvé"

  else:
    return "error : " + str(reponse.status_code)


def get_hanja_def(hanja):
  url = "https://koreanhanja.app/"

  reponse = requests.get(url + hanja)
  reponse.encoding = reponse.apparent_encoding

  if reponse.status_code == 200:
    html = reponse.text

    soup = BeautifulSoup(html, 'html5lib')
    if soup.find("td"):
      e_hanjas = soup.find_all("td")
      return e_hanjas[1].text
    else:
      return "pas de hanja trouvé"

  else:
    return "error : " + str(reponse.status_code)


def get_hanja_exemple(hanja):

  url = "https://koreanhanja.app/"

  logging.warning("hanja: " + hanja)
  reponse = requests.get(url + hanja)
  reponse.encoding = reponse.apparent_encoding

  if reponse.status_code == 200:
    html = reponse.text

    soup = BeautifulSoup(html, 'html5lib')
    if soup.find("table", class_="similar-words"):
      e_hanjas = soup.find("table", class_="similar-words")
      hanjas = e_hanjas.find_all("tr")
      logging.warning("hanja exemple: " + hanjas[1].text)
      return hanjas
    else:
      return "Pas d'exemple trouvé"

  else:
    return "error : " + str(reponse.status_code)
  

@app.get("/hanja/{word}")
async def hanja_def(word: str):
    """
    Analyse un mot coréen et retourne :
    - Les hanja correspondants
    - Leur définition
    - Quelques exemples
    """
    hanja = get_hanja(word)

    # Si rien trouvé
    if hanja == "pas de hanja trouvé":
        return {"message": "pas de hanja trouvé"}

    # Sinon, on construit une réponse JSON complète
    result = {
        "mot": word,
        "hanja": hanja,
        "details": []
    }

    table_hanja = [*hanja]  # on sépare chaque caractère hanja

    for h in table_hanja:
        try:
            def_hanja = clean_text(get_hanja_def(h))
            hanja_exemples = get_hanja_exemple(h)

            # Formatage des exemples
            if isinstance(hanja_exemples, str):
                exemples = [hanja_exemples]
            else:
                exemples = [ex.text for ex in hanja_exemples[:5]]  # max 5 exemples

            result["details"].append({
                "caractere": h,
                "definition": def_hanja,
                "exemples": exemples
            })

        except Exception as e:
            result["details"].append({
                "caractere": h,
                "erreur": str(e)
            })

    return result

"""
@bot.command(aliases=["hanja"])
async def hanja_def(ctx, word):
  
  hanja = get_hanja(word)
  if hanja == "pas de hanja trouvé":
    await ctx.send("pas de hanja trouvé")
  else:
    try:
      await ctx.send(f"{word} hanja: {hanja}")
      table_hanja = [*hanja]
        
      for hanja in table_hanja:
        def_hanja = get_hanja_def(hanja)
        await ctx.send(f"***********\n{hanja}: {def_hanja}\n***********")

        hanja_exemples = get_hanja_exemple(hanja)
        if isinstance(hanja_exemples, str):
            await ctx.send(hanja_exemples)
        else:
            for i, hanja_exemple in enumerate(hanja_exemples):
                if i >= 5:
                    break
                await ctx.send(f"---------------{hanja_exemple.text}")
            
    except discord.errors.HTTPException as e:
        if e.status == 429: 
            await ctx.send("Désolé, je dois faire une pause. Réessayez dans quelques secondes.")
            return
        raise
"""
        

@bot.command(aliases=['tr'])
async def translate_sentence(ctx, lang_to, *args):
  """
    Translates the given text to the language `lang_to`.
    The language translated from is automatically detected.
    """

  lang_to = lang_to.lower()
  if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
    raise commands.BadArgument("Invalid language to translate text to")

  text = ' '.join(args)
  translator = googletrans.Translator()
  text_translated = translator.translate(text, dest=lang_to).text
  await ctx.send(text_translated)


@bot.command(aliases=['trad'])
async def translate(ctx, lang_to, arg):

  lang_to = lang_to.lower()
  if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
    raise commands.BadArgument("Invalid language to translate text to")

  hanja = get_hanja(arg)
  if hanja == "pas de hanja trouvé":
    await ctx.send("pas de hanja trouvé")
  else:
    await ctx.send(f"hanja: {hanja}")
    table_hanja = [*hanja]

    for hanja in table_hanja:
      def_hanja = get_hanja_def(hanja)
      await ctx.send(f"{hanja}: {def_hanja}")
      #await ctx.send(f"{kanji} => {trad_kanji_en} => {trad_kanji_kr}")

  translator = googletrans.Translator()

  text_translated = translator.translate(arg, dest=lang_to).text

  await ctx.send(f"{arg} in {lang_to} means **{text_translated}**")
  """

  trad_china = translator.translate(arg, dest='zh-tw').text
  src = translator.translate(arg, dest='zh-tw').src

  table_china = [*trad_china]
  await ctx.send(f"Hanja : **{trad_china}**")

  for kanji in table_china:
    trad_kanji_en = translator.translate(kanji, dest='en').text
    trad_kanji_kr = translator.translate(kanji, dest='ko').text
    await ctx.send(f"{kanji} => {trad_kanji_en} => {trad_kanji_kr}")

  """

  src_url = ""
  if src == "fr":
    src_url = "fra"
  if src == "en":
    src_url = "eng"
  if src == "ko":
    src_url = "kor"

  dest_url = ""
  if lang_to == "french":
    dest_url = "fra"
  if lang_to == "english":
    dest_url = "eng"
  if lang_to == "korean":
    dest_url = "kor"

  response = requests.get(
      f"https://api.dev.tatoeba.org/unstable/sentences?lang={src_url}&q={arg}&trans={dest_url}"
  )
  rep = response.json()

  await ctx.send("__**EXEMPLE :**__")

  if rep['data'] == []:
    await ctx.send("*No exemple found*")
  else:

    for sentence in rep['data']:
      if sentence['text'].find(arg):
        sentence['text'] = sentence['text'].replace(arg, f"**{arg}**")
      await ctx.send(f"Ex : original sentence =>  {sentence['text']}")
      if len(sentence['translations'][0]) == 0:
        for traduction in sentence['translations'][1]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"Translate sentence =>  {traduction['text']}")
      else:
        for traduction in sentence['translations'][0]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"Translate sentence =>  {traduction['text']}")
