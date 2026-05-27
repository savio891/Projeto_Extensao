import tkinter as tk
from tkinter import ttk

def open_interface():
    window = tk.Tk()
    window.title("Automação Processamento de PDFs com IA")

    # Define o tamanho inicial da window (Largura x Altura)
    window.geometry("600x480")
    window.configure(bg="#f5f5f5")

    # 1. Título Principal
    label_titulo = tk.Label(
        window,
        text="Painel de Configurações",
        font=("Arial", 16, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )

    # O pack() é um gerenciador simples que joga o elemento na tela e o centraliza
    label_titulo.pack(pady=20)

    # Criando uma "Caixa de Agrupamento" para o formulário
    frame_config = tk.LabelFrame(
        window,
        text=" Credenciais e Modelo ",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=20,
        bg="#ffffff",
        relief="solid",
        borderwidth=1
    )
    frame_config.pack(padx=30, pady=10, fill="both", expand=True)


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
    
    # --- ALINHAMENTO DO FORMULÁRIO COM GRID ---
    
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

    # Mantém a janela viva
    window.mainloop()

if __name__ == "__main__":
    open_interface()