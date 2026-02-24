-- 1. Tabela de Usuários

CREATE TABLE usuarios (
    nickname VARCHAR(50) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    senha VARCHAR(100) NOT NULL
);

-- 2. Tabela de Fornecedores
CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    nome_fornecedor VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100)
);

-- 3. Tabela de Produtos
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome_produto VARCHAR(100) NOT NULL,
    codigo VARCHAR(50),
    preco NUMERIC(10, 2) NOT NULL,
    quantidade INTEGER NOT NULL,
    data_validade DATE,
    categoria VARCHAR(50),
    
    fornecedor_id INTEGER REFERENCES fornecedores(id) ON DELETE RESTRICT,
    usuario_criador VARCHAR(50) REFERENCES usuarios(nickname) ON DELETE SET NULL
);

INSERT INTO usuarios (nome, nickname, senha) 
VALUES ('ADMINISTRADOR', 'admin', 'admin')
ON CONFLICT (nickname) DO NOTHING;