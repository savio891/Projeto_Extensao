import os

CONFIG_ENV = ".env"

def armazenar_chave(provedor, chave):
    # Salva ou atualiza a chave API no arquivo ENV (Sua lógica perfeita)
    campo_provedor = f"{provedor.upper()}_KEY"
    linhas_atualizadas = []
    chave_cadastrada = False

    if os.path.exists(CONFIG_ENV):
        with open(CONFIG_ENV, "r", encoding="utf-8") as f:
            for linha in f:
                if linha.strip().startswith(f"{campo_provedor}="):
                    linhas_atualizadas.append(f"{campo_provedor}={chave.strip()}\n")
                    chave_cadastrada = True
                else:
                    linhas_atualizadas.append(linha)

    if not chave_cadastrada:
        linhas_atualizadas.append(f"{campo_provedor}={chave.strip()}\n")

    with open(CONFIG_ENV, "w", encoding="utf-8") as f:
        f.writelines(linhas_atualizadas)

def carregar_chave(provedor):
    """
    Carrega a chave lendo o arquivo .env diretamente como texto.
    Isso evita bugs de cache de memória do load_dotenv que corrompem a string da chave.
    """
    campo_provedor = f"{provedor.upper()}_KEY="
    
    if not os.path.exists(CONFIG_ENV):
        return None
        
    try:
        with open(CONFIG_ENV, "r", encoding="utf-8") as f:
            for linha in f:
                linha_limpa = linha.strip()
                if linha_limpa.startswith(campo_provedor):
                    # Divide a linha no '=' e pega apenas o valor da chave à direita
                    chave = linha_limpa.split("=", 1)[1]
                    return chave.strip()
    except Exception:
        return None
    return None

def obter_chaves_salvas(provedor):
    """Retorna a chave em formato de lista para o Combobox da interface"""
    chave = carregar_chave(provedor)
    return [chave] if chave else []