import threading
import customtkinter as ctk
from tkinter import ttk, messagebox
from configurador import obter_chaves_salvas, armazenar_chave, carregar_chave, remover_chave_salva
from gerenciador_ia import seletor_ia, listar_modelos_disponiveis
import time

# Tenta importar o módulo de splash do PyInstaller (só funciona dentro do .exe)
try:
    import pyi_splash
except ImportError:
    pyi_splash = None

def carregar_sistema_com_porcentagem():
    """Simula e atualiza a porcentagem na tela de abertura"""
    if pyi_splash:
        etapas = [
            ("Iniciando o sistema...", 10),
            ("Carregando layout e temas...", 30),
            ("Lendo chaves do arquivo .env...", 50),
            ("Conectando aos módulos OpenAI/Gemini/Claude...", 75),
            ("Pronto!", 100)
        ]
        
        for mensagem, porcentagem in etapas:
            # Atualiza o texto que aparece embaixo da imagem
            pyi_splash.update_text(f"{mensagem} ({porcentagem}%)")
            time.sleep(0.4) # Um pequeno intervalo para o usuário conseguir ler
            
        # Fecha a tela de splash após atingir 100%
        pyi_splash.close()

# --- Chame a função antes de abrir a interface ---
carregar_sistema_com_porcentagem()

# --- IMPORTAÇÃO DO SEU MOTOR REAL ---
from processador_ia import (
    busca_instrucoes, 
    diretorio_entrada, 
    diretorio_saida, 
    processar_arquivos
)

