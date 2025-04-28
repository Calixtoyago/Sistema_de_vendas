import sqlite3
import pandas as pd
from tabulate import tabulate

class Registradora:
    def __init__(self, banco="registros.db"):
        self.connector = sqlite3.connect(banco)
        self.cursor = self.connector.cursor()

    def mostrarTabelasCompletas(self, tabela):
        query = f"SELECT * FROM {tabela}"
        db = pd.read_sql(query, self.connector)
        print(tabulate(db, headers='keys', tablefmt='fancy_grid'))

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
        print(tabulate(db, headers='keys', tablefmt='fancy_grid'))

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
        db["valor_total"] = db["valor_total"].map('{:.2f}'.format)
        db = db.rename(columns={'valor_total' : 'valor_total (R$)'})
        print(tabulate(db, headers='keys', tablefmt='fancy_grid'))

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
        db["valor_total"] = db["valor_total"].map('{:.2f}'.format)
        db = db.rename(columns={'valor_total' : 'valor_total (R$)'})
        print(tabulate(db, headers='keys', tablefmt='fancy_grid'))
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



registrador = Registradora()
vendas = Vendas()
produtos = Produtos()

# produtos.cadastrarProdutos("Borracha", 1, 10)
# produtos.cadastrarProdutos("Lápis", 0.5, 30)
# produtos.cadastrarProdutos("Caderno", 10, 10)
# produtos.cadastrarProdutos("Estojo", 15, 15)
# produtos.cadastrarProdutos("Arroz", 20.00, 50)
# produtos.cadastrarProdutos("Feijão", 8.50, 40)
# produtos.cadastrarProdutos("Macarrão", 5.75, 60)
# produtos.cadastrarProdutos("Sabonete", 2.99, 100)
# produtos.cadastrarProdutos("Detergente", 3.50, 80)
# produtos.cadastrarProdutos("Caderno", 12.00, 30)
# produtos.cadastrarProdutos("Lápis", 1.50, 200)
# produtos.cadastrarProdutos("Caneta", 2.00, 150)
# produtos.cadastrarProdutos("Borracha", 0.75, 120)
# produtos.cadastrarProdutos("Leite", 6.90, 35)

# registrador.mostrarTabelasCompletas("produtos")

# lista1 = [(1, 2), (4, 1), (10, 5)]

# vendas.registrarVendas(lista1)

# lista2 = [(5, 5), (6, 10), (9, 2)]

# vendas.registrarVendas(lista2)

print()


registrador.mostrarProdutosVendidos()
registrador.mostrarVendas()

registrador.mostrarTabelasCompletas("produtos")

lista3 = [(1, 10)]

vendas.registrarVendas(lista3)

lista4 = [(7, 30), (5, 10)]

vendas.registrarVendas(lista4)

# registrador.mostrarProdutosVendidos()
registrador.mostrarVendas()
registrador.mostrarTabelasCompletas("produtos")
