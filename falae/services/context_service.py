from flask import session


class ContextService:

    @staticmethod
    def usuario():
        return session.get("usuario_id")

    @staticmethod
    def perfil():
        return session.get("perfil")

    @staticmethod
    def assessoria():
        return session.get("assessoria_id")

    @staticmethod
    def empresa():
        empresa_id = session.get("empresa_ativa") or session.get("empresa_id")

        if not empresa_id:
            raise RuntimeError(
                "Nenhuma empresa está definida no contexto atual."
            )

        return int(empresa_id)

    @staticmethod
    def empresa_nome():
        return session.get("empresa_ativa_nome")