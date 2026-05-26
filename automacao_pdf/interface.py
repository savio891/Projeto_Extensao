import tkinter as tk
from tkinter import ttk

def iniciar_interface():
    janela = tk.Tk()
    janela.title("Automação Processamento de PDFs com IA")

    # Define o tamanho inicial da janela (Largura x Altura)
    janela.geometry("600x480")

    # Criando um rótulo na tela
    label_titulo = tk.Label(
        janela,
        text="Configurações de Processamento",
        font=("Arial", 14, "bold")
    )

    # O pack() é um gerenciador simples que joga o elemento na tela e o centraliza
    label_titulo.pack(pady=15)

    # Criando o menu de escolha do provedor
    label_provider = tk.Label(
        janela,
        text="Selecione o Provedor IA para o processamento:",
        font=("Arial", 10)
    )
    label_provider.pack(pady=5)

    # O ttk.Combobox cria uma caixa de escolha com opções em formato de lista
    combo_provider = ttk.Combobox(
        janela,
        values=["Gemini", "OpenAI", "Claude"], state="readonly"
    )
    combo_provider.current(0) # Deixa o "Gemini" selecionado como padrão
    combo_provider.pack(pady=5)

    # Mantém a janela "viva" e aberta assistindo aos cliques do usuário
    janela.mainloop()

if __name__ == "__main__":
    iniciar_interface()