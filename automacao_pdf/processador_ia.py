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

        # Verifica se o usuário fechou ou cancelou a janela
        if not caminho_entrada:
            messagebox.showwarning("Aviso", "Operação cancelada pelo usuário.")
            return None
        
        # Verifica se realmente a pasta existe e está acessível
        if not os.path.exists(caminho_entrada):
            messagebox.showwarning("Erro", "O caminho selecionado não existe.")
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
        # Verifica se o usuário fechou a janela ou cancelou a operação
        if not caminho_salvamento:
            messagebox.showwarning(
                "Aviso",
                "O arquivo não foi salvo porque a operação foi cancelada."
            )
            return None

        return caminho_salvamento
        
    except Exception as e:
        messagebox.showerror(
            "Aviso",
            f"Erro inesperado ao tentar escolher o local de salvamento do arquivo:\n{str(e)}"
        )
         
        return None
    
# Realizar o processamento dos arquivos PDFs mediante às instruções do PROMPT
def processar_arquivos(provider, key, model_version, caminho_prompt, pasta_entrada, pasta_saida, callback_progresso):
    try:
        # Configuração da IA usando os dados coletados da tela na hora do clique
        chamar_ia = seletor_ia(provider=provider, key=key, model=model_version)
        if not chamar_ia:
            return "Falha ao inicializar o servidor IA. Verifique sua chave API."
        
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

        # Cria a lista com os PDFs
        arquivos_pdf = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(".pdf")]
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
            
            except Exception as e_interno:
                # Se um arquivo falhar, registra no log e continua o loop para os outros arquivos
                linhas_log.append(f"     => Erro inesperado no arquivo {nome_arquivo}: {str(e_interno)}")
                continue

        # --- FIM DO LOOP FOR (A identação foi movida para fora do loop) ---
        # Salvamento do arquivo Log ocorre apenas quando TODOS os arquivos terminam
        destino_log = os.path.dirname(pasta_saida)
        caminho_log = os.path.join(destino_log, "log_processamento.txt")
        linhas_log.append("Processamento concluído!")

        with open(caminho_log, "w", encoding="utf-8") as f_log:
            f_log.write("\n".join(linhas_log) + "\n")
        
        return "Sucesso"

    except Exception as e:
        return f"Erro crítico no processamento: {str(e)}"