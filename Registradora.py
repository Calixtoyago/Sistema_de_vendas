import sqlite3
import pandas as pd

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
        query = "SELECT * FROM produtos"
        db = pd.read_sql(query, self.connector)
        print(db.to_string(index=False))
    
registrador = Registradora()

# registrador.cadastrarProdutos("Borracha", 1, 10)
# registrador.cadastrarProdutos("Lápis", 0.5, 30)
# registrador.cadastrarProdutos("Caderno", 10, 10)
# registrador.cadastrarProdutos("Estojo", 15, 15)

registrador.mostrarProdutos()