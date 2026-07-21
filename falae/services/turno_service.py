from falae.repositories.turno_repository import TurnoRepository
from falae.services.context_service import ContextService


class TurnoService:
    """Regras de negócio relacionadas ao cadastro de turnos."""

    @staticmethod
    def _obter_empresa_id() -> int:
        empresa_id = ContextService.empresa()

        if not empresa_id:
            raise ValueError(
                "Nenhuma empresa ativa foi identificada."
            )

        return int(empresa_id)

    @staticmethod
    def _normalizar_nome(nome: str | None) -> str:
        """
        Remove espaços extras e valida o nome informado.
        """
        nome_normalizado = " ".join((nome or "").strip().split())

        if not nome_normalizado:
            raise ValueError("Informe o nome do turno.")

        if len(nome_normalizado) < 2:
            raise ValueError(
                "O nome do turno deve possuir pelo menos 2 caracteres."
            )

        if len(nome_normalizado) > 100:
            raise ValueError(
                "O nome do turno deve possuir no máximo 100 caracteres."
            )

        return nome_normalizado

    @classmethod
    def listar(cls) -> list[dict]:
        empresa_id = cls._obter_empresa_id()

        return TurnoRepository.listar_por_empresa(empresa_id)

    @classmethod
    def buscar_por_id(cls, turno_id: int) -> dict:
        empresa_id = cls._obter_empresa_id()

        turno = TurnoRepository.buscar_por_id(
            turno_id=turno_id,
            empresa_id=empresa_id,
        )

        if not turno:
            raise ValueError(
                "Turno não encontrado ou sem permissão para acesso."
            )

        return turno

    @classmethod
    def criar(cls, nome: str | None) -> int:
        empresa_id = cls._obter_empresa_id()
        nome_normalizado = cls._normalizar_nome(nome)

        turno_existente = TurnoRepository.buscar_por_nome(
            nome=nome_normalizado,
            empresa_id=empresa_id,
        )

        if turno_existente:
            raise ValueError(
                "Já existe um turno com esse nome nesta empresa."
            )

        return TurnoRepository.criar(
            empresa_id=empresa_id,
            nome=nome_normalizado,
        )

    @classmethod
    def atualizar(
        cls,
        turno_id: int,
        nome: str | None,
    ) -> bool:
        empresa_id = cls._obter_empresa_id()

        turno_atual = TurnoRepository.buscar_por_id(
            turno_id=turno_id,
            empresa_id=empresa_id,
        )

        if not turno_atual:
            raise ValueError(
                "Turno não encontrado ou sem permissão para edição."
            )

        nome_normalizado = cls._normalizar_nome(nome)

        turno_duplicado = TurnoRepository.buscar_por_nome(
            nome=nome_normalizado,
            empresa_id=empresa_id,
            ignorar_turno_id=turno_id,
        )

        if turno_duplicado:
            raise ValueError(
                "Já existe outro turno com esse nome nesta empresa."
            )

        atualizado = TurnoRepository.atualizar(
            turno_id=turno_id,
            empresa_id=empresa_id,
            nome=nome_normalizado,
        )

        if not atualizado:
            raise ValueError("Não foi possível atualizar o turno.")

        return True

    @classmethod
    def excluir(cls, turno_id: int) -> bool:
        empresa_id = cls._obter_empresa_id()

        turno = TurnoRepository.buscar_por_id(
            turno_id=turno_id,
            empresa_id=empresa_id,
        )

        if not turno:
            raise ValueError(
                "Turno não encontrado ou sem permissão para exclusão."
            )

        excluido = TurnoRepository.excluir(
            turno_id=turno_id,
            empresa_id=empresa_id,
        )

        if not excluido:
            raise ValueError("Não foi possível excluir o turno.")

        return True