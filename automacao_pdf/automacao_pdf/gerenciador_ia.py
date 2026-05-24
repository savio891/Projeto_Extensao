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
        messagebox.showwarning(f"Provedor '{provider} não é suportado.'")
        return None