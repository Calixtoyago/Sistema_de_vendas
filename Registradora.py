import sqlite3
import pandas as pd
from tabulate import tabulate

class Registradora:
    def __init__(self, banco="registros.db"):
        self.connector = sqlite3.connect(banco)
        self.cursor = self.connector.cursor()

    def mostrarTabelasCompletas(self, tabela, show=True):
        query = f"SELECT * FROM {tabela}"
        if show:
            db = pd.read_sql(query, self.connector)
            # if tabela == "produtos":
                # db["valor_unitario"] = db["valor_unitario"].astype(float).round(2)
            print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))
        else:
            return self.cursor.execute(query).fetchall()

    def mostrarProdutosVendidos(self):
        query = """SELECT 
                        pv.venda_id,
                        p.nome,
                        pv.quantidade,
                        pv.valor_total as valor_total,
                        v.data_compra
                    FROM produtos_vendidos pv
                    JOIN produtos p ON pv.produto_id = p.codigo_produto
                    JOIN vendas v ON pv.venda_id = v.codigo_venda"""
        db = pd.read_sql(query, self.connector)
        print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))

    def mostrarVendas(self):
        query = """
                SELECT 
                    v.codigo_venda,
                    group_concat(p.nome, ' | ') as produtos,
                    group_concat(pv.quantidade, ' | ') as quantidade,
                    v.quantidade as quantidade_total,
                    v.valor_total, 
                    v.data_compra
                FROM vendas v
                JOIN produtos_vendidos pv ON v.codigo_venda = pv.venda_id
                JOIN produtos p ON pv.produto_id = p.codigo_produto
                GROUP BY v.codigo_venda
                """
        db = pd.read_sql(query, self.connector)
        # db["valor_total"] = db["valor_total"].astype(float).round(2)
        db = db.rename(columns={'valor_total' : 'valor_total (R$)'})
        print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))

    def mostrarUnicaVenda(self, venda_id):
        query = """
                SELECT 
                    v.codigo_venda,
                    group_concat(p.nome, ' | ') as produtos,
                    group_concat(pv.quantidade, ' | ') as quantidade,
                    v.quantidade as quantidade_total,
                    v.valor_total, 
                    v.data_compra
                FROM vendas v
                JOIN produtos_vendidos pv ON v.codigo_venda = pv.venda_id
                JOIN produtos p ON pv.produto_id = p.codigo_produto
                WHERE v.codigo_venda = ?
                GROUP BY v.codigo_venda
                """
        db = pd.read_sql(query, self.connector, params=(venda_id, ))
        # db["valor_total"] = db["valor_total"].astype(float).round(2)
        db = db.rename(columns={'valor_total' : 'valor_total (R$)'})
        print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))
        # print(db.to_string(index=False))
    
class Produtos(Registradora):
    def __init__(self, banco="registros.db"):
        super().__init__(banco)

    def cadastrarProdutos(self, nome, valor_unitario, estoque):
        try:
            self.cursor.execute("""
                INSERT INTO produtos(nome, valor_unitario, estoque)
                VALUES (?, ?, ?)
            """, (nome, valor_unitario, estoque))
        except sqlite3.IntegrityError as ie:
            print(f"Produto {nome} já cadastrado")
        else:
            self.connector.commit()
            print("Produto cadastrado")
        
            self.mostrarTabelasCompletas("produtos")
    
    def verProdutoUnico(self, nome):
        query = "SELECT * FROM produtos WHERE nome = ?"
        db = pd.read_sql(query, self.connector, params=(nome,))
        print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))

