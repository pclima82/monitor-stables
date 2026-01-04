import requests
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO ---
# --- CONFIGURAÇÃO: MODO DE TESTE (ALVOS ALTOS PARA FORÇAR CSV) ---
ASSETS = [
    # TIER 1: AS ROCHAS
    {
        "symbol": "USDT", 
        "network": "arbitrum", 
        "address": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 
        "target_buy": 1.02, # <--- MUDAMOS PARA 1.02 (Vai disparar compra)
        "target_sell": 1.05
    },
    {
        "symbol": "USDC.e", 
        "network": "arbitrum", 
        "address": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 
        "target_buy": 1.02, # <--- FORÇADO
        "target_sell": 1.05
    },
    # TIER 2: VOLÁTEIS
    {
        "symbol": "USDe", 
        "network": "arbitrum", 
        "address": "0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34", 
        "target_buy": 1.02, # <--- FORÇADO
        "target_sell": 1.05
    },
    {
        "symbol": "FRAX", 
        "network": "arbitrum", 
        "address": "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F", 
        "target_buy": 1.02, # <--- FORÇADO
        "target_sell": 1.05
    },
    {
        "symbol": "MIM", 
        "network": "arbitrum", 
        "address": "0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A", 
        "target_buy": 1.02, # <--- FORÇADO
        "target_sell": 1.05
    }
]

FILENAME = "oportunidades.csv"

def get_price(network, address):
    if "COLE_" in address: return None
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        data = requests.get(url, timeout=10).json()
        best_pair = None
        max_liq = 0
        if data.get('pairs'):
            for pair in data['pairs']:
                if pair['chainId'] != network: continue
                if pair['baseToken']['address'].lower() != address.lower(): continue
                liq = float(pair.get('liquidity', {}).get('usd', 0))
                if liq > max_liq:
                    max_liq = liq
                    best_pair = pair
            if best_pair and max_liq > 10000:
                return {'price': float(best_pair['priceUsd']), 'dex': best_pair['dexId']}
    except:
        pass
    return None

def main():
    print("--- INICIANDO VARREDURA GITHUB ACTIONS ---")
    new_data = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for asset in ASSETS:
        data = get_price(asset['network'], asset['address'])
        if data:
            price = data['price']
            symbol = asset['symbol']
            tipo = "NEUTRO"
            
            if price <= asset['target_buy']:
                tipo = "COMPRA"
                print(f"!!! OPORTUNIDADE {symbol}: ${price}")
            elif price >= asset['target_sell']:
                tipo = "VENDA"
            
            # Só salvamos se for Oportunidade para não encher o CSV de lixo
            if tipo != "NEUTRO":
                row = {
                    "Timestamp": now,
                    "Moeda": symbol,
                    "Tipo": tipo,
                    "Preco": price,
                    "DEX": data['dex']
                }
                new_data.append(row)

    if new_data:
        df = pd.DataFrame(new_data)
        # Se o arquivo já existe, carrega e adiciona. Se não, cria.
        if os.path.exists(FILENAME):
            df.to_csv(FILENAME, mode='a', header=False, index=False)
        else:
            df.to_csv(FILENAME, mode='w', header=True, index=False)
        print("Dados salvos no CSV.")
    else:
        print("Nenhuma oportunidade encontrada nesta rodada.")

if __name__ == "__main__":
    main()
