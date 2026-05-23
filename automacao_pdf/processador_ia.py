import os
import argparse
from extrator import extrair_texto_seguro # Reutilizar o extrator
from tkinter import filedialog, messagebox # Recurso do Tkinter para selecionar diretórios
from entrada_dados import inserir_dados
from gerenciador_ia import seletor_ia
from configurador import carregar_chave, armazenar_chave
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
        if not caminho_prompt:
            return None

        return caminho_prompt
        
    except Exception as e:
        messagebox.showwarning(
            "Aviso",
            f"Erro inesperado ao selecionar o arquivo de instruções:\n{str(e)}"
        )
         
        return None

# Uso da biblioteca argparse para entrada de dados
parse = argparse.ArgumentParser(
    description="Preencha os campos a seguir para continuar com o processamento dos PDFs.")

# Criação de argumentos para entrada de dados
parse.add_argument("--provider", type=str, help='Escolha qual tipo de IA para realizar o processamento PROMPT:')
parse.add_argument("--key", type=str, help='Insira a chave API correspondente ao servidor IA da sua conta.')
parse.add_argument("--model", type=str, help='Insira a versão da sua IA para processar os arquivos.')
args = parse.parse_args()
entrada_usuario = inserir_dados(args.provider,args.key, args.model) # Função que retorna uma lista de Strings contendo a chave e a versão da IA 

# Validação entrada de dados
if not entrada_usuario:
    exit()

# Verifica se o usuário digitou a chave no termninal para salvá-la no arquivo JSON
if entrada_usuario[0] is not None:
    armazenar_chave(provedor=args.provider, chave=entrada_usuario[0])

# Confiugração IA
chamar_ia = seletor_ia(provider=args.provider, key=entrada_usuario[0], model=entrada_usuario[1])

if not chamar_ia:
    exit()

# Selecionar diretório para escolher a pasta com PDFs a serem processados
def diretorio_entrada():
    try:
        caminho_entrada = filedialog.askdirectory(
            title="Selecione uma pasta com PDFs:",
            mustexist=True
        )

        # Verifica se o usuário fechou ou cancelou a janela
        if not caminho_entrada:
            messagebox.showwarning("Operação cancelada pelo usuário.")
            return None
        
        # Verifica se realmente a pasta existe e está acessível
        if not os.path.exists(caminho_entrada):
            messagebox.showwarning("Erro", "O caminho selecionado não existe.")
            return None
        
        # Verifica se o usuário tem permissão de leitura na pasta
        if not os.access(caminho_entrada, os.R_OK):
            messagebox.showwarning(
                "Você não tem permissão de acesso a essa pasta."
            )
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
        caminho_salvamento = filedialog.asksaveasfilename( # Essa função vai garantir que o tkinter devolva apenas o texto do caminho e não haja conflito com a WITH OPEN
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
def processar_arquivos():

    # Busca o caminho do arquivo prompt
    caminho_prompt = busca_instrucoes()

    if not caminho_prompt:
        return

    # Carregamento do Prompt
    with open(caminho_prompt, "r", encoding="utf-8") as file:
        conteudo_prompt = file.read()

    # Conversão do conteúdo com letras minusculas para nao haver diferenciação entre maiusculo e minusculo
    caixa_baixa = conteudo_prompt.lower()

    # Lista com termos imperativos
    termos_imperativos = ["comece", "gere", "use", "fazer", "prefira"]

    # validação de palavras-chave para continuidade no anexo do prompt
    if not any(termo in caixa_baixa for termo in termos_imperativos):
        messagebox.showerror(
            "Arquivo Inválido",
            "O arquivo selecionado não parece conter instruções válidas para a IA.\n\n"
            "Certifique-se de que o documento inclua termos de comando (ex: analisar, extrair, resumo)."
        )
        return

    pasta_entrada = diretorio_entrada()
    if not pasta_entrada:
        return

    pasta_saida = diretorio_saida()
    if not pasta_saida:
        return

    instrucoes = conteudo_prompt

    # Captura e formata a data e a hora do início do processamento
    agora = datetime.now()
    data_formatada = agora.strftime("%d/%m/%Y às %H:%M")

    # Cria uma lista com os PDFs existentes em uma pasta selecionada para o processamento
    arquivos_pdf = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(".pdf")]
    total_arquivos = len(arquivos_pdf)

    # Inicializa a lista que armazenará o log
    linhas_log = []
    linhas_log.append(f"Data de processamento: {data_formatada}\n") # Primeira linha do relatório

    if total_arquivos == 0:
        messagebox.showwarning(
            "Aviso",
            "Nenhum arquivo PDF foi encontrado na pasta selecionada."
            )
        return
    
    with open(pasta_saida, "w", encoding="utf-8") as f_limpa:
        f_limpa.write(f"=== RELATÓRIO DE ANÁLISES - INICIADO EM {data_formatada} ===\n\n")

    # Enumerate fornece o índice e o nome do arquivo ao mesmo tempo
    for indice, nome_arquivo in enumerate(arquivos_pdf, start=1):

        # Cria a mensagem de progresso
        mensagem_progresso = f"Processando ({indice}/{total_arquivos}): {nome_arquivo}..."
        print(mensagem_progresso) # Mostra mensagem no terminal
        linhas_log.append(mensagem_progresso)

        # Função extração de texto no arquivo extrator.py
        caminho_completo = os.path.join(pasta_entrada, nome_arquivo)
        texto_pdf = extrair_texto_seguro(caminho_completo)

        if "Erro" not in texto_pdf:
            try:
                # Chama IA para o processamento
                response_IA = chamar_ia(instrucoes, texto_pdf)

                if response_IA:

                    # Abrimos o arquivo no modo "a" (append) para adicionar o texto sem apagar o que já existe
                    with open(pasta_saida, "a", encoding="utf-8") as f_escrita:
                        f_escrita.write(f"--ANÁLISE DO ARQUIVO: {nome_arquivo}--\n\n")
                        f_escrita.write(response_IA)
                        f_escrita.write("\n\n" + "="*50 + "\n\n")

                else:
                    msg_erro_ia = f"     => O servidor de IA retornou uma resposta vazia."
                    print(msg_erro_ia)
                    linhas_log.append(msg_erro_ia)

            except Exception as e_ia:
                msg_falha_ia = f"    => Erro de comunicação com a IA: {str(e_ia)}"
                print(msg_falha_ia)
                linhas_log.append(msg_falha_ia)

        # Caso ocorra um erro no extrator do PDF     
        else:
            # Mensagem de erro do extrator é enviada para o log
            msg_erro_pdf = f"     => Falha no processo de extração das informações: {texto_pdf}"
            print(msg_erro_pdf)
            linhas_log.append(msg_erro_pdf)

    # Definir local de destino para salvar o relatório
    destino_log = os.path.dirname(pasta_saida)
    caminho_log = os.path.join(destino_log, "log_processamento.txt")

    # Linha final de conclusão do relatório
    linhas_log.append(f"Processamento concluído!.")

    # Grava o registro do relatório no arquivo Txt
    with open(caminho_log, "w", encoding="utf-8") as f_log:
        # Texto corrido com quebras de linha
        f_log.write("\n".join(linhas_log) + "\n")

    print(f"O registro de log foi salvo em em {caminho_log}")

if __name__ == "__main__":
    processar_arquivos()