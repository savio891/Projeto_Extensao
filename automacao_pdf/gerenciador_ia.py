from tkinter import messagebox

def seletor_ia(provider, key, model):
    provider = provider.lower()

    if provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=key)
        model_obj = genai.GenerativeModel(model)

        def executar_gemini(instrucoes, texto):
            response = model_obj.generate_content(f"{instrucoes}\n\nTexto do PDF:\n{texto}")
            return response.text
        return executar_gemini
    
    elif provider == "claude":
        import anthropic
        client = anthropic.Anthropic(api_key=key)

        def executar_claude(instrucoes, texto):
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": f"{instrucoes}\n\nTexto do PDF:\n{texto}"}
                ]
            )

            return response.content[0].text
        return executar_claude
    
    elif provider == "openai":
        import openai
        client = openai.OpenAI(api_key=key)

        def executar_openai(instrucoes, texto):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": f"{instrucoes}\n\nTexto do PDF:\n{texto}"}
                ]
            )
            return response.choices[0].message.content
        return executar_openai
    else:
        messagebox.showwarning(f"Aviso:", "É preciso selecionar um provedor IA!")
        return None
    
def listar_modelos_disponiveis(provider, key, model=""):
    if not key or not key.strip():
        return []
    
    provider = provider.lower()
    modelos = []

    try:
        if provider == "gemini":
            import google.generativeai as genai
            from google.api_core import exceptions as google_exceptions
            
            try:
                genai.configure(api_key=key.strip())
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        nome_limpo = m.name.split('/')[-1]

                        # FILTRO INTELIGENTE: Ignora modelos descontinuados, experimentais ou de robótica
                        modelos_obsoletos = ["tunedModels", "-preview", "robotics", "vision"]
                        if any (modelo in m.name for modelo in modelos_obsoletos):
                            continue # Pula este modelo e vai para o próximo

                        if nome_limpo.startswith("gemini-") and "tunedModels" not in m.name:
                            if nome_limpo not in modelos:
                                modelos.append(nome_limpo)
                modelos.sort()
            except google_exceptions.ResourceExhausted:
                return ["ERRO: Cota esgotada ou sem saldo no Google Gemini"]
            except google_exceptions.InvalidArgument:
                return ["ERRO: Chave API inválida no Gemini"]
            except Exception as e:
                # Captura de segurança caso o Google mude a classe do erro de saldo
                if "quota" in str(e).lower() or "exhausted" in str(e).lower():
                    return ["ERRO: Cota esgotada ou sem saldo no Google Gemini"]
                return [f"ERRO: Falha na API do Gemini ({str(e)})"]

        elif provider == "openai":
            import openai
            try:
                client = openai.OpenAI(api_key=key.strip())
                lista_api = client.models.list()

                for m in lista_api.data:
                    id_modelo = m.id

                    # 1. FILTRO DE PREFIXO: Garante que pertence às famílias de chat estáveis
                    if id_modelo.startswith("gpt-") or (id_modelo.startswith("o") and id_modelo[1:2].isdigit()):
                        
                        # 2. FILTRO DE OBSOLETOS: Evita modelos experimentais, de áudio ou datados antigamente
                        modelos_obsoletos = ["-realtime", "-audio", "-preview", "2024", "2023", "instruct"]
                        if any(modelo in id_modelo for modelo in modelos_obsoletos):
                            continue # Pula esses modelos específicos

                        if id_modelo not in modelos:
                            modelos.append(id_modelo)

                    # Adiciona o gpt-4o e o gpt-4o-mini manualmente como garantia se a API omitir
                if not modelos:
                    modelos = ["gpt-4o-mini", "o3-mini", "gpt-4o", "o1"]

                modelos.sort()
            except openai.RateLimitError:
                return ["ERRO: Conta sem saldo ou plano expirado na OpenAI"]
            except openai.AuthenticationError:
                return ["ERRO: Chave API inválida na OpenAI"]
            except Exception as e:
                # Captura cirúrgica do erro JSON 'insufficient_quota' enviado no seu log
                erro_msg = str(e).lower()
                if "quota" in erro_msg or "insufficient" in erro_msg or "credit" in erro_msg:
                    return ["ERRO: Conta sem saldo ou plano expirado na OpenAI"]
                return [f"ERRO: Falha na API da OpenAI ({str(e)})"]

        elif provider == "claude":
            try:
                import anthropic
                
                # Inicializa o cliente real com a chave
                client = anthropic.Anthropic(api_key=key)
                
                # Limpa o texto do modelo digitado
                modelo_teste = str(model).strip()
                
                # Se o usuário ainda não digitou nada ou está com o placeholder, 
                # usamos um modelo padrão apenas para testar se a CHAVE é válida e tem saldo.
                if not modelo_teste or "Digite" in modelo_teste or "manual" in modelo_teste:
                    modelo_teste = "claude-sonnet-4-6" 

                # O VERDADEIRO TESTE REATIVADO:
                # Faz o ping usando o modelo para disparar as suas exceções caso haja erros!
                client.messages.create(
                    model=modelo_teste,
                    max_tokens=1,
                    messages=[
                        {"role": "user", "content": "Validar conexao"}
                    ]
                )
                
                # Se a chave e o modelo estão 100% corretos, retornamos uma lista vazia.
                # Isso indica para a interface que não há "sugestões" a preencher, deixando o campo livre.
                return []

            except anthropic.AuthenticationError:
                return ["ERRO: Chave inválida (caracteres incorretos ou revogada)."]
                
            except anthropic.APIStatusError as e:
                erro_msg = str(e).lower()
                if "credit" in erro_msg or "balance" in erro_msg or "quota" in erro_msg or e.status_code == 429:
                    return ["ERRO: Conta Anthropic sem saldo ou créditos."]
                    
                elif e.status_code == 404:
                    return [f"ERRO API (404): O modelo '{modelo_teste}' não foi encontrado."]
                    
                return [f"ERRO API ({e.status_code}): {e.message}"]
                
            except Exception as e:
                return [f"ERRO: Não foi possível validar."]
        
    except Exception as e:
        print(f"Erro ao listar modelos do {provider}: {str(e)}")
        return []

    return modelos