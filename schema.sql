CREATE TABLE IF NOT EXISTS produtos(
    codigo_produto INTEGER,
    nome TEXT UNIQUE NOT NULL,
    valor_unitario REAL NOT NULL,
    estoque INTEGER NOT NULL,
    PRIMARY KEY (codigo_produto)
);

CREATE TABLE IF NOT EXISTS vendas(
    codigo_venda INTEGER,
    quantidade INTEGER NOT NULL,
    valor_total REAL NOT NULL,
    data_compra NUMERIC NOT NULL,
    PRIMARY KEY (codigo_venda)
);

CREATE TABLE IF NOT EXISTS produtos_vendidos(
    venda_id INTEGER,
    produto_id INTEGER,
    quantidade REAL NOT NULL,
    valor_total INTEGER NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(codigo_venda),
    FOREIGN KEY (produto_id) REFERENCES produtos(codigo_produto)
);