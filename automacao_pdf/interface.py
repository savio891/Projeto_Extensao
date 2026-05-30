import threading
import customtkinter as ctk
from tkinter import ttk, messagebox
from configurador import obter_chaves_salvas, armazenar_chave, carregar_chave



# --- IMPORTAÇÃO DO SEU MOTOR REAL ---
from processador_ia import (
    busca_instrucoes, 
    diretorio_entrada, 
    diretorio_saida, 
    processar_arquivos
)

# Simulando o seu configurador. amanhã você pode trocar pelas suas funções reais
# que lêem o arquivo .env ou .json

def open_interface():
    window = ctk.CTk()
    window.title("Automação Processamento de PDFs com IA")
    window.geometry("700x680")
    window.configure(fg_color="#f5f5f5")
    ctk.set_appearance_mode("Light") 

    # --- DICIONÁRIO DE MODELOS PADRÃO ---
    MODELOS_POR_PROVEDOR = {
        "Gemini": ["gemini-3.1-flash-lite", "gemini-3-flash-preview", "gemini-3.5-flash"],
        "OpenAI": ["gpt-5.4-mini", "gpt-5.4", "gpt-5.5"],
        "Claude": ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]
    }

    # --- VARIÁVEIS DE CONTROLE ---
    caminho_prompt_var = ctk.StringVar(value="Nenhum arquivo selecionado")
    pasta_entrada_var = ctk.StringVar(value="Nenhuma pasta selecionada")
    pasta_saida_var = ctk.StringVar(value="Nenhum local definido")

    # --- FUNÇÕES DE ATUALIZAÇÃO DINÂMICA (EVENTOS) ---
    def atualizar_campos_por_provedor(event=None):
        provedor_selecionado = combo_provider.get()
        
        # 1. Atualiza os modelos recomendados no Combobox de Modelos
        modelos_disponiveis = MODELOS_POR_PROVEDOR.get(provedor_selecionado, [])
        combo_model.configure(values=modelos_disponiveis)
        if modelos_disponiveis:
            combo_model.set(modelos_disponiveis[0]) # Seleciona o primeiro por padrão
            
        # 2. Busca as chaves já salvas para esse provedor e atualiza o Combobox de Chaves
        chaves_salvas = obter_chaves_salvas(provedor_selecionado)
        combo_key.configure(values=chaves_salvas)
        if chaves_salvas:
            combo_key.set(chaves_salvas[0]) # Preenche automaticamente com a última chave
        else:
            combo_key.set("") # Fica vazio se não tiver chave salva

    # --- FUNÇÕES DOS BOTÕES DE BUSCA ---
    def acionar_busca_prompt():
        caminho = busca_instrucoes()
        if caminho: caminho_prompt_var.set(caminho)

    def acionar_busca_entrada():
        caminho = diretorio_entrada()
        if caminho: pasta_entrada_var.set(caminho)

    def acionar_busca_saida():
        caminho = diretorio_saida()
        if caminho: pasta_saida_var.set(caminho)

    # --- FUNÇÃO DO NOVO BOTÃO LIMPAR ---
    def limpar_todos_os_campos():
        if messagebox.askyesno("Limpar Campos", "Deseja realmente limpar todos os caminhos e chaves da tela?"):
            combo_key.set("")
            caminho_prompt_var.set("Nenhum arquivo selecionado")
            pasta_entrada_var.set("Nenhuma pasta selecionada")
            pasta_saida_var.set("Nenhum local definido")
            label_status.configure(text="Status: Pronto para iniciar")
            progress_bar.set(0.0)
            label_porcentagem.configure(text="0%")

    def atualizar_progresso_gui(porcentagem, texto_status):
        window.after(0, lambda: progress_bar.set(porcentagem))
        window.after(0, lambda: label_porcentagem.configure(text=f"{int(porcentagem * 100)}%"))
        window.after(0, lambda: label_status.configure(text=texto_status))

    # --- GATILHO DE EXECUÇÃO ---
    def iniciar_execucao():
        provedor = str(combo_provider.get()).strip()
        chave = str(combo_key.get()).strip()
        modelo = str(combo_model.get()).strip()
        prompt = caminho_prompt_var.get()
        entrada = pasta_entrada_var.get()
        saida = pasta_saida_var.get()

        if not chave.strip():
            messagebox.showwarning("Campos Vazios", "Por favor, selecione ou digite uma Chave API.")
            return
        
        armazenar_chave(provedor, chave)

        if not modelo.strip():
            messagebox.showwarning("Campos Vazios", "Por favor, selecione ou digite o modelo de IA.")
            return
        if "Nenhum" in prompt or "Nenhuma" in entrada or "Nenhum" in saida:
            messagebox.showwarning("Arquivos Ausentes", "Selecione todos os caminhos antes de iniciar.")
            return

        frame_progresso_container.pack(pady=(15, 5))
        progress_bar.pack(pady=(0, 20))
        btn_processar.configure(state="disabled", text="PROCESSANDO...")
        btn_limpar.configure(state="disabled")

        def rotina_segundo_plano():
            resultado = processar_arquivos(
                provider=provedor, key=chave, model_version=modelo,
                caminho_prompt=prompt, pasta_entrada=entrada, pasta_saida=saida,
                callback_progresso=atualizar_progresso_gui
            )

            if resultado == "Sucesso":
                messagebox.showinfo("Sucesso!", "Todos os arquivos foram analisados com sucesso!")
            elif resultado == "VALIDATION_ERROR_PROMPT":
                messagebox.showerror("Arquivo Inválido", "O prompt não possui termos imperativos válidos.")
            else:
                messagebox.showerror("Erro", resultado)

            btn_processar.configure(state="normal", text="INICIAR PROCESSAMENTO")
            btn_limpar.configure(state="normal")
            frame_progresso_container.pack_forget()
            progress_bar.pack_forget()

        threading.Thread(target=rotina_segundo_plano).start()

    # --- DESIGN DA INTERFACE ---
    ctk.CTkLabel(window, text="Painel de Configurações", font=("Arial", 18, "bold"), text_color="#333333").pack(pady=(15, 5))

    # Bloco 1: Credenciais Dinâmicas
    frame_config = ctk.CTkFrame(window, fg_color="#ffffff", border_width=1, border_color="#cccccc", corner_radius=8)
    frame_config.pack(padx=30, pady=10, fill="x")

    ctk.CTkLabel(frame_config, text="Provedor IA:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=0, column=0, padx=(20, 15), pady=12, sticky="e")
    combo_provider = ctk.CTkComboBox(frame_config, values=["Gemini", "OpenAI", "Claude"], state="readonly", width=310, command=atualizar_campos_por_provedor)
    combo_provider.set("Gemini")
    combo_provider.grid(row=0, column=1, columnspan=2, pady=12, sticky="w")

    ctk.CTkLabel(frame_config, text="API Key:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=1, column=0, padx=(20, 15), pady=12, sticky="e")
    # Trocado para ctk.CTkComboBox que aceita digitação livre (state="normal")
    combo_key = ctk.CTkComboBox(frame_config, width=310, state="normal")
    combo_key.grid(row=1, column=1, columnspan=2, pady=12, sticky="w")

    ctk.CTkLabel(frame_config, text="Modelo IA:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=2, column=0, padx=(20, 15), pady=12, sticky="e")
    # Trocado para ctk.CTkComboBox que aceita digitação livre (state="normal")
    combo_model = ctk.CTkComboBox(frame_config, width=310, state="normal")
    combo_model.grid(row=2, column=1, columnspan=2, pady=12, sticky="w")

    # Bloco 2: Caminhos e Arquivos
    frame_arquivos = ctk.CTkFrame(window, fg_color="#ffffff", border_width=1, border_color="#cccccc", corner_radius=8)
    frame_arquivos.pack(padx=30, pady=10, fill="x")

    # Prompt
    ctk.CTkLabel(frame_arquivos, text="Instruções (Prompt):", font=("Arial", 11, "bold"), text_color="#444444").grid(row=0, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=caminho_prompt_var, width=260, state="readonly").grid(row=0, column=1, pady=10, sticky="w")
    ctk.CTkButton(frame_arquivos, text="Buscar...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_prompt).grid(row=0, column=2, padx=(15, 20), pady=10, sticky="w")

    # Entrada
    ctk.CTkLabel(frame_arquivos, text="Pasta dos PDFs:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=1, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=pasta_entrada_var, width=260, state="readonly").grid(row=1, column=1, pady=10, sticky="w")
    ctk.CTkButton(frame_arquivos, text="Buscar...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_entrada).grid(row=1, column=2, padx=(15, 20), pady=10, sticky="w")

    # Saída
    ctk.CTkLabel(frame_arquivos, text="Salvar Relatório:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=2, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=pasta_saida_var, width=260, state="readonly").grid(row=2, column=1, pady=10, sticky="w")
    ctk.CTkButton(frame_arquivos, text="Definir...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_saida).grid(row=2, column=2, padx=(15, 20), pady=10, sticky="w")

    # --- CONTÊINER DOS BOTÕES DO RODAPÉ (Alinhamento Lado a Lado) ---
    frame_botoes_acao = ctk.CTkFrame(window, fg_color="transparent")
    frame_botoes_acao.pack(pady=20)

    btn_processar = ctk.CTkButton(
        frame_botoes_acao, text="INICIAR PROCESSAMENTO", font=("Arial", 12, "bold"),
        fg_color="#2ecc71", hover_color="#27ae60", text_color="white",
        border_width=2, border_color="#1e7e34", corner_radius=10, height=45, width=240,
        cursor="hand2", command=iniciar_execucao
    )
    btn_processar.pack(side="left", padx=10)

    btn_limpar = ctk.CTkButton(
        frame_botoes_acao, text="LIMPAR CAMPOS", font=("Arial", 12, "bold"),
        fg_color="#e74c3c", hover_color="#c0392b", text_color="white", # Vermelho corporativo elegante
        border_width=2, border_color="#962d22", corner_radius=10, height=45, width=160,
        cursor="hand2", command=limpar_todos_os_campos
    )
    btn_limpar.pack(side="left", padx=10)

    # Elementos de Progresso
    frame_progresso_container = ctk.CTkFrame(window, fg_color="transparent")
    label_status = ctk.CTkLabel(frame_progresso_container, text="Processando arquivos...", font=("Arial", 11, "italic"), text_color="#7f8c8d")
    label_status.pack(side="left", padx=(0, 10))
    label_porcentagem = ctk.CTkLabel(frame_progresso_container, text="0%", font=("Arial", 11, "bold"), text_color="#2ecc71")
    label_porcentagem.pack(side="right", padx=(10, 0))

    progress_bar = ctk.CTkProgressBar(window, width=450, height=12, corner_radius=6, fg_color="#e0e0e0", progress_color="#2ecc71")
    progress_bar.set(0.0)

    # Executa a primeira carga para o Gemini (padrão) abrir populado
    atualizar_campos_por_provedor()

    window.mainloop()

if __name__ == "__main__":
    open_interface()