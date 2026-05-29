import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from processador_ia import (
    busca_instrucoes,
    diretorio_entrada,
    diretorio_saida,
    processar_arquivos
)

def open_interface():
    window = tk.Tk()
    window.title("Automação Processamento de PDFs com IA")
    window.geometry("680x600")
    window.configure(bg="#f5f5f5")

    # armazenam e mostram os caminhos na tela automaticamente
    url_prompt_var = tk.StringVar(value="Nenhum arquivo selecionado.")
    input_folder_var = tk.StringVar(value="Nenhuma pasta selecionada.")
    output_folder_var = tk.StringVar(value="Nenhum local definido.")

    def acionar_busca_prompt():
        caminho = busca_instrucoes()
        if caminho:
            url_prompt_var.set(caminho)
        
    def acionar_busca_entrada():
        caminho = diretorio_entrada()
        if caminho:
            input_folder_var.set(caminho)
    
    def acionar_busca_saida():
        caminho = diretorio_saida()
        if caminho:
            output_folder_var.set(caminho)
    
    # Atualização de interface processamento
    def atualizar_progresso(porcentagem, texto_status):
        # Altera os componentes na tela de forma segura enquanto a IA roda atrás
        window.after(0, lambda:progress_bar.set(porcentagem))
        window.after(0, lambda: label_porcentagem.configure(text=f"{int(porcentagem * 100)}%"))
        window.after(0, lambda: label_status.configure(text=texto_status))

    # Função início processamento
    def iniciar_execucao():
        provedor = combo_provider.get()
        chave = enter_key.get()
        modelo = enter_model.get()
        prompt = url_prompt_var.get()
        entrada = input_folder_var.get()
        saida = output_folder_var.get()

        # 2. Validações de preenchimento básico antes de chamar a IA
        if chave == "Digite a sua chave API do provedor:" or not chave.strip():
            messagebox.showwarning("Campos Vazios", "Por favor, digite uma Chave API válida.")
            return
        if modelo == "Digite o modelo de linguagem do seu provedor:" or not modelo.strip():
            messagebox.showwarning("Campos Vazios", "Por favor, digite o modelo de IA correspondente.")
            return
        if "Nenhum" in prompt or "Nenhuma" in entrada or "Nenhum" in saida:
            messagebox.showwarning("Arquivos Ausentes", "Certifique-se de selecionar todas as pastas e arquivos.")
            return
        
        # Exibe a barra de progresso e desativa o botão (evita cliques duplos)
        frame_progresso_container.pack(pady=(15, 5))
        progress_bar.pack(pady=(0, 20))
        btn_processar.configure(state="disabled", text="PROCESSANDO...")

        # THREADING: Cria um segundo plano para rodar o motor sem congelar a janela
        def rotina_segundo_plano():
            # Executa o loop de processamento de PDFs
            resultado = processar_arquivos(
                provider=provedor,
                key=chave,
                model_version=modelo,
                caminho_prompt=prompt,
                pasta_entrada=entrada,
                pasta_saida=saida,
                callback_progresso=atualizar_progresso
            )

            # Trata as respostas visuais baseadas no retorno do motor
            if resultado == "Sucesso":
                messagebox.showinfo("Sucesso!", "Todos os arquivos foram analisados!\nRelatório e Log gerados com sucesso.")
            elif resultado == "VALIDATION_ERROR_PROMPT":
                messagebox.showerror(
                    "Arquivo Inválido", 
                    "O arquivo selecionado não parece conter instruções válidas para a IA.\n"
                    "Certifique-se de usar termos de comando (ex: comece, gere, use)."
            )
            else:
                messagebox.showerror("Erro no Processamento", resultado)

            # Restaura os elementos visuais originais para o padrão
            btn_processar.configure(state="normal", text="INICIAR PROCESSAMENTO")
            progress_bar.set(0.0)
            label_porcentagem.configure(text="0%")
            frame_progresso_container.pack_forget()
            progress_bar.pack_forget()
    
        # Inicia a execução em paralelo
        thread_trabalho = threading.Thread(target=rotina_segundo_plano)
        thread_trabalho.start()
              

    # --- ELEMENTOS VISUAIS DA TELA ---
    label_titulo = tk.Label(
        window,
        text="Painel de Configurações",
        font=("Arial", 16, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )
    label_titulo.pack(pady=20)

    # Criando uma "Caixa de Agrupamento" para o formulário
    # Credenciais (Ajustado com CTK)
    frame_config = ctk.CTkFrame(window, fg_color="#ffffff", border_width=1, border_color="#cccccc", corner_radius=8)
    frame_config.pack(padx=30, pady=10, fill="x")

    # Funções manipular comportamento de campos
    def limpar_placeholder(event):
        field = event.widget
        placeholder = field.placeholder_text
        if field.get() == placeholder:
            field.delete(0, tk.END)
            field.config(fg="black")

    def restaurar_placeholder(event):
        field = event.widget
        placeholder = field.placeholder_text
        if field.get() == "":
            field.insert(0, placeholder)
            field.config(fg="gray")

    # Função que cria campos rapidamente
    def create_fields_with_placeholder(text_placeholder, linha):
        field = tk.Entry(frame_config, width=35, font=("Arial", 11), fg="gray")

        # Criar uma propriedade nova dentro do widget para guardar o texto do Entry
        field.placeholder_text = text_placeholder
        field.insert(0, text_placeholder)

        # Vincula os eventos de clique e perda de foco
        field.bind("<FocusIn>", limpar_placeholder)
        field.bind("<FocusOut>", restaurar_placeholder)

        field.grid(row=linha, column=1, pady=10, sticky="w")
        return field
    
     # Linha 0: Provedor IA
    label_provider = tk.Label(frame_config, text="Provedor IA:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444")
    label_provider.grid(row=0, column=0, padx=(0, 15), pady=10, sticky="e") # sticky="e" alinha o texto à direita (East)
    
    combo_provider = ttk.Combobox(frame_config, values=["Gemini", "OpenAI", "Claude"], state="readonly", width=38)
    combo_provider.current(0)
    combo_provider.grid(row=0, column=1, pady=10, sticky="w") # sticky="w" alinha o campo à esquerda (West)

    # Linha 1: Chave API
    label_API_KEY = tk.Label(frame_config, text="API Key:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444")
    label_API_KEY.grid(row=1, column=0, padx=(0, 15), pady=10, sticky="e")
    
    enter_key = create_fields_with_placeholder("Digite a sua chave API do provedor:", linha=1)

    # Linha 2: Modelo de Linguagem
    label_MODEL = tk.Label(frame_config, text="Modelo IA:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444")
    label_MODEL.grid(row=2, column=0, padx=(0, 15), pady=10, sticky="e")
    
    enter_model = create_fields_with_placeholder("Digite o modelo de linguagem:", linha=2)

    # Cria frame para trabalhar com arquivos e caminhos 
    frame_files = tk.Label(window, text="Seleção de Arquivos e Pastas ", font=("Arial", 10, "bold"), padx=20, bg="#ffffff", relief="solid", borderwidth=1)
    frame_files.pack(padx=30, pady=10, fill="x")

    # Linha Arquivo de Prompt
    tk.Label(frame_files, text="Instruções (Prompt):", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444").grid(row=0, column=0, padx=(0,15), pady=8, sticky="e")
    # Este Entry serve apenas para MOSTRAR o caminho (usamos textvariable)
    entry_prompt = tk.Entry(frame_files, textvariable=url_prompt_var, width=32, state="readonly", fg="black")
    entry_prompt.grid(row=0, column=1, pady=8, sticky="w") # command=busca_instrucoes

    # Botão que chama a função busca instruções
    btn_prompt = tk.Button(frame_files, text="Buscar...", font=("Arial", 9), width=8, command=acionar_busca_prompt)
    btn_prompt.grid(row=0, column=2, padx=(0, 0), pady=8)

    # Linha 1: Pasta de Entrada (PDFs)
    tk.Label(frame_files, text="Pasta dos PDFs:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444").grid(row=1, column=0, padx=(0, 15), pady=8, sticky="e")
    entry_entrada = tk.Entry(frame_files, textvariable=input_folder_var, width=32, state="readonly")
    entry_entrada.grid(row=1, column=1, pady=8, sticky="w")
    btn_entrada = tk.Button(frame_files, text="Buscar...", font=("Arial", 9), width=8, command=acionar_busca_entrada)
    btn_entrada.grid(row=1, column=2, padx=(0, 0), pady=8)

    # Linha 2: Local de Saída (Relatório)
    tk.Label(frame_files, text="Salvar Relatório:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#444444").grid(row=2, column=0, padx=(0, 15), pady=8, sticky="e")
    entry_saida = tk.Entry(frame_files, textvariable=output_folder_var, width=32, state="readonly")
    entry_saida.grid(row=2, column=1, pady=8, sticky="w")
    btn_saida = tk.Button(frame_files, text="Definir...", font=("Arial", 9), width=8, command=acionar_busca_saida)
    btn_saida.grid(row=2, column=2, padx=(0, 0), pady=8)


    # --- BOTÃO PRINCIPAL DE EXECUÇÃO ---
    # Fica bem destacado no final da janela
    btn_processar = ctk.CTkButton(
        window, 
        text="INICIAR PROCESSAMENTO", 
        font=("Arial", 11, "bold"), 
        fg_color="#2ecc71",
        hover_color="#6699CC",
        text_color="white",
        border_width=2,
        corner_radius=10,
        height=45,
        width=250,
        cursor="hand2",
        command=iniciar_execucao
        
    )
    btn_processar.pack(pady=15)

    # Elementos Invisíveis de Progresso (vão brotar na tela ao clicar)
    frame_progresso_container = ctk.CTkFrame(window, fg_color="transparent")
    label_status = ctk.CTkLabel(frame_progresso_container, text="Processando arquivos...", font=("Arial", 11, "italic"), text_color="#7f8c8d")
    label_status.pack(side="left", padx=(0, 10))
    label_porcentagem = ctk.CTkLabel(frame_progresso_container, text="0%", font=("Arial", 11, "bold"), text_color="#2ecc71")
    label_porcentagem.pack(side="right", padx=(10, 0))

    progress_bar = ctk.CTkProgressBar(window, width=450, height=12, corner_radius=6, fg_color="#e0e0e0", progress_color="#2ecc71")
    progress_bar.set(0.0)

    # Mantém a janela viva
    window.mainloop()

if __name__ == "__main__":
    open_interface()