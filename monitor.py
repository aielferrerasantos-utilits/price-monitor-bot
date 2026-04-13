import requests
from bs4 import BeautifulSoup
import random
import time
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# 🔐 CONFIG (USE VARIÁVEIS DE AMBIENTE)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("❌ Erro: Configure TELEGRAM_TOKEN e TELEGRAM_CHAT_ID no arquivo .env")

ARQUIVO_ESTADO = "estado.json"

# Lista de produtos para monitorar
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
    """Carrega o estado anterior de monitoramento"""
    if os.path.exists(ARQUIVO_ESTADO):
        try:
            with open(ARQUIVO_ESTADO, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar estado: {e}")
            return {}
    return {}

def salvar_estado(estado):
    """Salva o estado de monitoramento"""
    try:
        with open(ARQUIVO_ESTADO, "w") as f:
            json.dump(estado, f, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar estado: {e}")

def enviar_telegram(msg):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        response = requests.post(url, data=data, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Erro ao enviar Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar Telegram: {e}")

def pegar_preco_ml(soup):
    """Extrai preço do Mercado Livre"""
    try:
        preco = soup.find("span", {"class": "andes-money-amount__fraction"})
        if preco:
            return float(preco.text.replace(".", "").replace(",", "."))
    except Exception as e:
        print(f"Erro ao parsear Mercado Livre: {e}")
    return None

def pegar_preco_generico(soup):
    """Extrai preço de sites genéricos"""
    try:
        preco = soup.find("span")
        if preco:
            texto = preco.text.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(texto)
    except Exception as e:
        print(f"Erro ao parsear preço: {e}")
    return None

def verificar():
    """Verifica preços de todos os produtos"""
    estado = carregar_estado()
    agora = time.time()
    headers = {"User-Agent": random.choice(headers_list)}

    print(f"\n🔍 Verificando preços em {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    for p in produtos:
        try:
            print(f"📦 Checando: {p['nome']}...", end=" ")
            
            r = requests.get(p["url"], headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            if "mercadolivre" in p["url"]:
                preco = pegar_preco_ml(soup)
            else:
                preco = pegar_preco_generico(soup)

            if preco:
                print(f"R$ {preco:.2f}")

                ultima = estado.get(p["nome"], 0)
                passou_12h = (agora - ultima) > 43200

                if preco <= p["preco_desejado"]:
                    msg = f"🔥 PROMOÇÃO ENCONTRADA!\n\n{p['nome']}\n💰 R$ {preco:.2f}\n🎯 Preço desejado: R$ {p['preco_desejado']}\n\n🔗 {p['url']}"
                    enviar_telegram(msg)
                    estado[p["nome"]] = agora
                    print(f"   ✅ Alerta enviado!")

                elif passou_12h:
                    msg = f"ℹ️ ATUALIZAÇÃO DE PREÇO\n\n{p['nome']}\n💰 R$ {preco:.2f}\n🎯 Preço desejado: R$ {p['preco_desejado']}\n\n🔗 {p['url']}"
                    enviar_telegram(msg)
                    estado[p["nome"]] = agora
            else:
                print("❌ Não conseguiu extrair preço")

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout ao acessar {p['nome']}")
        except Exception as e:
            print(f"❌ Erro em {p['nome']}: {e}")

    salvar_estado(estado)
    print("=" * 50)
    print("✅ Verificação concluída!\n")

if __name__ == "__main__":
    try:
        verificar()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")