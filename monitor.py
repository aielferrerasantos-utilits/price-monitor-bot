import requests
from bs4 import BeautifulSoup
import random
import time
import json
import os

# 🔐 CONFIG (COLOCA SEUS DADOS AQUI)
TOKEN = "8225102414:AAEoWT4xfa56mKXVHeOUgQurq4Pjq7FjtZo" 
CHAT_ID = "7287966965" 

ARQUIVO_ESTADO = "estado.json"

produtos = [
    {
        "nome": "RTX 5060 Ti",
        "url": "https://www.pichau.com.br/placa-de-video-asus-geforce-rtx-5060-ti-prime-oc-edition-16gb-gddr7-128-bit-prime-rtx5060ti-o16g-nac",
        "preco_desejado": 3800
    },
    {
        "nome": "Ryzen 7 7800X3D",
        "url": "https://www.kabum.com.br/produto/426262",
        "preco_desejado": 2200
    },
    {
        "nome": "B650M-E WiFi",
        "url": "https://www.pichau.com.br/placa-mae-asus-tuf-gaming-b650m-e-wifi",
        "preco_desejado": 1100
    },
    {
        "nome": "Kingston NV3 1TB",
        "url": "https://www.kabum.com.br/produto/633107",
        "preco_desejado": 850
    },
    {
        "nome": "Husky Freezy 360",
        "url": "https://www.kabum.com.br/produto/593860",
        "preco_desejado": 200
    },
    {
        "nome": "Husky Dome 700",
        "url": "https://www.kabum.com.br/busca/gabinete-gamer-husky",
        "preco_desejado": 500
    },
    {
        "nome": "Fonte Redragon 650W",
        "url": "https://www.pichau.com.br/fonte-redragon-rgps-650w",
        "preco_desejado": 430
    },
    {
        "nome": "Attack Shark X11",
        "url": "https://www.amazon.com.br/dp/B0D3KQVQXK",
        "preco_desejado": 140
    },
    {
        "nome": "Kumara Pro",
        "url": "https://www.pichau.com.br/teclado-magnetico-redragon-kumara-pro",
        "preco_desejado": 190
    }
]

headers_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r") as f:
            return json.load(f)
    return {}

def salvar_estado(estado):
    with open(ARQUIVO_ESTADO, "w") as f:
        json.dump(estado, f)

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def pegar_preco_ml(soup):
    try:
        preco = soup.find("span", {"class": "andes-money-amount__fraction"})
        return float(preco.text.replace(".", "").replace(",", "."))
    except:
        return None

def pegar_preco_generico(soup):
    try:
        preco = soup.find("span")
        texto = preco.text.replace("R$", "").replace(".", "").replace(",", ".")
        return float(texto)
    except:
        return None

def verificar():
    estado = carregar_estado()
    agora = time.time()
    headers = {"User-Agent": random.choice(headers_list)}

    for p in produtos:
        try:
            r = requests.get(p["url"], headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")

            if "mercadolivre" in p["url"]:
                preco = pegar_preco_ml(soup)
            else:
                preco = pegar_preco_generico(soup)

            if preco:
                print(f"{p['nome']} = R$ {preco}")

                ultima = estado.get(p["nome"], 0)
                passou_12h = (agora - ultima) > 43200

                if preco <= p["preco_desejado"]:
                    enviar_telegram(f"🔥 PROMOÇÃO!\n{p['nome']}\nR$ {preco}\n{p['url']}")
                    estado[p["nome"]] = agora

                elif passou_12h:
                    enviar_telegram(f"ℹ️ Atualização:\n{p['nome']}\nR$ {preco}")
                    estado[p["nome"]] = agora

        except Exception as e:
            print(f"Erro em {p['nome']}: {e}")

    salvar_estado(estado)

if __name__ == "__main__":
    verificar()
