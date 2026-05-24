from configurador import carregar_chave

def inserir_dados(provider, key, model):
    try:
        # Verifica se o usuário digitou o provedor da IA
        if not provider or provider.strip() == "":
            print("O provedor não foi informado. Por favor informá-lo para continuar o processamento.")
            return None
        
        # Verifica se o usuário digitou a chave
        if not key or key.strip() == "":
            saved_key = carregar_chave(provider)

            if saved_key:
                key_final = saved_key
            else:
                print(f"Chave para o provedor {provider} não foi informada. Por favor, insira uma chave.")
                return None
        else:
            # Caso a chave veio pelo terminal
            key_final = key.strip()
    
        # Verifica se o usuário digitou o model
        if not model or model.strip() == "":
            print("O nome do modelo não foi informado.")
            return None
        
        return key_final, model.strip()
    
    except Exception as e:
        print(f"Erro ao receber as informações:\n{str(e)}")
        return None
