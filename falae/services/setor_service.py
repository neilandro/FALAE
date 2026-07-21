from falae.repositories.setor_repository import SetorRepository
from falae.services.context_service import ContextService


class SetorService:

    @staticmethod
    def listar():
        empresa_id = ContextService.empresa()
        repo = SetorRepository()

        try:
            return repo.listar_por_empresa(empresa_id)
        finally:
            repo.close()

    @staticmethod
    def obter(setor_id):
        empresa_id = ContextService.empresa()
        repo = SetorRepository()

        try:
            return repo.obter_por_id(
                setor_id=setor_id,
                empresa_id=empresa_id
            )
        finally:
            repo.close()

    @staticmethod
    def preparar_formulario():
        empresa_id = ContextService.empresa()
        repo = SetorRepository()

        try:
            return {
                "unidades": repo.listar_unidades_ativas(empresa_id)
            }
        finally:
            repo.close()

    @staticmethod
    def criar(form):
        empresa_id = ContextService.empresa()
        dados = SetorService._montar_dados_formulario(form)

        validacao = SetorService._validar_dados(dados)

        if not validacao["sucesso"]:
            return validacao

        repo = SetorRepository()

        try:
            unidade = repo.unidade_pertence_empresa(
                unidade_id=dados["unidade_id"],
                empresa_id=empresa_id
            )

            if not unidade:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A unidade selecionada não existe, está inativa "
                        "ou não pertence à empresa atual."
                    )
                }

            setor_existente = repo.existe_nome(
                empresa_id=empresa_id,
                unidade_id=dados["unidade_id"],
                nome=dados["nome"]
            )

            if setor_existente:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe um setor com esse nome "
                        "na unidade selecionada."
                    )
                }

            setor_id = repo.criar(
                empresa_id=empresa_id,
                dados=dados
            )

            return {
                "sucesso": True,
                "mensagem": "Setor cadastrado com sucesso.",
                "setor_id": setor_id
            }
        finally:
            repo.close()

    @staticmethod
    def editar(setor_id, form):
        empresa_id = ContextService.empresa()
        dados = SetorService._montar_dados_formulario(form)

        validacao = SetorService._validar_dados(dados)

        if not validacao["sucesso"]:
            return validacao

        repo = SetorRepository()

        try:
            setor = repo.obter_por_id(
                setor_id=setor_id,
                empresa_id=empresa_id
            )

            if not setor:
                return {
                    "sucesso": False,
                    "mensagem": "Setor não encontrado."
                }

            unidade = repo.unidade_pertence_empresa(
                unidade_id=dados["unidade_id"],
                empresa_id=empresa_id
            )

            if not unidade:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A unidade selecionada não existe, está inativa "
                        "ou não pertence à empresa atual."
                    )
                }

            setor_existente = repo.existe_nome(
                empresa_id=empresa_id,
                unidade_id=dados["unidade_id"],
                nome=dados["nome"],
                setor_id=setor_id
            )

            if setor_existente:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe um setor com esse nome "
                        "na unidade selecionada."
                    )
                }

            repo.atualizar(
                setor_id=setor_id,
                empresa_id=empresa_id,
                dados=dados
            )

            return {
                "sucesso": True,
                "mensagem": "Setor atualizado com sucesso."
            }
        finally:
            repo.close()

    @staticmethod
    def _montar_dados_formulario(form):
        unidade_id = form.get("unidade_id")

        try:
            unidade_id = int(unidade_id)
        except (TypeError, ValueError):
            unidade_id = None

        try:
            ativo = int(form.get("ativo", 1))
        except (TypeError, ValueError):
            ativo = 1

        if ativo not in (0, 1):
            ativo = 1

        return {
            "unidade_id": unidade_id,
            "nome": (form.get("nome") or "").strip(),
            "descricao": (form.get("descricao") or "").strip() or None,
            "ativo": ativo
        }

    @staticmethod
    def _validar_dados(dados):
        if not dados["unidade_id"]:
            return {
                "sucesso": False,
                "mensagem": "Selecione a unidade do setor."
            }

        if not dados["nome"]:
            return {
                "sucesso": False,
                "mensagem": "Informe o nome do setor."
            }

        if len(dados["nome"]) > 150:
            return {
                "sucesso": False,
                "mensagem": (
                    "O nome do setor deve possuir no máximo 150 caracteres."
                )
            }

        if dados["descricao"] and len(dados["descricao"]) > 255:
            return {
                "sucesso": False,
                "mensagem": (
                    "A descrição deve possuir no máximo 255 caracteres."
                )
            }

        return {
            "sucesso": True
        }