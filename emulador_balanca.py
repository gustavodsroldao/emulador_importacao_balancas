import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class EmuladorFilizola:
    def __init__(self, master):
        self.master = master
        self.master.title("Emulador de Importação – Modelo Filizola")
        self.master.geometry("1000x600")
        
        # Neste exemplo, o único modelo disponível é Filizola.
        self.modelo = "Filizola"
        label_modelo = tk.Label(master, text=f"Modelo Selecionado: {self.modelo}", font=("Arial", 12, "bold"))
        label_modelo.pack(pady=10)
        
        # Label com a descrição abaixo do modelo selecionado
        self.label_descricao = tk.Label(master,
                                        text="Obs: Este emulador permite importar arquivos TXT referente a carga de produtos, "
                                             "incluindo informações nutricionais, ingredientes e departamentos, conforme o padrão definido",
                                        font=("Arial", 10),
                                        wraplength=500,
                                        justify="left")
        self.label_descricao.pack(pady=5)
        
        
        # Botão para selecionar arquivos TXT (vários)
        self.btn_carregar = tk.Button(master, text="Selecionar Arquivos TXT", command=self.selecionar_arquivos, width=30)
        self.btn_carregar.pack(pady=10)
        
        # Label de status
        self.status_label = tk.Label(master, text="Aguardando arquivos...", fg="black")
        self.status_label.pack(pady=5)
        
        # Treeview para exibir os produtos importados
        colunas = ("Código", "Tipo", "Descrição", "Preço", "Validade",
                   "Nutrição", "Ingredientes", "Departamento")
        self.tabela = ttk.Treeview(master, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=120, anchor=tk.CENTER)
        self.tabela.pack(pady=10, fill=tk.X, padx=20)
        
        # Dicionário para armazenar os produtos (chave: código do produto)
        self.produtos = {}

    def ler_cadtxt(self, arquivo):
        """
        Lê um arquivo CADTXT.TXT e extrai os dados básicos.
        Layout (exemplo):
          - Código do produto: 6 caracteres (posição 0-5)
          - Tipo (P ou U): 1 caractere (posição 6)
          - Descrição: 22 caracteres (posição 7-28)
          - Preço unitário: 7 caracteres (posição 29-35) – valor com duas casas decimais implícitas
          - Validade: 3 caracteres (posição 36-38)
          - Se houver informações nutricionais anexadas, elas iniciam na posição 39.
        """
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if len(linha) < 39:
                        continue  # linha inválida ou incompleta
                    codigo = linha[0:6]
                    tipo = linha[6:7]
                    descricao = linha[7:29].strip()
                    preco_raw = linha[29:36]
                    validade = linha[36:39]
                    
                    try:
                        preco = int(preco_raw) / 100.0
                    except:
                        preco = None
                    self.produtos[codigo] = {
                        "Código": codigo,
                        "Tipo": tipo,
                        "Descrição": descricao,
                        "Preço": preco,
                        "Validade": validade,
                        "Nutrição": None,
                        "Ingredientes": None,
                        "Departamento": None
                    }
                    # Se houver conteúdo extra, trata-o como informação nutricional “bruta”
                    if len(linha) > 39:
                        add_nutri = linha[39:]
                        self.produtos[codigo]["Nutrição"] = add_nutri
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def ler_nutri(self, arquivo):
        """
        Lê o arquivo NUTRI.TXT e atualiza as informações nutricionais dos produtos.
        Layout (exemplo):
          - Código do produto: 6 caracteres (posição 0-5)
          - Porção: 35 caracteres (posição 6-40)
          - Em seguida, os valores nutricionais.
        """
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if len(linha) < 41:
                        continue
                    codigo = linha[0:6]
                    porcao = linha[6:41].strip()
                    valores = linha[41:].strip()
                    info = f"Porção: {porcao} | Valores: {valores}"
                    if codigo in self.produtos:
                        self.produtos[codigo]["Nutrição"] = info
        except Exception as e:
            print(f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def ler_rec_ass(self, arquivo):
        """
        Lê o arquivo REC_ASS.TXT que contém os ingredientes.
        Layout (exemplo):
          - Linha com: espaços + código do produto repetido + ingredientes
          - Linha seguinte contendo apenas "@" (delimitador)
        """
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                linhas = f.readlines()
                i = 0
                while i < len(linhas):
                    linha = linhas[i].rstrip("\n")
                    if len(linha) < 12:
                        i += 1
                        continue
                    # Supondo que o código esteja em uma posição fixa (ex.: posição 12 a 18)
                    codigo = linha[12:18]
                    ingredientes = linha[18:].strip()
                    if codigo in self.produtos:
                        self.produtos[codigo]["Ingredientes"] = ingredientes
                    i += 2  # pula a linha com "@" também
        except Exception as e:
            print(f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def ler_setores(self, arquivo):
        """
        Lê o arquivo SETORES.TXT que contém os departamentos.
        Layout (exemplo):
          - Descrição do departamento: 12 caracteres (posição 0-11)
          - Código do produto: 6 caracteres (posição 12-17)
        """
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if len(linha) < 18:
                        continue
                    depto = linha[0:12].strip()
                    codigo = linha[12:18]
                    if codigo in self.produtos:
                        self.produtos[codigo]["Departamento"] = depto
        except Exception as e:
            print(f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def selecionar_arquivos(self):
        """
        Abre um diálogo para seleção de múltiplos arquivos TXT. De acordo com o nome do arquivo,
        chama a função de leitura correspondente.
        """
        arquivos = filedialog.askopenfilenames(title="Selecione os arquivos TXT",
                                                filetypes=[("Arquivos TXT", "*.txt")])
        if not arquivos:
            return
        
        # Reinicia o dicionário de produtos
        self.produtos = {}
        
        for arq in arquivos:
            nome = os.path.basename(arq).upper()
            if "CADTXT" in nome:
                self.ler_cadtxt(arq)
            elif "NUTRI" in nome:
                self.ler_nutri(arq)
            elif "REC_ASS" in nome:
                self.ler_rec_ass(arq)
            elif "SETORES" in nome:
                self.ler_setores(arq)
            else:
                print(f"Arquivo não identificado (ignorado): {nome}")
        
        self.atualizar_tabela()
    
    def atualizar_tabela(self):
        """
        Atualiza a Treeview com os dados dos produtos importados.
        """
        # Limpa a tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        for prod in self.produtos.values():
            self.tabela.insert('', 'end', values=(
                prod.get("Código", ""),
                prod.get("Tipo", ""),
                prod.get("Descrição", ""),
                prod.get("Preço", ""),
                prod.get("Validade", ""),
                prod.get("Nutrição", ""),
                prod.get("Ingredientes", ""),
                prod.get("Departamento", "")
            ))
        
        total = len(self.produtos)
        self.status_label.config(text=f"{total} produto(s) importado(s).", fg="green")


def main():
    root = tk.Tk()
    app = EmuladorFilizola(root)
    root.mainloop()

if __name__ == "__main__":
    main()
