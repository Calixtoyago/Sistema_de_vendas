import sqlite3
import pandas

class Registradora:
    def __init__(self, banco="registros.db"):
        self.connector = sqlite3.connect(banco)
        self.cursor = self.connector.cursor()
        
    def cadastrarProdutos(self, nome, valor_unitario, estoque):
        self.cursor.execute("""
            INSERT INTO produtos(nome, valor_unitario, estoque)
            VALUES (?, ?, ?)
        """, (nome, valor_unitario, estoque))

        self.connector.commit()
        print("Produto adicionado")
    
    def mostrarProdutos(self):
        self.cursor.execute("SELECT * FROM produtos")
        mostrar = self.cursor.fetchall()
        for produto in mostrar:
            codigo, nome, valor_unitario, estoque = produto
            print(f"{codigo} | {nome} | {valor_unitario} | {estoque}")
        print(mostrar)
    
registrador = Registradora()

# registrador.cadastrarProdutos("Borracha", 1, 10)
# registrador.cadastrarProdutos("Lápis", 0.5, 30)
# registrador.cadastrarProdutos("Caderno", 10, 10)
# registrador.cadastrarProdutos("Estojo", 15, 15)

# registrador.mostrarProdutos()