import json
from flask import g, session
from falae.repositories.auditoria_repository import AuditoriaRepository
from datetime import date, datetime
from decimal import Decimal


class AuditService:

    @staticmethod
    def registrar(
        modulo,
        acao,
        registro_id=None,
        valor_antigo=None,
        valor_novo=None
    ):
        AuditoriaRepository.registrar(
            empresa_id=session.get("empresa_id"),
            usuario_id=session.get("usuario_id"),
            modulo=modulo,
            acao=acao,
            registro_id=registro_id,
            valor_antigo=json.dumps(
                valor_antigo,
                ensure_ascii=False,
                default=AuditService._serializar_json
            ) if valor_antigo is not None else None,

            valor_novo=json.dumps(
                valor_novo,
                ensure_ascii=False,
                default=AuditService._serializar_json
            ) if valor_novo is not None else None,

            ip=getattr(g, "ip", None),
            user_agent=getattr(g, "user_agent", None),
            request_id=getattr(g, "request_id", None)
        )

    @staticmethod
    def listar_timeline(modulo, registro_id, empresa_id):
        return AuditoriaRepository.listar_por_registro(
            modulo=modulo,
            registro_id=registro_id,
            empresa_id=empresa_id
        )

    @staticmethod
    def listar_ultimos_eventos(empresa_id, limite=5):
        return AuditoriaRepository.listar_ultimos_eventos(
            empresa_id=empresa_id,
            limite=limite
        )
    
    @staticmethod
    def _serializar_json(valor):
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()

        if isinstance(valor, Decimal):
            return float(valor)

        return str(valor)