def open_interface():
    window = ctk.CTk()
    window.title("Automação Processamento de PDFs com IA")
    window.geometry("700x600")
    window.configure(fg_color="#f5f5f5")
    ctk.set_appearance_mode("Light")

    # --- CONFIGURAÇÃO DO ÍCONE DA JANELA ---
    try:
        # Para o topo da janela e barra de tarefas do Windows
        window.iconbitmap("image.ico")
    except Exception as e:
        print(f"Não foi possível carregar o ícone (.ico): {e}")

    # --- VARIÁVEIS DE CONTROLE ---
    caminho_prompt_var = ctk.StringVar(value="Nenhum arquivo selecionado")
    pasta_entrada_var = ctk.StringVar(value="Nenhuma pasta selecionada")
    pasta_saida_var = ctk.StringVar(value="Nenhum local definido")

    # --- FUNÇÃO DO POP-UP GERENCIADOR DE CHAVES ---
    def abrir_gerenciador_chaves():
        provedor_atual = combo_provider.get()
        if provedor_atual == "Nenhum":
            messagebox.showwarning("Provedor Ausente", "Selecione um Provedor IA na tela principal para gerenciar suas chaves.")
            return

        # Cria a janela pop-up (Toplevel)
        popup = ctk.CTkToplevel(window)
        popup.title(f"Gerenciar Chaves - {provedor_atual}")
        popup.geometry("450x300")
        popup.configure(fg_color="#f5f5f5")
        popup.grab_set() # Bloqueia a janela de trás até fechar o pop-up
        popup.resizable(False, False) # impede o redimensionamento da janela pelo usuário

        ctk.CTkLabel(popup, text=f"Chaves Salvas para {provedor_atual}", font=("Arial", 14, "bold"), text_color="#333333").pack(pady=(15, 10))

        # Lista as chaves atuais gravadas no .env para o provedor
        chaves = obter_chaves_salvas(provedor_atual)

        # Container para a lista de chaves (com scrollbar se houver muitas)
        frame_lista = ctk.CTkScrollableFrame(popup, width=400, height=160, fg_color="#ffffff", border_width=1, border_color="#cccccc")
        frame_lista.pack(padx=20, pady=5)

        def atualizar_lista_popup():
            # Limpa o frame para reconstruir
            for widget in frame_lista.winfo_children():
                widget.destroy()

            chaves_atualizadas = obter_chaves_salvas(provedor_atual)
            if not chaves_atualizadas:
                ctk.CTkLabel(frame_lista, text="Nenhuma chave salva para este provedor.", font=("Arial", 11, "italic"), text_color="#7f8c8d").pack(pady=40)
                return
            
            for i, chv in enumerate(chaves_atualizadas):
                frame_linha = ctk.CTkFrame(frame_lista, fg_color="transparent")
                frame_linha.pack(fill="x", pady=4, padx=5)
            
            # Exibe a chave mascarada ou cortada para proteção visual se for muito longa
            texto_chave = chv if len(chv) <= 25 else f"{chv[:10]}...{chv[-10:]}"

            lbl_chv = ctk.CTkLabel(frame_linha, text=texto_chave, font=("Arial", 11), anchor="w")
            lbl_chv.pack(side="left", fill="x", expand=True)

            # Botão para Selecionar a Chave
            btn_sel = ctk.CTkButton(
                    frame_linha, text="Selecionar", font=("Arial", 10, "bold"),
                    fg_color="#2ecc71", hover_color="#27ae60", width=75, height=22,
                    command=lambda c=chv: acionar_selecao_chave(c)
                )
            btn_sel.pack(side="right", padx=2)

            # Botão para Deletar a Chave
            btn_del = ctk.CTkButton(
                    frame_linha, text="Excluir", font=("Arial", 10, "bold"),
                    fg_color="#e74c3c", hover_color="#c0392b", width=60, height=22,
                    command=lambda c=chv: acionar_exclusao_chave(c)
                )
            btn_del.pack(side="right", padx=5)
        
        # Função que define a chave na tela principal e fecha o popup
        def acionar_selecao_chave(chave_selecionada):
            combo_key.set(chave_selecionada) # Injeta a chave no campo principal
            popup.destroy()                  # Fecha a janela popup automaticamente
            
        def acionar_exclusao_chave(chave_alvo):
            if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja apagar esta chave?"):
                remover_chave_salva(provedor_atual, chave_alvo)
                atualizar_lista_popup()
                atualizar_campos_por_provedor()

        # Carrega a lista pela primeira vez no pop-up
        atualizar_lista_popup()

        # Botão Fechar no rodapé do pop-up
        ctk.CTkButton(popup, text="Fechar", font=("Arial", 11, "bold"), width=100, command=popup.destroy).pack(pady=(15, 10))

    # --- FUNÇÕES DE ATUALIZAÇÃO DINÂMICA (EVENTOS) ---
    def atualizar_campos_por_provedor(event=None):
        provedor_selecionado = combo_provider.get()
        
        # 1. VALIDAÇÃO SE FOR "NENHUM": Limpa e desativa os campos de credenciais
        if provedor_selecionado == "Nenhum":
            combo_key.configure(values=[], state="disabled")
            combo_key.set("")
            combo_model.configure(values=["Selecione um Provedor IA..."], state="disabled")
            combo_model.set("Selecione um Provedor IA...")
            return  # Interrompe a função aqui de forma segura
        
        combo_key.configure(state="normal")

        # 2. Busca a chave já salva no .env para esse provedor específico
        chaves_salvas = obter_chaves_salvas(provedor_selecionado)

        if chaves_salvas:
            combo_key.configure(values=chaves_salvas)
            combo_key.set(chaves_salvas[0])
            chave_atual = chaves_salvas[0]
        else:
            combo_key.configure(values=[])
            combo_key.set("")
            chave_atual = ""

        # 3. Se não houver chave salva, avisa o usuário que ele precisa inserir uma para liberar os modelos
        if not chave_atual.strip():
            combo_model.configure(values=[])
            combo_model.set("Insira uma API key válida...")
            return

        # 4. Se houver chave, reseta o Combobox de Modelos para o estado de espera
        combo_model.configure(values=["Carregando modelos da sua chave..."], state="disabled")
        combo_model.set("Carregando modelos da sua chave...")

        # 5. Dispara uma Thread separada para buscar os modelos na API vinculados a essa Chave específica
        def buscar_modelos_thread(prov, key):
            model_selecionado = combo_model.get()
            modelos_reais = listar_modelos_disponiveis(prov, key, model_selecionado)

            # Se o primeiro item começar com "ERRO:", exibe o aviso específico da API
            if modelos_reais and str(modelos_reais[0]).startswith("ERRO:"):
                mensagem_erro = modelos_reais[0]
                window.after(0, lambda: combo_model.configure(values=[mensagem_erro]))
                window.after(0, lambda: combo_model.set(mensagem_erro))
                window.after(0, lambda: combo_model.configure(state="disabled"))
            else:
                # SE FOR O CLAUDE: Não há sugestões, configuramos o modo manual com placeholder
                if prov.lower() == "claude":
                    placeholder_texto = "Digite o modelo manualmente..."
                    window.after(0, lambda: combo_model.configure(values=[], state="normal"))
                    window.after(0, lambda: combo_model.set(placeholder_texto))
                    
                else:
                    # PARA GEMINI E OPENAI:
                    # Forçamos o estado para 'readonly' ANTES de injetar a nova lista.
                    # Isso remove permanentemente a caixa de edição de texto do Claude.
                    if modelos_reais:
                        window.after(0, lambda: combo_model.configure(state="readonly", values=modelos_reais))
                        window.after(0, lambda: combo_model.set(modelos_reais[0]))
                    else:
                        window.after(0, lambda: combo_model.configure(values=["Nenhum modelo encontrado"], state="disabled"))
                        window.after(0, lambda: combo_model.set("Nenhum modelo encontrado"))
        
        threading.Thread(target=buscar_modelos_thread, args=(provedor_selecionado, chave_atual), daemon=True).start()

    # Variável de controle de cancelamento (Booleana pura)
    cancelado_pelo_usuario = False
    
    # Função auxiliar que o processador vai chamar para saber se o usuário cancelou
    def verificar_se_cancelou():
        nonlocal cancelado_pelo_usuario
        return cancelado_pelo_usuario

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

    # --- FUNÇÃO DO BOTÃO LIMPAR CONFIGURADA PARA VOLTAR AO "NENHUM" ---
    def limpar_todos_os_campos():
        if messagebox.askyesno("Limpar Campos", "Deseja realmente limpar todos os caminhos e chaves da tela?"):
            combo_provider.set("Nenhum")
            atualizar_campos_por_provedor() # Força o reset visual dos campos de chave/modelo
            caminho_prompt_var.set("Nenhum arquivo selecionado")
            pasta_entrada_var.set("Nenhuma pasta selecionada")
            pasta_saida_var.set("Nenhum local definido")
            label_status.configure(text="Status: Pronto para iniciar")
            progress_bar.set(0.0)
            label_porcentagem.configure(text="0%")
            chk_subpastas_var.set(False)

    def atualizar_progresso_gui(porcentagem, texto_status):
        window.after(0, lambda: progress_bar.set(porcentagem))
        window.after(0, lambda: label_porcentagem.configure(text=f"{int(porcentagem * 100)}%"))
        window.after(0, lambda: label_status.configure(text=texto_status))

    # --- GATILHO DE EXECUÇÃO ---
    def iniciar_execucao():
        nonlocal cancelado_pelo_usuario
        cancelado_pelo_usuario = False # Reseta o estado ao iniciar

        # Coleta dados interface
        provedor = str(combo_provider.get()).strip()
        chave = str(combo_key.get()).strip()
        modelo = str(combo_model.get()).strip()
        prompt = caminho_prompt_var.get()
        entrada = pasta_entrada_var.get()
        saida = pasta_saida_var.get()
        subpastas_ativo = chk_subpastas_var.get()

        # Bloqueia a execução se houver mensagens de erro registradas no campo do modelo
        if "ERRO:" in modelo or "saldo" in modelo.lower() or "cota" in modelo.lower():
            messagebox.showerror("Erro de Créditos/Cota", "Não é possível iniciar. Verifique o saldo e faturamento da sua conta de IA.")
            return

        # Evita prosseguir caso esteja marcado como "Nenhum"
        if provedor == "Nenhum":
            messagebox.showwarning("Provedor Ausente", "Por favor, selecione um Provedor de IA válido para processar.")
            return

        if not chave.strip() or chave == "Insira uma API key válida...":
            messagebox.showwarning("Campos Vazios", "Por favor, selecione ou digite uma Chave API válida.")
            return
        
        armazenar_chave(provedor, chave)

        if not modelo.strip() or "válida" in modelo or "Carregando" in modelo or "Selecione" in modelo or "Inválida" in modelo:
            messagebox.showwarning("Modelo Inválido", "Por favor, selecione um modelo de IA válido carregado da sua conta.")
            return
            
        if "Nenhum" in prompt or "Nenhuma" in entrada or "Nenhum" in saida:
            messagebox.showwarning("Arquivos Ausentes", "Selecione todos os caminhos antes de iniciar.")
            return
        
        # 1. BLOQUEIO TOTAL DE CAMPOS E BOTÕES (EXCETO CANCELAR)
        combo_provider.configure(state="disabled")
        combo_key.configure(state="disabled")
        combo_model.configure(state="disabled")
        btn_config_chaves.configure(state="disabled")
        
        btn_buscar_prompt.configure(state="disabled")
        btn_buscar_entrada.configure(state="disabled")
        btn_definir_saida.configure(state="disabled")
        chk_subpastas.configure(state="disabled")
        
        btn_processar.configure(state="disabled", text="PROCESSANDO...")
        btn_limpar.configure(state="disabled")
        
        # Ativa unicamente o botão de Cancelar
        btn_cancelar.configure(state="normal", text="Cancelar")

        frame_progresso_container.pack(pady=(15, 5))
        progress_bar.pack(pady=(0, 20))
        btn_processar.configure(state="disabled", text="PROCESSANDO...")
        btn_limpar.configure(state="disabled")

        def rotina_segundo_plano():
            resultado = processar_arquivos(
                provider=provedor, key=chave, model_version=modelo,
                caminho_prompt=prompt, pasta_entrada=entrada, pasta_saida=saida,
                buscar_subpastas=subpastas_ativo,
                callback_progresso=atualizar_progresso_gui,
                checar_cancelamento=verificar_se_cancelou
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

            # --- TRATAMENTO DO RETORNO APÓS TERMINAR A THREAD ---
            def finalizar():
                # 2. LIBERAÇÃO DE TODOS OS CAMPOS APÓS O TÉRMINO
                combo_provider.configure(state="readonly")
                combo_key.configure(state="normal")

                if combo_provider.get().lower() == "claude":
                    combo_model.configure(state="normal")
                else:
                    combo_model.configure(state="readonly")
                    
                btn_config_chaves.configure(state="normal")
                
                btn_buscar_prompt.configure(state="normal")
                btn_buscar_entrada.configure(state="normal")
                btn_definir_saida.configure(state="normal")
                chk_subpastas.configure(state="normal")
                
                btn_processar.configure(state="normal", text="INICIAR PROCESSAMENTO")
                btn_cancelar.configure(state="disabled", text="Cancelar")
                btn_limpar.configure(state="normal")
                
                frame_progresso_container.pack_forget()
                progress_bar.pack_forget()
                
                if resultado == "Sucesso":
                    messagebox.showinfo("Concluído", "Todos os arquivos foram processados com sucesso!")
                elif resultado == "CANCELADO":
                    messagebox.showwarning("Interrompido", "O processamento foi cancelado pelo usuário. O relatório e o log foram gerados com os dados parciais.")
                else:
                    messagebox.showerror("Erro", resultado)
            
            # Devolve a atualização dos botões para a thread principal da GUI
            window.after(0, finalizar)

        threading.Thread(target=rotina_segundo_plano).start()

    # --- CANCELAMENTO PROCESSAMENTO ---
    def solicitar_cancelamento():
        nonlocal cancelado_pelo_usuario
        cancelado_pelo_usuario = True
        btn_cancelar.configure(state="disabled", text="Cancelando...")

    # --- GATILHO INTELIGENTE PARA QUANDO O USUÁRIO DIGITA UMA CHAVE MANUALMENTE ---
    def disparar_busca_por_digitacao(*args):
        prov = combo_provider.get()
        key = combo_key.get().strip()
        
        if prov == "Nenhum" or combo_provider.cget("state") == "disabled":
            return
        
        if not key:
            combo_model.configure(values=["Insira uma API key válida..."], state="disabled")
            combo_model.set("Insira uma API key válida...")
            return

        # Evita buscar se o texto for apenas os avisos padrão
        if "válida" in key or "Carregando" in key:
            return
        
        combo_model.configure(values=["Carregando modelos da nova chave..."], state="disabled")
        combo_model.set("Carregando modelos da nova chave...")
            
        def buscar_modelos_digitados(prov, key):
            modelos_reais = listar_modelos_disponiveis(prov, key)
            
            if modelos_reais and str(modelos_reais[0]).startswith("ERRO:"):
                mensagem_erro = modelos_reais[0]
                window.after(0, lambda: combo_model.configure(values=[mensagem_erro]))
                window.after(0, lambda: combo_model.set(mensagem_erro))
                window.after(0, lambda: combo_model.configure(state="disabled"))
            else:
                # --- MESMA CORREÇÃO APLICADA NA DIGITAÇÃO DA CHAVE ---
                if prov.lower() == "claude":
                    placeholder_texto = "Digite o modelo manualmente..."
                    window.after(0, lambda: combo_model.configure(values=[], state="normal"))
                    window.after(0, lambda: combo_model.set(placeholder_texto))
                else:
                    # PARA GEMINI E OPENAI:
                    # Forçamos o estado para 'readonly' ANTES de injetar a nova lista.
                    # Isso remove o modo de edição do Claude se o usuário colar uma chave nova.
                    if modelos_reais:
                        window.after(0, lambda: combo_model.configure(state="readonly", values=modelos_reais))
                        window.after(0, lambda: combo_model.set(modelos_reais[0]))
                    else:
                        window.after(0, lambda: combo_model.configure(values=["Nenhum modelo encontrado"], state="disabled"))
                        window.after(0, lambda: combo_model.set("Nenhum modelo encontrado"))

        threading.Thread(target=buscar_modelos_digitados, args=(prov, key), daemon=True).start()


    # --- DESIGN DA INTERFACE ---
    ctk.CTkLabel(window, text="Painel de Configurações", font=("Arial", 18, "bold"), text_color="#333333").pack(pady=(15, 5))

    # Bloco 1: Credenciais Dinâmicas
    frame_config = ctk.CTkFrame(window, fg_color="#ffffff", border_width=1, border_color="#cccccc", corner_radius=8)
    frame_config.pack(padx=30, pady=10, fill="x")

    # Provider
    ctk.CTkLabel(frame_config, text="Provedor IA:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=0, column=0, padx=(20, 15), pady=12, sticky="e")
    combo_provider = ctk.CTkComboBox(frame_config, values=["Nenhum", "Gemini", "OpenAI", "Claude"], state="readonly", width=310, command=atualizar_campos_por_provedor)
    combo_provider.set("Nenhum")
    combo_provider.grid(row=0, column=1, columnspan=2, pady=12, sticky="w")

    # API KEY
    ctk.CTkLabel(frame_config, text="API Key:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=1, column=0, padx=(20, 15), pady=12, sticky="e")
    combo_key = ctk.CTkComboBox(frame_config, width=310, state="normal")
    combo_key.grid(row=1, column=1, pady=12, sticky="w")

    btn_config_chaves = ctk.CTkButton(
        frame_config, text="⚙️", font=("Arial", 14), width=40, height=28, 
        fg_color="#f0f0f0", hover_color="#e0e0e0", text_color="#333333",
        border_width=1, border_color="#cccccc", corner_radius=6, cursor="hand2",
        command=abrir_gerenciador_chaves
    )
    btn_config_chaves.grid(row=1, column=2, padx=(5, 20), pady=12, sticky="w")

    # Model
    ctk.CTkLabel(frame_config, text="Modelo IA:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=2, column=0, padx=(20, 15), pady=12, sticky="e")
    combo_model = ctk.CTkComboBox(frame_config, width=310, state="disabled")
    combo_model.set("Selecione um Provedor IA...")
    combo_model.grid(row=2, column=1, columnspan=2, pady=12, sticky="w")

    # Bloco 2: Caminhos e Arquivos
    frame_arquivos = ctk.CTkFrame(window, fg_color="#ffffff", border_width=1, border_color="#cccccc", corner_radius=8)
    frame_arquivos.pack(padx=30, pady=10, fill="x")

    # Prompt
    ctk.CTkLabel(frame_arquivos, text="Instruções (Prompt):", font=("Arial", 11, "bold"), text_color="#444444").grid(row=0, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=caminho_prompt_var, width=260, state="readonly").grid(row=0, column=1, pady=10, sticky="w")
    btn_buscar_prompt = ctk.CTkButton(frame_arquivos, text="Buscar...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_prompt)
    btn_buscar_prompt.grid(row=0, column=2, padx=(15, 20), pady=10, sticky="w")

    # Entrada
    ctk.CTkLabel(frame_arquivos, text="Pasta dos PDFs:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=1, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=pasta_entrada_var, width=260, state="readonly").grid(row=1, column=1, pady=10, sticky="w")
    btn_buscar_entrada = ctk.CTkButton(frame_arquivos, text="Buscar...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_entrada)
    btn_buscar_entrada.grid(row=1, column=2, padx=(15, 20), pady=10, sticky="w")

    # Saída
    ctk.CTkLabel(frame_arquivos, text="Salvar Relatório:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=2, column=0, padx=(20, 15), pady=10, sticky="e")
    ctk.CTkEntry(frame_arquivos, textvariable=pasta_saida_var, width=260, state="readonly").grid(row=2, column=1, pady=10, sticky="w")
    btn_definir_saida = ctk.CTkButton(frame_arquivos, text="Definir...", font=("Arial", 10), width=80, cursor="hand2", command=acionar_busca_saida)
    btn_definir_saida.grid(row=2, column=2, padx=(15, 20), pady=10, sticky="w")

    ctk.CTkLabel(frame_arquivos, text="Opções Avançadas:", font=("Arial", 11, "bold"), text_color="#444444").grid(row=3, column=0, padx=(20, 15), pady=10, sticky="e")

    chk_subpastas_var = ctk.BooleanVar(value=False)
    chk_subpastas = ctk.CTkCheckBox(frame_arquivos, text="Incluir arquivos de subpastas", font=("Arial", 11), variable=chk_subpastas_var)
    chk_subpastas.grid(row=3, column=1, columnspan=2, pady=10, sticky="w")

    # --- CONTÊINER DOS BOTÕES DO RODAPÉ ---
    frame_botoes_acao = ctk.CTkFrame(window, fg_color="transparent")
    frame_botoes_acao.pack(pady=20)

    btn_processar = ctk.CTkButton(
        frame_botoes_acao, text="INICIAR PROCESSAMENTO", font=("Arial", 12, "bold"),
        fg_color="#2ecc71", hover_color="#27ae60", text_color="white",
        border_width=2, border_color="#1e7e34", corner_radius=10, height=45, width=240,
        cursor="hand2", command=iniciar_execucao
    )
    btn_processar.pack(side="left", padx=10)

    # Botão Cancelar
    btn_cancelar = ctk.CTkButton(
        frame_botoes_acao, text="Cancelar", font=("Arial", 12, "bold"),
        fg_color="#D32F2F", hover_color="#B71C1C", text_color="white",
        border_width=2, border_color="#9c1f1f", corner_radius=10, height=45, width=120,
        state="disabled", cursor="hand2", command=solicitar_cancelamento
    )
    btn_cancelar.pack(side="left", padx=10)

    btn_limpar = ctk.CTkButton(
        frame_botoes_acao, text="LIMPAR CAMPOS", font=("Arial", 12, "bold"),
        fg_color="#FFD700", hover_color="#ae9c27", text_color="white",
        border_width=2, border_color="#E1A95F", corner_radius=10, height=45, width=160,
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

    # --- VÍNCULOS E CARGA INICIAL SEÇÃO SEGURA ---
    key_string_var = ctk.StringVar()
    combo_key.configure(variable=key_string_var)
    
    # O comando 'trace_add' monitora o modo "write" (qualquer digitação/deleção) e chama a função na hora!
    key_string_var.trace_add("write", disparar_busca_por_digitacao)
    
    # Chama a função inicializer para carregar o estado "Nenhum" e blindar os objetos
    atualizar_campos_por_provedor()

    window.mainloop()

if __name__ == "__main__":
    open_interface()