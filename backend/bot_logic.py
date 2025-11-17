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
      return "No hanja found"

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
      return "No hanja found"

  else:
    return "error : " + str(reponse.status_code)


def get_hanja_exemple(hanja):

  url = "https://koreanhanja.app/"

  reponse = requests.get(url + hanja)
  reponse.encoding = reponse.apparent_encoding

  if reponse.status_code == 200:
    html = reponse.text

    soup = BeautifulSoup(html, 'html5lib')
    if soup.find("table", class_="similar-words"):
      e_hanjas = soup.find("table", class_="similar-words")
      hanjas = e_hanjas.find_all("tr")
      return hanjas
    else:
      return "Pas d'exemple trouvé"

  else:
    return "error : " + str(reponse.status_code)
  

def translate_sentence(arg):

  try:
      translator = googletrans.Translator()
      result = translator.translate(arg, dest='en').text
      text_translated = result

      logging.warning("hanjadu translateur " + text_translated)
      return text_translated

  except Exception as e:
      
      # Valeur par défaut quand la traduction échoue
      return "No translation available"
  

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
    if hanja == "No hanja found":
        return {"message": "No hanja found for this word."}
    
    translated_word = translate_sentence(word)

    # Sinon, on construit une réponse JSON complète
    result = {
        "translation": translated_word,
        "mot": word,
        "hanja": hanja,
        "details": []
    }

    table_hanja = [*hanja]

    for h in table_hanja:
        try:
            def_hanja = clean_text(get_hanja_def(h))
            hanja_exemples = get_hanja_exemple(h)

            # Formatage des exemples
            if isinstance(hanja_exemples, str):
                exemples = [hanja_exemples]
            else:
                exemples = [ex.text for ex in hanja_exemples]

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
