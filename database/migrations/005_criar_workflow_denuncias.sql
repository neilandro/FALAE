CREATE TABLE IF NOT EXISTS denuncia_workflow (
    id INT AUTO_INCREMENT PRIMARY KEY,

    denuncia_id INT NOT NULL,
    empresa_id INT NOT NULL,

    etapa VARCHAR(50) NOT NULL,
    status_etapa ENUM('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA', 'ATRASADA', 'CANCELADA') DEFAULT 'PENDENTE',

    responsavel_id INT NULL,

    prazo_limite DATETIME NULL,
    iniciado_em DATETIME NULL,
    concluido_em DATETIME NULL,

    observacao TEXT NULL,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workflow_denuncia
        FOREIGN KEY (denuncia_id)
        REFERENCES denuncias(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_workflow_empresa
        FOREIGN KEY (empresa_id)
        REFERENCES empresas(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_workflow_responsavel
        FOREIGN KEY (responsavel_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL,

    INDEX idx_workflow_denuncia (denuncia_id),
    INDEX idx_workflow_empresa (empresa_id),
    INDEX idx_workflow_etapa (etapa),
    INDEX idx_workflow_status_etapa (status_etapa),
    INDEX idx_workflow_prazo (prazo_limite)
);