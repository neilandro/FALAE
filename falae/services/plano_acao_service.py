from flask import session
from falae.repositories.plano_acao_repository import PlanoAcaoRepository
from falae.services.audit_service import AuditService


class PlanoAcaoService:

    @staticmethod
    def listar_por_denuncia(denuncia_id):
        return PlanoAcaoRepository.listar_por_denuncia(
            empresa_id=session["empresa_id"],
            denuncia_id=denuncia_id
        )
    
    @staticmethod
    def obter(plano_id):
        return PlanoAcaoRepository.buscar_por_id(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )
    
    @staticmethod
    def atualizar(plano_id, titulo, descricao, responsavel, prazo, status):
        plano_antigo = PlanoAcaoRepository.buscar_por_id(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )

        if not plano_antigo:
            return None
        
        PlanoAcaoRepository.atualizar(
            empresa_id=session["empresa_id"],
            plano_id=plano_id,
            titulo=titulo,
            descricao=descricao,
            responsavel=responsavel,
            prazo=prazo,
            status=status
        )
    
        AuditService.registrar(
            modulo="planos_acao",
            acao="atualizar_plano_acao",
            registro_id=plano_id,
            valor_antigo={
                "id": plano_antigo["id"],
                "denuncia_id": plano_antigo["denuncia_id"],
                "titulo": plano_antigo["titulo"],
                "descricao": plano_antigo["descricao"],
                "responsavel": plano_antigo["responsavel"],
                "prazo": str(plano_antigo["prazo"]) if plano_antigo["prazo"] else None,
                "status": plano_antigo["status"]
            },
            valor_novo={
                "titulo": titulo,
                "descricao": descricao,
                "responsavel": responsavel,
                "prazo": prazo,
                "status": status
            }
        )

        return plano_antigo["denuncia_id"]
    
    @staticmethod
    def excluir(plano_id):
        plano = PlanoAcaoRepository.buscar_por_id(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )

        if not plano:
            return None

        PlanoAcaoRepository.excluir(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )

        AuditService.registrar(
            modulo="planos_acao",
            acao="excluir_plano_acao",
            registro_id=plano_id,
            valor_antigo={
                "id": plano["id"],
                "denuncia_id": plano["denuncia_id"],
                "titulo": plano["titulo"],
                "descricao": plano["descricao"],
                "responsavel": plano["responsavel"],
                "prazo": str(plano["prazo"]) if plano["prazo"] else None,
                "status": plano["status"]
            }
        )

        return plano["denuncia_id"]
    

    @staticmethod
    def criar(denuncia_id, titulo, descricao, responsavel, prazo, status):
        titulo = (titulo or "").strip()
        descricao = (descricao or "").strip() or None
        responsavel = (responsavel or "").strip() or None
        status = status or "PENDENTE"

        if not titulo:
            return {
                "sucesso": False,
                "mensagem": "Informe o título do plano de ação."
            }

        duplicado = PlanoAcaoRepository.buscar_duplicado_recente(
            empresa_id=session["empresa_id"],
            denuncia_id=denuncia_id,
            titulo=titulo,
            responsavel=responsavel,
            prazo=prazo,
            status=status
        )

        if duplicado:
            return {
                "sucesso": False,
                "duplicado": True,
                "plano_id": duplicado["id"],
                "mensagem": "Este plano já foi registrado. O envio duplicado foi ignorado."
            }

        plano_id = PlanoAcaoRepository.criar(
            empresa_id=session["empresa_id"],
            denuncia_id=denuncia_id,
            titulo=titulo,
            descricao=descricao,
            responsavel=responsavel,
            prazo=prazo,
            status=status,
            criado_por=session.get("usuario_id")
        )

        AuditService.registrar(
            modulo="planos_acao",
            acao="criar_plano_acao",
            registro_id=plano_id,
            valor_novo={
                "denuncia_id": denuncia_id,
                "titulo": titulo,
                "responsavel": responsavel,
                "prazo": prazo,
                "status": status
            }
        )

        return {
            "sucesso": True,
            "plano_id": plano_id,
            "mensagem": "Plano de ação criado com sucesso."
        }

    @staticmethod
    def resumo_por_denuncia(denuncia_id):
        return PlanoAcaoRepository.resumo_por_denuncia(
            empresa_id=session["empresa_id"],
            denuncia_id=denuncia_id
        )
    
    @staticmethod
    def concluir(plano_id):
        plano = PlanoAcaoRepository.buscar_por_id(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )

        if not plano:
            return None

        PlanoAcaoRepository.concluir(
            empresa_id=session["empresa_id"],
            plano_id=plano_id
        )

        AuditService.registrar(
            modulo="planos_acao",
            acao="concluir_plano_acao",
            registro_id=plano_id,
            valor_antigo={
                "id": plano["id"],
                "denuncia_id": plano["denuncia_id"],
                "titulo": plano["titulo"],
                "status": plano["status"],
                "prazo": str(plano["prazo"]) if plano["prazo"] else None
            },
            valor_novo={
                "status": "CONCLUIDA"
            }
        )

        return plano["denuncia_id"]