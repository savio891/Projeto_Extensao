import os
from extrator import extrair_texto_seguro # Reutilizar o extrator
from tkinter import filedialog, messagebox # Recurso do Tkinter para selecionar diretórios
from gerenciador_ia import seletor_ia
from datetime import datetime

# Função que busca PROMPT em um diretório para ser anexado
def busca_instrucoes():
    try:
        caminho_prompt = filedialog.askopenfilename( 
            title="Selecione o arquivo de instruções para o processamento:",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        # Verifica se o usuário fechou a janela ou cancelou a operação
        return caminho_prompt if caminho_prompt else None
        
    except Exception as e:
        messagebox.showwarning("Aviso", f"Erro inesperado ao selecionar o arquivo de instruções:\n{str(e)}") 
        return None

# Selecionar diretório para escolher a pasta com PDFs a serem processados
def diretorio_entrada():
    try:
        caminho_entrada = filedialog.askdirectory(
            title="Selecione uma pasta com PDFs:",
            mustexist=True
        )
        
        # Verifica se realmente a pasta existe e está acessível
        if not caminho_entrada:
            return None
        
        # Verifica se o usuário tem permissão de leitura na pasta
        if not os.access(caminho_entrada, os.R_OK):
            messagebox.showwarning("Aviso", "Você não tem permissão de acesso a essa pasta.")
            return None
        
        return caminho_entrada
    
    except Exception as e:
        messagebox.showerror(
            "Erro inesperado",
            f"Ocorreu um erro ao tentar abrir a pasta:\n{str(e)}",
        )
        return None


# Define o local onde será salvo o resultado final do processamento
def diretorio_saida():
    try:
        caminho_salvamento = filedialog.asksaveasfilename( 
            title="Defina onde você deseja salvar o relatório final...",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile="resultado_final.txt"
        )

        if not caminho_salvamento:
            return None
        
        # Extrai apenas a pasta onde o arquivo será salvo
        pasta_destino = os.path.dirname(caminho_salvamento)
            
        # Verifica se o usuário tem permissão de ESCRITA (W_OK) na pasta de destino
        if not os.access(pasta_destino, os.W_OK):
            messagebox.showwarning("Aviso", "Você não tem permissão de gravação nesta pasta.")
            return None

        return caminho_salvamento
        
    except Exception as e:
        messagebox.showerror(
            "Aviso",
            f"Erro inesperado ao tentar escolher o local de salvamento do arquivo:\n{str(e)}"
        )
         
        return None
    
# Realizar o processamento dos arquivos PDFs mediante às instruções do PROMPT
def processar_arquivos(provider, key, model_version, caminho_prompt, pasta_entrada, pasta_saida, buscar_subpastas, callback_progresso, checar_cancelamento):
    try:
        # Configuração da IA usando os dados coletados da tela na hora do clique
        chamar_ia = seletor_ia(provider=provider, key=key, model=model_version)
        if not chamar_ia:
            return "Falha ao inicializar o servidor IA. Verifique se sua chave API ou Servidor estão corretos."
        
        # Carregamento do Prompt
        with open(caminho_prompt, "r", encoding="utf-8") as file:
            conteudo_prompt = file.read()

        # validação prompt termos imperativos
        caixa_baixa = conteudo_prompt.lower()
        termos_imperativos = ["comece", "gere", "use", "fazer", "prefira"]

        if not any(termo in caixa_baixa for termo in termos_imperativos):
            return "VALIDATION_ERROR_PROMPT"
        
        # Captura e formata a data e a hora do início
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y às %H:%M")

        # Cria a lista com os PDFs com base na escolha do Checkbox
        if buscar_subpastas:
            arquivos_pdf_com_caminho = []
            for raiz, diretorios, arquivos in os.walk(pasta_entrada):
                for arquivo in arquivos:
                    if arquivo.lower().endswith(".pdf"):
                        # Guarda o caminho completo relativo para sabermos onde o arquivo está
                        caminho_completo_arquivo = os.path.join(raiz, arquivo)
                        caminho_relativo = os.path.relpath(caminho_completo_arquivo, pasta_entrada)
                        arquivos_pdf_com_caminho.append(caminho_relativo)
            arquivos_pdf = arquivos_pdf_com_caminho
        else:
            arquivos_pdf = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(".pdf")]
        # Cria a lista com os PDFs
        total_arquivos = len(arquivos_pdf)

        if total_arquivos == 0:
            return "Nenhum arquivo PDF foi encontrado na pasta selecionada."
        
        # Inicializa a lista que armazenará o seu log original
        linhas_log = [f"Data de processamento: {data_formatada}\n"]

        with open(pasta_saida, "w", encoding="utf-8") as f_limpa:
            f_limpa.write(f"=== RELATÓRIO DE ANÁLISES - INICIADO EM {data_formatada} ===\n\n")

        # loop "Enumerate" corrigido
        for indice, nome_arquivo in enumerate(arquivos_pdf, start=1):
            try:
                # 1. CHECAGEM DE CANCELAMENTO ANTES DE PROCESSAR O PRÓXIMO ARQUIVO
                if checar_cancelamento():
                    linhas_log.append(f"     => PROCESSAMENTO INTERROMPIDO PELO USUÁRIO no arquivo {nome_arquivo}.")
                    salvar_log_final(pasta_saida, linhas_log)
                    return "CANCELADO"
                
                # Calcula a porcentagem e cria a sua mensagem original de progresso
                porcentagem = indice / total_arquivos
                mensagem_progresso = f"Processando ({indice}/{total_arquivos}): {nome_arquivo}..."

                # ATUALIZA A TELA GRAFICAMENTE
                callback_progresso(porcentagem, mensagem_progresso)
                linhas_log.append(mensagem_progresso)

                # Função de extração dados PDF
                caminho_completo = os.path.join(pasta_entrada, nome_arquivo)
                texto_pdf = extrair_texto_seguro(caminho_completo)

                if "Erro" not in texto_pdf:
                    # Resposta IA
                    response_IA = chamar_ia(conteudo_prompt, texto_pdf)

                    if response_IA:
                        with open(pasta_saida, "a", encoding="utf-8") as f_escrita:
                            f_escrita.write(f"--ANÁLISE DO ARQUIVO: {nome_arquivo}--\n\n")
                            f_escrita.write(response_IA)
                            f_escrita.write("\n\n" + "="*50 + "\n\n")
                    else:
                        linhas_log.append(f"     => O servidor de IA retornou uma resposta vazia para {nome_arquivo}.")

                else:
                    linhas_log.append(f"     => Falha no processo de extração ({nome_arquivo}): {texto_pdf}")
            
            except Exception as e:
                erro_msg = str(e).lower()

                # 1. VERIFICAÇÃO DE MODELO INDISPONÍVEL / INCOMPATÍVEL
                if "404" in erro_msg or "not available" in erro_msg or "not found" in erro_msg:
                    linhas_log.append(f"     => PROCESSAMENTO INTERROMPIDO: O modelo selecionado ({model_version}) não está mais disponível ou não foi encontrado.")
                    salvar_log_final(pasta_saida, linhas_log)
                    return f"O modelo '{model_version}' foi descontinuado ou não está disponível para esta chave. Escolha um modelo mais recente."
                
                # LISTA DE PALAVRAS-CHAVE DE ERROS FINANCEIROS, LIMITE OU COTA (Gemini e OpenAI)
                termos_bloqueio = ["quota", "insufficient", "exhausted", "credit", "rate_limit"]
                
                # 2. CAPTURA CIRÚRGICA: Se o erro for de saldo, cota ou limite de requisições, interrompe o loop na hora!
                if any(termo in erro_msg for termo in termos_bloqueio):
                    linhas_log.append(f"     => PROCESSAMENTO INTERROMPIDO: A conta atingiu o limite, restrição de cota ou falta de saldo para o processamento. Verifique com a sua provedora essa pendência.")
                    
                    # Salva o log parcial até o momento antes de abortar
                    salvar_log_final(pasta_saida, linhas_log)
                    return "A conta atingiu o limite, restrição de cota ou falta de saldo para o processamento. Verifique com a sua provedora essa pendência."
                
                # Se for outro tipo de erro comum (ex: PDF corrompido, falha de leitura), registra e continua os outros
                linhas_log.append(f"     => Erro inesperado no arquivo {nome_arquivo}: {str(e)}")
                continue

        salvar_log_final(pasta_saida, linhas_log)
        return "Sucesso"

    except Exception as e:
        return f"Erro crítico no processamento: {str(e)}"
    
# Função auxiliar isolada para gerar o arquivo de log e não duplicar código
def salvar_log_final(pasta_saida, linhas_log):
    destino_log = os.path.dirname(pasta_saida)
    caminho_log = os.path.join(destino_log, "log_processamento.txt")
    if "concluído" not in linhas_log[-1] and "INTERROMPIDO" not in linhas_log[-1]:
        linhas_log.append("Processamento finalizado.")
    with open(caminho_log, "w", encoding="utf-8") as f_log:
        f_log.write("\n".join(linhas_log) + "\n")    
