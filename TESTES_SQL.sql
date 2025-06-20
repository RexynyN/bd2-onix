
-- SELECT setval('autores_id_autor_seq', (SELECT MAX(id_autor) FROM autores));
-- SELECT nextval('autores_id_autor_seq');  -- Mostra qual será o próximo id gerado

-- SELECT * 
-- FROM AUTORES;


-- ALTER SEQUENCE revistas_id_livro_seq RENAME TO revistas_id_revista_seq
-- SELECT setval('livros_id_livro_seq', 100000);
-- SELECT setval('revistas_id_revista_seq', 100000);
-- SELECT setval('dvds_id_dvd_seq', 100000);
-- SELECT setval('artigos_id_artigo_seq', 100000);


-- SELECT * FROM BIBLIOTECA
-- ALTER TABLE autorias DROP COLUMN tipo_midia;



SELECT COUNT(*) FROM LIVROS;
SELECT COUNT(*) FROM DVDS;
SELECT COUNT(*) FROM REVISTAS;
SELECT COUNT(*) FROM ARTIGOS;
SELECT COUNT(*) FROM EMPRESTIMO;
SELECT COUNT(*) FROM Penalizacao;



-- ========================================= QUERIES AND OTIMIZATIONS =========================================
-- 00:251
SELECT e.id_emprestimo, e.data_emprestimo, m.tipo_midia, u.nome
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Usuario u ON e.id_usuario = u.id_usuario
WHERE e.id_usuario = 42
  AND e.data_emprestimo >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY e.data_emprestimo DESC;

-- 01:080
SELECT b.nome AS biblioteca, COUNT(e.id_emprestimo) AS total_emprestimos
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
WHERE e.data_emprestimo >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY b.nome
ORDER BY total_emprestimos DESC;

-- 00:851
SELECT u.id_usuario, u.nome, COUNT(p.id_penalizacao) AS total_penalizacoes
FROM Usuario u
JOIN Penalizacao p ON u.id_usuario = p.id_usuario
GROUP BY u.id_usuario, u.nome
HAVING COUNT(p.id_penalizacao) > 3
ORDER BY total_penalizacoes DESC;


-- 02.136
SELECT m.tipo_midia,
       AVG(e.data_devolucao - e.data_emprestimo) AS media_dias_emprestimo
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
WHERE e.data_devolucao IS NOT NULL
GROUP BY m.tipo_midia;


-- 02.283
SELECT DISTINCT a.nome AS autor, m.tipo_midia
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Autorias au ON m.id_titulo = au.id_titulo
JOIN Autores a ON au.id_autor = a.id_autor
WHERE e.data_emprestimo >= '2024-01-01';



-- ================= Otimizações =================
-- EXTENSÕES
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ÍNDICES SIMPLES
CREATE INDEX idx_midia_id_biblioteca ON Titulo(id_biblioteca);
CREATE INDEX idx_emprestimo_id_usuario ON Emprestimo(id_usuario);
CREATE INDEX idx_emprestimo_id_midia ON Emprestimo(id_titulo);
CREATE INDEX idx_penalizacao_id_usuario ON Penalizacao(id_usuario);
CREATE INDEX idx_autorias_id_autor ON Autorias(id_autor);
CREATE INDEX idx_autorias_id_midia ON Autorias(id_titulo);
CREATE INDEX idx_usuario_email ON Usuario(email);
CREATE INDEX idx_livros_titulo ON Livros(titulo);
CREATE INDEX idx_revistas_titulo ON Revistas(titulo);
CREATE INDEX idx_dvds_titulo ON DVDs(titulo);
CREATE INDEX idx_penalizacao_usuario_emprestimo ON Penalizacao(id_usuario, id_emprestimo);
CREATE INDEX idx_emprestimo_usuario_emprestimo ON emprestimo(id_usuario, id_emprestimo);



-- ÍNDICES FULL-TEXT
CREATE INDEX idx_usuario_nome_trgm ON Usuario USING gin (nome gin_trgm_ops);
CREATE INDEX idx_autores_nome_trgm ON autores USING gin (nome gin_trgm_ops);
CREATE INDEX idx_livros_titulo_trgm ON Livros USING gin (titulo gin_trgm_ops);
CREATE INDEX idx_dvds_titulo_trgm ON dvds USING gin (titulo gin_trgm_ops);
CREATE INDEX idx_revistas_titulo_trgm ON revistas USING gin (titulo gin_trgm_ops);
CREATE INDEX idx_artigos_trgm ON artigos USING gin (titulo gin_trgm_ops);


-- 00:251
-- 00.052
-- 00.053
SELECT e.id_emprestimo, e.data_emprestimo, m.tipo_midia, u.nome
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Usuario u ON e.id_usuario = u.id_usuario
WHERE e.id_usuario = 42
  AND e.data_emprestimo >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY e.data_emprestimo DESC;

-- 01:080
-- 00.829
-- 00.817
SELECT b.nome AS biblioteca, COUNT(e.id_emprestimo) AS total_emprestimos
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
WHERE e.data_emprestimo >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY b.nome
ORDER BY total_emprestimos DESC;

-- 00:851
-- 00.736
-- 00.692
SELECT u.id_usuario, u.nome, COUNT(p.id_penalizacao) AS total_penalizacoes
FROM Usuario u
JOIN Penalizacao p ON u.id_usuario = p.id_usuario
GROUP BY u.id_usuario, u.nome
HAVING COUNT(p.id_penalizacao) > 3
ORDER BY total_penalizacoes DESC;


-- 02.136
-- 01.939
-- 01.847
SELECT m.tipo_midia,
       AVG(e.data_devolucao - e.data_emprestimo) AS media_dias_emprestimo
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
WHERE e.data_devolucao IS NOT NULL
GROUP BY m.tipo_midia;


-- 02.283
-- 01.783
-- 01.703
SELECT DISTINCT a.nome AS autor, m.tipo_midia
FROM Emprestimo e
JOIN Titulo m ON e.id_titulo = m.id_titulo
JOIN Autorias au ON m.id_titulo = au.id_titulo
JOIN Autores a ON au.id_autor = a.id_autor
WHERE e.data_emprestimo >= '2024-01-01';
