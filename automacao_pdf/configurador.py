import os
<<<<<<< HEAD
from dotenv import load_dotenv

CONFIG_ENV = ".env"

def armazenar_chave(provedor, chave):
    # Salva ou atualiza a chave API no arquivo ENV
    campo_provedor = f"{provedor.upper()}_KEY"
    linhas_atualizadas = []
    chave_cadastrada = False

    # 1. Se o arquivo já existe, lê as chaves antigas para preservar os outros provedores
    if os.path.exists(CONFIG_ENV):
        with open(CONFIG_ENV, "r", encoding="utf-8") as f:
            for linha in f:
                # Se a linha começar com o provedor atual (ex: GEMINI_KEY=), nós a substituímos
                if linha.strip().startswith(f"{campo_provedor}="):
                    linhas_atualizadas.append(f"{campo_provedor}={chave.strip()}\n")
                    chave_cadastrada = True
                else:
                    linhas_atualizadas.append(linha)

    # 2. Se a chave não existia antes (ou o arquivo é novo), adiciona ela ao final
    if not chave_cadastrada:
        linhas_atualizadas.append(f"{campo_provedor}={chave.strip()}\n")

    # 3. Grava as informações de volta no arquivo oculto
    with open(CONFIG_ENV, "w", encoding="utf-8") as f:
        f.writelines(linhas_atualizadas)

def carregar_chave(provedor):
    """Carrega o arquivo .env e busca a chave do provedor solicitado."""
    # Recarrega o arquivo .env para garantir que pegamos alterações recentes
    load_dotenv(dotenv_path=CONFIG_ENV, override=True)
    
    nome_variavel = f"{provedor.upper()}_KEY"
    
    # Busca a variável de ambiente do sistema operacional
    return os.getenv(nome_variavel)
=======
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
>>>>>>> 63c5e65e9a20ccc8c6f8ae10b93ed55363617f49
