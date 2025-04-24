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
    data_compra NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP, 
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

-- CREATE TRIGGER IF NOT EXISTS vendas_registradas
-- AFTER INSERT ON itens_venda
-- BEGIN
--     -- Tenta inserir a venda (se não existir)
--     INSERT INTO vendas (id, total_itens, valor_total)
--     SELECT NEW.venda_id, 
--            SUM(quantidade), 
--            SUM(quantidade * preco_unitario)
--     FROM itens_venda
--     WHERE venda_id = NEW.venda_id
--     ON CONFLICT(id) DO NOTHING;

--     -- Atualiza a venda, caso já exista
--     UPDATE vendas
--     SET total_itens = (
--         SELECT SUM(quantidade)
--         FROM itens_venda
--         WHERE venda_id = NEW.venda_id
--     ),
--     valor_total = (
--         SELECT SUM(quantidade * preco_unitario)
--         FROM itens_venda
--         WHERE venda_id = NEW.venda_id
--     )
--     WHERE id = NEW.venda_id;
-- END;