import os
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
