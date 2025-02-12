import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import unicodedata

class EmuladorImportacao:
    def __init__(self, master):
        self.master = master
        self.master.title("Emulador de Importação de Produtos")
        self.master.geometry("1050x650")
        self.produtos = {}  # Dicionário com os produtos importados

        self.configurar_estilos()
        self.criar_widgets()

        # Modelo selecionado ("Filizola", "Toledo" ou "Urano")
        self.modelo_selecionado = None

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
    def criar_widgets(self):
        # --- Frame superior: seleção do modelo e opção para Toledo ---
        top_frame = ttk.Frame(self.master, padding=10)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(3, weight=1)
        
        lbl_modelo = ttk.Label(top_frame, text="Modelo Selecionado:", font=("Segoe UI", 12, "bold"))
        lbl_modelo.grid(row=0, column=0, padx=5, sticky="w")
        
        self.combo_modelo = ttk.Combobox(top_frame, 
                                         values=["Filizola", "Toledo", "Urano"],
                                         state="readonly", width=20)
        self.combo_modelo.set("Selecione o Modelo")
        self.combo_modelo.grid(row=0, column=1, padx=5, sticky="w")
        self.combo_modelo.bind("<<ComboboxSelected>>", self.on_modelo_selecionado)
        
        # Frame para os radiobuttons (apenas para Toledo)
        self.frame_toledo = ttk.Frame(top_frame)
        self.toledo_var = tk.StringVar(value="MGV5")
        self.rb_mgv5 = ttk.Radiobutton(self.frame_toledo, text="MGV5", variable=self.toledo_var, value="MGV5")
        self.rb_mgv6 = ttk.Radiobutton(self.frame_toledo, text="MGV6", variable=self.toledo_var, value="MGV6")
        self.rb_mgv5.pack(side="left", padx=5)
        self.rb_mgv6.pack(side="left", padx=5)
        self.frame_toledo.grid(row=0, column=2, padx=10, sticky="w")
        self.frame_toledo.grid_remove()  # Oculta inicialmente
        
        # --- Label de descrição ---
        descricao_texto = (
            "Elgin exporta de: Urano, Filizola e Toledo.\n"
            "Toledo exporta de: exclusivamente Toledo MGV5 e MGV6.\n"
            "Urano exporta de: exclusivamente Urano."
        )
        self.lbl_descricao = ttk.Label(self.master, text=descricao_texto,
                                       font=("Segoe UI", 10),
                                       wraplength=800, justify="left")
        self.lbl_descricao.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # --- Frame para os botões: Importar e Limpar Campos ---
        btn_frame = ttk.Frame(self.master, padding=10)
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.columnconfigure((0,1), weight=1)
        
        self.btn_importar = ttk.Button(btn_frame, text="Importar", command=self.selecionar_arquivos)
        self.btn_importar.grid(row=0, column=0, padx=5, sticky="w")
        
        self.btn_limpar = ttk.Button(btn_frame, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.grid(row=0, column=1, padx=5, sticky="w")
        
        # --- Label de status ---
        self.status_label = ttk.Label(self.master, text="Aguardando arquivos...", foreground="black")
        self.status_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # --- Frame para a Treeview (com barra de rolagem) ---
        tabela_frame = ttk.Frame(self.master, padding=10)
        tabela_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        self.master.rowconfigure(4, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        colunas = ("Código", "Tipo", "Descrição", "Preço", "Validade", "Nutrição", "Ingredientes", "Departamento")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=120, anchor="center")
            
        vsb = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=vsb.set)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)

    def on_modelo_selecionado(self, event):
        modelo = self.combo_modelo.get()
        self.modelo_selecionado = modelo
        if modelo == "Toledo":
            self.frame_toledo.grid()  # Exibe os radiobuttons
        else:
            self.frame_toledo.grid_remove()
    
    # ----------------------
    # Funções de Importação
    # ----------------------
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

    def ler_cadtxt_toledo(self, arquivo):
        formato = self.toledo_var.get()  # "MGV5" ou "MGV6"
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if formato == "MGV5":
                        if len(linha) < 111:
                            linha = linha.ljust(111)
                        if len(linha) != 111:
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

    def ler_produtos_urano(self, arquivo):
        """
        Lê o arquivo Produtos.txt no formato Urano.
        Exemplo de linha:
          10000 0 ABACATE KG              27,00    0D
        Layout:
          - Código:      5 caracteres (posição 0 a 4)
          - Espaço:      1 caractere (posição 5)
          - Tipo:        1 caractere (posição 6)
          - Espaço:      1 caractere (posição 7)
          - Descrição:   24 caracteres (posição 8 a 31)
          - Espaço:      1 caractere (posição 32)
          - Preço:       7 caracteres (posição 33 a 39)
          - Espaços:     4 caracteres (posição 40 a 43)
          - Validade:    2 caracteres (posição 44 a 45)
        """
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.rstrip("\n")
                    if len(linha) < 46:
                        continue
                    codigo = linha[0:5].strip()
                    tipo = linha[6:7].strip()
                    descricao = linha[8:32].strip()
                    preco_str = linha[33:40].strip()
                    try:
                        preco = float(preco_str.replace(",", "."))
                    except Exception:
                        preco = None
                    validade = linha[44:46].strip()
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
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler {os.path.basename(arquivo)}: {e}")

    def selecionar_arquivos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecione os arquivos TXT",
            filetypes=[("Arquivos TXT", "*.txt")]
        )
        if not arquivos:
            return
        
        self.produtos = {}
        for arq in arquivos:
            nome = os.path.basename(arq).upper()
            # Atualização: se o arquivo for ITENSMGV.TXT, consideramos como arquivo de Toledo (MGV5 ou MGV6)
            if "CADTXT" in nome:
                self.ler_cadtxt_filizola(arq)
            elif "TOLEDO" in nome or nome == "ITENSMGV.TXT" or "MGV5" in nome or "MGV6" in nome:
                self.ler_cadtxt_toledo(arq)
            elif nome == "PRODUTOS.TXT" or "URANO" in nome:
                self.ler_produtos_urano(arq)
            else:
                print(f"Arquivo não identificado (ignorado): {nome}")
        
        self.atualizar_tabela()

    
    def atualizar_tabela(self):
        # Remove os itens antigos da Treeview
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        # Insere os produtos importados
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

    def limpar_campos(self):
        # Limpa a tabela e outros campos
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self.combo_modelo.set("Selecione o Modelo")
        self.produtos = {}

# Função principal
def main():
    root = tk.Tk()
    app = EmuladorImportacao(root)
    root.mainloop()

if __name__ == "__main__":
    main()
