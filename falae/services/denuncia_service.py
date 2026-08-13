from flask import session

from falae.repositories.denuncia_repository import DenunciaRepository
from falae.repositories.usuario_repository import UsuarioRepository
from falae.services.context_service import ContextService
from falae.workflow.workflow_engine import WorkflowEngine
from falae.services.notificacao_service import (NotificacaoService
)


class DenunciaService:

    STATUS_ETAPA = {
        "NOVA": "TRIAGEM",
        "EM_ANALISE": "INVESTIGACAO",
        "CONCLUIDA": "ENCERRAMENTO",
        "ARQUIVADA": "ARQUIVADA",
    }

    STATUS_PERMITIDOS = set(STATUS_ETAPA.keys())

    @staticmethod
    def _empresa_id():
        return ContextService.empresa()

    @staticmethod
    def listar_unidades():
        repo = DenunciaRepository()

        try:
            return repo.listar_unidades(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_categorias():
        repo = DenunciaRepository()

        try:
            return repo.listar_categorias(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_criticidades():
        repo = DenunciaRepository()

        try:
            return repo.listar_criticidades(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_investigadores():
        repo = UsuarioRepository()

        try:
            return repo.listar_investigadores(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_paginado(
        protocolo=None,
        status=None,
        categoria=None,
        criticidade=None,
        unidade_id=None,
        data_inicio=None,
        data_fim=None,
        ordenacao="mais_recentes",
        page=1,
        per_page=20
    ):
        empresa_id = DenunciaService._empresa_id()

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1

        per_page = max(1, min(int(per_page), 100))
        offset = (page - 1) * per_page

        filtros = ["d.empresa_id = %s"]
        params = [empresa_id]

        if protocolo:
            filtros.append("d.protocolo LIKE %s")
            params.append(f"%{protocolo.strip()}%")

        if status:
            filtros.append("d.status = %s")
            params.append(status)

        if categoria:
            filtros.append("d.categoria = %s")
            params.append(categoria)

        if criticidade:
            filtros.append("d.criticidade = %s")
            params.append(criticidade)

        if unidade_id:
            filtros.append("d.unidade_id = %s")
            params.append(unidade_id)

        if data_inicio:
            filtros.append("d.criado_em >= %s")
            params.append(f"{data_inicio} 00:00:00")

        if data_fim:
            filtros.append("d.criado_em <= %s")
            params.append(f"{data_fim} 23:59:59")

        where_sql = " AND ".join(filtros)

        repo = DenunciaRepository()

        try:
            total_registros = repo.contar_denuncias(where_sql, params)
            total_paginas = (
                total_registros + per_page - 1
            ) // per_page

            denuncias = repo.listar_denuncias(
                where_sql=where_sql,
                params=params,
                order_by=ordenacao,
                per_page=per_page,
                offset=offset
            )

            return {
                "denuncias": denuncias,
                "paginacao": {
                    "page": page,
                    "per_page": per_page,
                    "total_registros": total_registros,
                    "total_paginas": total_paginas
                }
            }
        finally:
            repo.close()

    @staticmethod
    def obter_denuncia(denuncia_id):
        repo = DenunciaRepository()

        try:
            return repo.buscar_por_id(
                denuncia_id,
                DenunciaService._empresa_id()
            )
        finally:
            repo.close()

    @staticmethod
    def obter_denuncia_com_workflow(denuncia_id):
        repo = DenunciaRepository()

        try:
            empresa_id = DenunciaService._empresa_id()

            denuncia = repo.buscar_por_id(denuncia_id, empresa_id)

            if not denuncia:
                return None

            etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"
            workflow = repo.listar_workflow(denuncia_id, empresa_id)

            return {
                "denuncia": denuncia,
                "workflow": workflow,
                "linha_do_tempo": WorkflowEngine.montar_linha_do_tempo(
                    etapa_atual
                ),
                "resumo_etapa": WorkflowEngine.resumo_etapa_atual(
                    etapa_atual
                )
            }
        finally:
            repo.close()

    @staticmethod
    def atualizar_denuncia(
        denuncia_id,
        status,
        criticidade=None,
        observacao_interna=None
    ):
        status = (status or "").strip().upper()

        if status not in DenunciaService.STATUS_PERMITIDOS:
            return {
                "sucesso": False,
                "mensagem": "Status inválido."
            }

        etapa_atual = DenunciaService.STATUS_ETAPA[status]
        repo = DenunciaRepository()

        try:
            resultado = repo.atualizar_denuncia(
                denuncia_id=denuncia_id,
                empresa_id=DenunciaService._empresa_id(),
                status=status,
                criticidade=criticidade or None,
                etapa_atual=etapa_atual,
                observacao_interna=observacao_interna
            )

            if not resultado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Denúncia não encontrada ou acesso não autorizado."
                    )
                }

            return {
                "sucesso": True,
                "mensagem": "Denúncia atualizada com sucesso.",
                **resultado
            }
        finally:
            repo.close()

    @staticmethod
    def obter_dados_exportacao(limite=None):
        repo = DenunciaRepository()

        try:
            return repo.listar_dados_exportacao(
                empresa_id=DenunciaService._empresa_id(),
                limite=limite
            )
        finally:
            repo.close()

    @staticmethod
    def atribuir_responsavel(
        denuncia_id,
        responsavel_id
    ):
        empresa_id = DenunciaService._empresa_id()

        responsavel_id = responsavel_id or None

        repo = DenunciaRepository()
        usuario_repo = UsuarioRepository()

        try:
            denuncia = repo.buscar_por_id(
                denuncia_id,
                empresa_id
            )

            if not denuncia:
                return {
                    "sucesso": False,
                    "mensagem": "Denúncia não encontrada."
                }

            responsavel_anterior_id = (
                denuncia.get("responsavel_id")
            )

            responsavel = None

            if responsavel_id:
                responsavel = usuario_repo.buscar_por_id(
                    responsavel_id,
                    empresa_id
                )

                if not responsavel:
                    return {
                        "sucesso": False,
                        "mensagem": "Responsável inválido."
                    }

            atualizado = repo.atualizar_responsavel(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id,
                responsavel_id=responsavel_id
            )

            if not atualizado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Não foi possível atribuir o responsável."
                    )
                }

            houve_mudanca_responsavel = (
                responsavel_id is not None
                and responsavel_id != responsavel_anterior_id
            )

            if houve_mudanca_responsavel:
                try:
                    NotificacaoService.notificar_responsavel_atribuido(
                        responsavel=responsavel,
                        protocolo=denuncia["protocolo"]
                    )

                except Exception:
                    from flask import current_app

                    current_app.logger.exception(
                        (
                            "Falha ao enviar notificação "
                            "de responsável atribuído | "
                            "empresa_id=%s | "
                            "denuncia_id=%s | "
                            "responsavel_id=%s"
                        ),
                        empresa_id,
                        denuncia_id,
                        responsavel_id
                    )

            return {
                "sucesso": True,
                "mensagem": "Responsável atribuído com sucesso.",
                "responsavel": responsavel,
                "valor_antigo": {
                    "responsavel_id": responsavel_anterior_id,
                    "responsavel": denuncia.get("responsavel")
                },
                "valor_novo": {
                    "responsavel_id": responsavel_id,
                    "responsavel": (
                        responsavel["nome"]
                        if responsavel
                        else None
                    )
                }
            }

        finally:
            repo.close()
            usuario_repo.close()

    @staticmethod
    def listar_workflow(denuncia_id):
        repo = DenunciaRepository()

        try:
            return repo.listar_workflow(
                denuncia_id,
                DenunciaService._empresa_id()
            )
        finally:
            repo.close()

    @staticmethod
    def iniciar_etapa(workflow_id, responsavel_id=None):
        repo = DenunciaRepository()

        try:
            return repo.iniciar_etapa_workflow(
                workflow_id,
                DenunciaService._empresa_id(),
                responsavel_id
            )
        finally:
            repo.close()

    @staticmethod
    def concluir_etapa(workflow_id, observacao=None):
        repo = DenunciaRepository()

        try:
            return repo.concluir_etapa_workflow(
                workflow_id,
                DenunciaService._empresa_id(),
                observacao
            )
        finally:
            repo.close()

    @staticmethod
    def alterar_etapa_denuncia(denuncia_id, etapa):
        repo = DenunciaRepository()

        try:
            return repo.atualizar_etapa_atual(
                denuncia_id,
                DenunciaService._empresa_id(),
                etapa
            )
        finally:
            repo.close()

    @staticmethod
    def avancar_etapa(denuncia_id, observacao=None):
        repo = DenunciaRepository()

        try:
            empresa_id = DenunciaService._empresa_id()
            usuario_id = session.get("usuario_id")

            denuncia = repo.buscar_por_id(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id
            )

            if not denuncia:
                return {
                    "sucesso": False,
                    "mensagem": "Denúncia não encontrada."
                }

            etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"

            if etapa_atual == "PLANO_ACAO":
                from falae.repositories.plano_acao_repository import (
                    PlanoAcaoRepository
                )

                resumo_planos = PlanoAcaoRepository.resumo_por_denuncia(
                    empresa_id=empresa_id,
                    denuncia_id=denuncia_id
                )

                if resumo_planos["total"] == 0:
                    return {
                        "sucesso": False,
                        "mensagem": (
                            "Cadastre ao menos um plano de ação antes "
                            "de avançar para Validação."
                        )
                    }

                if resumo_planos["pendentes"] > 0:
                    return {
                        "sucesso": False,
                        "mensagem": (
                            "Conclua todos os planos de ação antes "
                            "de avançar para Validação."
                        )
                    }

            proxima_etapa = WorkflowEngine.proxima_etapa(etapa_atual)

            if not proxima_etapa:
                return {
                    "sucesso": False,
                    "mensagem": "Não existe uma próxima etapa."
                }

            proxima_etapa_codigo = proxima_etapa["codigo"]
            proxima_etapa_nome = proxima_etapa["nome"]

            dados_nova_etapa = WorkflowEngine.preparar_inicio_etapa(
                codigo_etapa=proxima_etapa_codigo,
                responsavel_id=denuncia.get("responsavel_id"),
                observacao=observacao
            )

            novo_status = WorkflowEngine.definir_status_por_etapa(
                proxima_etapa_codigo
            )

            repo.avancar_workflow(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id,
                etapa_atual=etapa_atual,
                proxima_etapa=dados_nova_etapa,
                novo_status=novo_status,
                usuario_id=usuario_id,
                observacao=observacao
            )

            return {
                "sucesso": True,
                "mensagem": (
                    f"Denúncia avançada para {proxima_etapa_nome}."
                ),
                "etapa_anterior": etapa_atual,
                "etapa_atual": proxima_etapa_codigo,
                "etapa_nome": proxima_etapa_nome
            }
        finally:
            repo.close()

    @staticmethod
    def etapas_padrao():
        return WorkflowEngine.listar_etapas()
