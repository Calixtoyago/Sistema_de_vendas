import sqlite3
import pandas as pd

class Registradora:
    def __init__(self, banco="registros.db"):
        self.connector = sqlite3.connect(banco)
        self.cursor = self.connector.cursor()
        
    def cadastrarProdutos(self, nome, valor_unitario, estoque):
        try:
            self.cursor.execute("""
                INSERT INTO produtos(nome, valor_unitario, estoque)
                VALUES (?, ?, ?)
            """, (nome, valor_unitario, estoque))

            self.connector.commit()
            print("Produto adicionado")
        except sqlite3.IntegrityError as ie:
            print(f"Produto {nome} já cadastrado")
    
    def mostrarProdutos(self):
        query = "SELECT * FROM produtos"
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))
        self.cursor.execute("SELECT * FROM produtos")
        print(self.cursor.fetchall())

    def registrarVendas(self, produtos):
        # cria a venda na tabela vendas
        self.cursor.execute("""
            INSERT INTO vendas(quantidade, valor_total)
            VALUES (0, 0)
        """)
        self.cursor.execute("SELECT codigo_venda FROM vendas ORDER BY codigo_venda DESC LIMIT 1")
        id_venda = self.cursor.fetchone()[0]

        # adiciona produto por produto
        for item in produtos:
            codigo_produto, nome, valor_unitario, estoque = item
            self.cursor.execute("""
                INSERT INTO produtos_vendidos (venda_id, produto_id, quantidade, valor_total)
                VALUES (?, ?, ?, ?)
            """, (id_venda, codigo_produto, estoque, valor_unitario))
        print("Venda realizada com sucesso")
        self.connector.commit()

    def mostrarVendas(self):
        query = "SELECT * FROM vendas"
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))
    
    def mostrarProdutosVendidos(self):
        query = """SELECT 
                        pv.venda_id,
                        p.nome,
                        pv.quantidade,
                        pv.valor_total
                    FROM produtos_vendidos pv
                    JOIN produtos p ON pv.produto_id = p.codigo_produto"""
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))

registrador = Registradora()

# registrador.cadastrarProdutos("Borracha", 1, 10)
# registrador.cadastrarProdutos("Lápis", 0.5, 30)
# registrador.cadastrarProdutos("Caderno", 10, 10)
# registrador.cadastrarProdutos("Estojo", 15, 15)
registrador.cadastrarProdutos("Arroz", 20.00, 50)
registrador.cadastrarProdutos("Feijão", 8.50, 40)
registrador.cadastrarProdutos("Macarrão", 5.75, 60)
registrador.cadastrarProdutos("Sabonete", 2.99, 100)
registrador.cadastrarProdutos("Detergente", 3.50, 80)
registrador.cadastrarProdutos("Caderno", 12.00, 30)
registrador.cadastrarProdutos("Lápis", 1.50, 200)
registrador.cadastrarProdutos("Caneta", 2.00, 150)
registrador.cadastrarProdutos("Borracha", 0.75, 120)
registrador.cadastrarProdutos("Leite", 6.90, 35)

registrador.mostrarProdutos()

produtos = [(1, 'Borracha', 1.0, 10), (2, 'Lápis', 0.5, 30), (3, 'Caderno', 10.0, 10), (4, 'Estojo', 15.0, 15), (5, 'Arroz', 20.0, 50), (6, 'Feijão', 8.5, 40), (7, 'Macarrão', 5.75, 60), (8, 'Sabonete', 2.99, 100), (9, 'Detergente', 3.5, 80), (10, 'Caneta', 2.0, 150), (11, 'Leite', 6.9, 35)]

# registrador.registrarVendas(produtos)
# registrador.mostrarProdutosVendidos()
