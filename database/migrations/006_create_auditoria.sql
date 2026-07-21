CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,

    empresa_id INT NULL,
    usuario_id INT NULL,

    modulo VARCHAR(100) NOT NULL,
    acao VARCHAR(100) NOT NULL,
    registro_id INT NULL,

    valor_antigo TEXT NULL,
    valor_novo TEXT NULL,

    ip VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    request_id VARCHAR(100) NULL,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_empresa (empresa_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_modulo (modulo),
    INDEX idx_acao (acao),
    INDEX idx_request_id (request_id)
);