import os
import json

CONFIG = "config.json"

def armazenar_chave(provedor, chave):
    # Salva a chave API no arquivo JSON
    dados = {}

    # Se o arquivo já existir, lê o que está lá para não apagar chaves de outros provedores
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception:
            dados = {} # Caso o arquivo esteja corrompido, começar do zero
    
    # Atualiza ou insere a chave do provedor atual
    dados[provedor.lower()] = chave.strip()

    # Grava de volta no arquivo de forma organizada
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_chave(chave_provedor):
    if not os.path.exists(CONFIG):
        return None
    
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Retorna a chave do provedor ou valor nulo
            return dados.get(chave_provedor.lower(), None)
    except Exception:
        return None
