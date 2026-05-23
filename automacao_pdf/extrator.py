import PyPDF2
import sys
import os

def extrair_texto_seguro(caminho_completo):
        
        try:
            # Sanitização caminho (evitar fraudes de caminhos)
            caminho_final = os.path.abspath(caminho_completo)
            
            # Bloqueio de Extensão 
            if not caminho_final.lower().endswith('.pdf'):
                 return "Erro: Apenas arquivos .pdf são permitidos."

            # Verificação de Existência
            if not os.path.exists(caminho_final):
             return f"Erro: O arquivo '{caminho_final}' não foi encontrado!"
            
            # Verificação tamanho de arquivo (Segurança)
            if os.path.getsize(caminho_final) > (15 * 1024 * 1024): # 15 MB
                 return "Erro: O arquivo excede o limite de segurança."

            with open(caminho_final, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                texto_completo = ""

                for pagina in leitor.pages:
                    texto_completo += pagina.extract_text()

                return texto_completo if texto_completo.strip() else "PDF sem texto extraível."

        except Exception as e:
             return f"Erro interno ao procesar o documento."
        
if __name__ == "__main__":
     if len(sys.argv) > 1:
       print(extrair_texto_seguro(sys.argv[1]))
     else: 
         print("Erro: Informe o nome do arquivo que está dentro da pasta uploads.")