class Vendas(Registradora):
    def __init__(self, banco="registros.db"):
        super().__init__(banco)
    
    def registrarVendas(self, lista):
        # cria a venda na tabela vendas
        try:
            self.cursor.execute("""
                INSERT INTO vendas(quantidade, valor_total)
                VALUES (0, 0)
            """)
            self.cursor.execute("SELECT codigo_venda FROM vendas ORDER BY codigo_venda DESC LIMIT 1")
            venda_id = self.cursor.fetchone()[0]

            # adiciona produto por produto
            for item in lista:
                produto_id, quantidade = item
                valor_unitario = self.cursor.execute("SELECT valor_unitario FROM produtos WHERE codigo_produto = ?", (produto_id,)).fetchone()[0]
                valor_unitario = float(f"{valor_unitario:.2f}")
                self.cursor.execute("""
                    INSERT INTO produtos_vendidos (venda_id, produto_id, quantidade, valor_total)
                    VALUES (?, ?, ?, ?)
                """, (venda_id, produto_id, quantidade, valor_unitario * quantidade))
        except sqlite3.IntegrityError:
            produto = self.cursor.execute("SELECT nome FROM produtos WHERE codigo_produto = ?", (produto_id,)).fetchone()[0]
            self.cursor.execute("DELETE FROM vendas WHERE codigo_venda = ?", (venda_id, ))
            print(f"Produto {produto} não tem estoque suficiente")
            
            self.connector.commit()
        else:
            self.atualizarVendas(venda_id)

            print("Venda realizada com sucesso")
            self.mostrarUnicaVenda(venda_id)

            self.connector.commit()

    def atualizarVendas(self, venda_id):
        quantidade_total_venda = self.cursor.execute("SELECT SUM(quantidade) FROM produtos_vendidos WHERE venda_id = ?", (venda_id,)).fetchone()[0]
        valor_total_venda = self.cursor.execute("SELECT SUM(valor_total) FROM produtos_vendidos WHERE venda_id = ?", (venda_id,)).fetchone()[0]
        self.cursor.execute("""
            UPDATE vendas
            SET  
                quantidade = ?,
                valor_total = ?
            WHERE codigo_venda = ?
        """, (quantidade_total_venda, valor_total_venda, venda_id))

def menu():
    ADMIN = "12345"
    registrador = Registradora()
    vendas = Vendas()
    produtos = Produtos()

    opcao = ""
    while opcao != 0:
        print("""
[1] Registrar produto
[2] Registrar venda
[3] Ver vendas
[4] Ver produtos
[0] Sair
    """)
        while True:
            opcao = input(">>>> ")
            if opcao in ('1', '2', '3', '4'):
                break
            else:
                print("Opcao invalida")

        match opcao:
            case '1':
                try:
                    nome = input("Nome do produto: ")
                    valor = float(input("Valor unitario: R$"))
                    estoque = int(input("Quantidade no estoque: "))

                    valor = float(f"{valor:.2f}")

                except TypeError:
                    print("Valor inserido invalido - registro cancelado")
                else:
                    produtos.cadastrarProdutos(nome, valor, estoque)
                    print("Produto cadastrado com sucesso")
                    produtos.verProdutoUnico(nome)
            case '2':
                adicionar = ""
                lista_produtos = []
                while adicionar != "nao":
                    registrador.mostrarTabelasCompletas("produtos")
                    
                    try:
                        codigo = int(input("Codigo do produto: "))
                        quantidade = int(input("Quantidade: "))
                    except ValueError:
                        print("ERROR - Valor invalido. Compra cancelada")
                    else:
                        quantidade_produto = registrador.cursor.execute("SELECT estoque FROM produtos WHERE codigo_produto = ?", (codigo, )).fetchone()[0]
                        if quantidade > quantidade_produto:
                            print("ERROR - Quantidade ultrapassa o estoque do produto")
                            continue
                        lista_produtos.append((codigo, quantidade))
                    
                    while True:
                        adicionar = input("Adicionar outro produto: [Sim/Nao] >> ").lower().strip()
                        if adicionar not in ("sim", "nao"):
                            print("ERROR - Opcao invalida")
                        else: 
                            break
                
                # codigos = []
                # for produto in lista_produtos:
                #     codigos.append(produto[0])

                # placeholders = ','.join(['?'] * len(codigos))  # Resultado: '?,?,?'
                # query = f"SELECT * FROM produtos WHERE codigo_produto IN ({placeholders})"
                # db = pd.read_sql(query, registrador.connector, params=codigos)
                # print(tabulate(db, headers='keys', tablefmt='fancy_grid', showindex=False))

                # registrador.cursor.execute()
                vendas.registrarVendas(lista_produtos)
                
            case '3':
                registrador.mostrarVendas()

    
menu()
