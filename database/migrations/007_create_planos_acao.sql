CREATE TABLE IF NOT EXISTS planos_acao (
    id INT AUTO_INCREMENT PRIMARY KEY,

    empresa_id INT NOT NULL,
    denuncia_id INT NOT NULL,

    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NULL,

    responsavel VARCHAR(150) NULL,
    prazo DATE NULL,

    status ENUM('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA') DEFAULT 'PENDENTE',

    criado_por INT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NULL,

    INDEX idx_empresa (empresa_id),
    INDEX idx_denuncia (denuncia_id),
    INDEX idx_status (status),

    CONSTRAINT fk_plano_denuncia
        FOREIGN KEY (denuncia_id)
        REFERENCES denuncias(id),

    CONSTRAINT fk_plano_usuario
        FOREIGN KEY (criado_por)
        REFERENCES usuarios(id)
);