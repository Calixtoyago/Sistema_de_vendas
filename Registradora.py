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
    
    def registrarVendas(self, lista):
        # cria a venda na tabela vendas
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
        print("Venda realizada com sucesso")

        self.atualizarVendas(venda_id)

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

    def mostrarProdutos(self):
        query = "SELECT * FROM produtos"
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))
        self.cursor.execute("SELECT * FROM produtos")
        print(self.cursor.fetchall())

    def mostrarVendas(self):
        query = "SELECT * FROM vendas"
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))
    
    def mostrarProdutosVendidos(self):
        query = """SELECT 
                        pv.venda_id,
                        p.nome,
                        pv.quantidade,
                        pv.valor_total,
                        v.data_compra
                    FROM produtos_vendidos pv
                    JOIN produtos p ON pv.produto_id = p.codigo_produto
                    JOIN vendas v ON pv.venda_id = v.codigo_venda"""
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))


registrador = Registradora()

registrador.cadastrarProdutos("Borracha", 1, 10)
registrador.cadastrarProdutos("Lápis", 0.5, 30)
registrador.cadastrarProdutos("Caderno", 10, 10)
registrador.cadastrarProdutos("Estojo", 15, 15)
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

lista1 = [(1, 2), (4, 1), (10, 5)]

registrador.registrarVendas(lista1)

lista2 = [(5, 5), (6, 10), (9, 2)]

registrador.registrarVendas(lista2)

print()


registrador.mostrarProdutosVendidos()
registrador.mostrarVendas()
