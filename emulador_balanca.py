import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Este emulador foi desenvolvido para simular a importação de produtos para balanças de supermercado.
# Inclusive com foco principal para uso de testes no navi e link.]

class EmuladorImportacao:
    def __init__(self, master):
        self.master = master
        self.master.title("Emulador de Importação de Produtos")
        self.master.geometry("1050x650")
        
        # Área de seleção do modelo
        top_frame = tk.Frame(master)
        top_frame.pack(pady=10)
        
        label_modelo = tk.Label(top_frame, text="Modelo Selecionado:", font=("Arial", 12, "bold"))
        label_modelo.grid(row=0, column=0, sticky="w", padx=5)
        
        self.combo_modelo = ttk.Combobox(top_frame, values=["Filizola", "Toledo", "Urano"], state="readonly", width=20)
        self.combo_modelo.set("Selecione o Modelo")
        self.combo_modelo.grid(row=0, column=1, padx=5)
        self.combo_modelo.bind("<<ComboboxSelected>>", self.on_modelo_selecionado)
        
        # Frame para os radiobuttons de Toledo (aparece somente se o modelo for Toledo)
        self.frame_toledo = tk.Frame(top_frame)
        self.toledo_var = tk.StringVar(value="MGV5")
        self.rb_mgv5 = tk.Radiobutton(self.frame_toledo, text="MGV5", variable=self.toledo_var, value="MGV5")
        self.rb_mgv6 = tk.Radiobutton(self.frame_toledo, text="MGV6", variable=self.toledo_var, value="MGV6")
        self.rb_mgv5.pack(side="left", padx=5)
        self.rb_mgv6.pack(side="left", padx=5)
        self.frame_toledo.grid(row=0, column=2, padx=10)
        self.frame_toledo.grid_remove()  # Oculta inicialmente
        
        # Label com a descrição abaixo da seleção
        self.label_descricao = tk.Label(master,
                                        text="Elgin exporta de: Urano, Filizola e Toledo.\n"
                                        "Toledo exporta de: exclusivamente Toledo MGV5 e MGV6.\n"
                                        "Urano exporta de: exclusivamente Urano.\n"
                                        "Upx exporta de: exclusivamente Toledo.\n",
                                        font=("Arial", 10),
                                        wraplength=800,
                                        justify="left")
        self.label_descricao.pack(pady=5)
        
        # Botão para selecionar arquivos TXT
        self.btn_carregar = tk.Button(master, text="Importar", command=self.selecionar_arquivos, width=20)
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
        
        # Guarda qual modelo está sendo utilizado
        self.modelo_selecionado = None

    def on_modelo_selecionado(self, event):
        modelo = self.combo_modelo.get()
        self.modelo_selecionado = modelo
        if modelo == "Toledo":
            self.frame_toledo.grid()  # Exibe os radiobuttons
        elif modelo == "Filizola":
            self.frame_toledo.grid_remove()
    # --------------------------------------------------
    # Funções de leitura para Filizola (CADTXT e demais arquivos)
    # --------------------------------------------------
    def ler_cadtxt_filizola(self, arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if len(linha) < 39:
                        continue
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
                    if len(linha) > 39:
                        add_nutri = linha[39:]
                        self.produtos[codigo]["Nutrição"] = add_nutri.strip()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    # --------------------------------------------------
    # Funções de leitura para Toledo
    # --------------------------------------------------
    def ler_cadtxt_toledo(self, arquivo):
        formato = self.toledo_var.get()  # "MGV5" ou "MGV6"
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if formato == "MGV5":
                        # Se a linha tiver menos de 111 caracteres, completa com espaços
                        if len(linha) < 111:
                            linha = linha.ljust(111)
                        if len(linha) != 111:
                            continue  # ignora linhas que não tenham o tamanho exato
                        codigo = linha[0:6]
                        tipo = linha[6:7]
                        descricao = linha[7:29].strip()
                        preco_raw = linha[29:36]
                        validade = linha[36:39]
                        try:
                            preco = int(preco_raw) / 100.0
                        except:
                            preco = None
                        extra1 = linha[39:63]
                        extra2 = linha[63:87]
                        extra3 = linha[87:111]
                        self.produtos[codigo] = {
                            "Código": codigo,
                            "Tipo": tipo,
                            "Descrição": descricao,
                            "Preço": preco,
                            "Validade": validade,
                            "Nutrição": extra1.strip(),
                            "Ingredientes": extra2.strip(),
                            "Departamento": extra3.strip()
                        }
                    elif formato == "MGV6":
                        if len(linha) < 39:
                            continue
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
                        if len(linha) > 39:
                            add_nutri = linha[39:]
                            self.produtos[codigo]["Nutrição"] = add_nutri.strip()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def ler_nutri(self, arquivo):
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
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                linhas = f.readlines()
                i = 0
                while i < len(linhas):
                    linha = linhas[i].rstrip("\n")
                    if len(linha) < 12:
                        i += 1
                        continue
                    codigo = linha[12:18]
                    ingredientes = linha[18:].strip()
                    if codigo in self.produtos:
                        self.produtos[codigo]["Ingredientes"] = ingredientes
                    i += 2
        except Exception as e:
            print(f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def ler_setores(self, arquivo):
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
        arquivos = filedialog.askopenfilenames(title="Selecione os arquivos TXT",
                                                filetypes=[("Arquivos TXT", "*.txt")])
        if not arquivos:
            return
        
        self.produtos = {}
        
        modelo = self.combo_modelo.get()
        formato_toledo = self.toledo_var.get() if modelo == "Toledo" else None

        for arq in arquivos:
            nome = os.path.basename(arq).upper()
            if "CADTXT" in nome:
                if modelo == "Filizola":
                    self.ler_cadtxt_filizola(arq)
                elif modelo == "Toledo":
                    self.ler_cadtxt_toledo(arq)
            elif "NUTRI" in nome:
                if modelo == "Filizola" or (modelo == "Toledo" and formato_toledo == "MGV6"):
                    self.ler_nutri(arq)
            elif "REC_ASS" in nome:
                if modelo == "Filizola" or (modelo == "Toledo" and formato_toledo == "MGV6"):
                    self.ler_rec_ass(arq)
            elif "SETORES" in nome:
                if modelo == "Filizola" or (modelo == "Toledo" and formato_toledo == "MGV6"):
                    self.ler_setores(arq)
            else:
                print(f"Arquivo não identificado (ignorado): {nome}")
        
        self.atualizar_tabela()
    
    def atualizar_tabela(self):
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
    app = EmuladorImportacao(root)
    root.mainloop()

if __name__ == "__main__":
    main()
