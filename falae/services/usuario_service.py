import re
import secrets
import string

from flask import session

from extensions import bcrypt
from falae.repositories.usuario_repository import (
    UsuarioRepository
)
from falae.services.audit_service import AuditService


class UsuarioService:

    TAMANHO_MINIMO_SENHA = 8

    CARACTERES_ESPECIAIS = "@#$%&*!_-"

    MENSAGEM_SENHA_FORTE = (
        "A senha deve possuir no mínimo 8 caracteres, "
        "incluindo letra maiúscula, letra minúscula, "
        "número e caractere especial."
    )

    @staticmethod
    def listar_usuarios():
        perfil = session.get("perfil")

        repo = UsuarioRepository()

        try:
            if perfil == "SUPER_ADMIN":
                return repo.listar_usuarios_global()

            if perfil == "ADM_ASSESSORIA":
                return repo.listar_usuarios_por_assessoria(
                    session.get("assessoria_id")
                )

            if perfil == "ADMIN_EMPRESA":
                return repo.listar_usuarios_por_empresa(
                    session.get("empresa_id")
                )

            return []

        finally:
            repo.close()

    @staticmethod
    def pode_acessar_usuario(usuario):
        perfil_logado = session.get("perfil")

        if not usuario:
            return False

        if perfil_logado == "SUPER_ADMIN":
            return True

        if usuario.get("perfil") == "SUPER_ADMIN":
            return False

        if perfil_logado == "ADM_ASSESSORIA":
            return (
                usuario.get("assessoria_id")
                == session.get("assessoria_id")
                or usuario.get("empresa_id")
                in UsuarioService._empresas_da_assessoria_logada()
            )

        if perfil_logado == "ADMIN_EMPRESA":
            return (
                usuario.get("empresa_id")
                == session.get("empresa_id")
                and usuario.get("perfil") in [
                    "GESTOR",
                    "INVESTIGADOR",
                    "VISUALIZADOR"
                ]
            )

        return False

    @staticmethod
    def _empresas_da_assessoria_logada():
        repo = UsuarioRepository()

        try:
            empresas = repo.listar_empresas()
            assessoria_id = session.get(
                "assessoria_id"
            )

            return [
                empresa["id"]
                for empresa in empresas
                if empresa.get("assessoria_id")
                == assessoria_id
            ]

        finally:
            repo.close()

    @staticmethod
    def obter_usuario(usuario_id):
        repo = UsuarioRepository()

        try:
            return repo.obter_usuario(
                usuario_id
            )

        finally:
            repo.close()

    @staticmethod
    def preparar_formulario_usuario():
        repo = UsuarioRepository()

        try:
            return {
                "empresas": repo.listar_empresas(),
                "assessorias": repo.listar_assessorias(),
                "perfis": UsuarioService._perfis_disponiveis()
            }

        finally:
            repo.close()

    @staticmethod
    def criar_usuario(dados_form):
        perfil_logado = session.get("perfil")

        senha = (
            dados_form.get("senha") or ""
        )

        validacao_senha = (
            UsuarioService.validar_senha_forte(
                senha
            )
        )

        if not validacao_senha["sucesso"]:
            return validacao_senha

        dados = {
            "nome": UsuarioService._normalizar_texto(
                dados_form.get("nome")
            ),
            "email": UsuarioService._normalizar_email(
                dados_form.get("email")
            ),
            "celular": UsuarioService._normalizar_texto(
                dados_form.get("celular")
            ),
            "whatsapp": UsuarioService._normalizar_texto(
                dados_form.get("whatsapp")
            ),
            "perfil": dados_form.get("perfil"),
            "empresa_id": (
                dados_form.get("empresa_id")
                or None
            ),
            "assessoria_id": (
                dados_form.get("assessoria_id")
                or None
            ),
            "ativo": dados_form.get(
                "ativo",
                1
            ),
            "senha_hash": (
                bcrypt.generate_password_hash(
                    senha
                ).decode("utf-8")
            )
        }

        validacao = (
            UsuarioService._validar_criacao_usuario(
                perfil_logado=perfil_logado,
                dados=dados
            )
        )

        if not validacao["sucesso"]:
            return validacao

        repo = UsuarioRepository()

        try:
            usuario_id = repo.criar_usuario(
                dados
            )

            AuditService.registrar(
                modulo="usuarios",
                acao="criar_usuario",
                registro_id=usuario_id,
                valor_antigo=None,
                valor_novo={
                    "nome": dados["nome"],
                    "email": dados["email"],
                    "perfil": dados["perfil"],
                    "empresa_id": dados["empresa_id"],
                    "assessoria_id": dados["assessoria_id"],
                    "ativo": dados["ativo"]
                }
            )

            return {
                "sucesso": True,
                "usuario_id": usuario_id
            }

        finally:
            repo.close()

    @staticmethod
    def editar_usuario(
        usuario_id,
        dados_form
    ):
        perfil_logado = session.get("perfil")

        usuario_atual = (
            UsuarioService.obter_usuario(
                usuario_id
            )
        )

        if not UsuarioService.pode_acessar_usuario(
            usuario_atual
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Acesso não autorizado para editar este usuário."
                )
            }
        
        editando_proprio_usuario = (
            int(usuario_id)
            == int(
                session.get(
                    "usuario_id",
                    0
                )
            )
        )


        dados = {
            "nome": UsuarioService._normalizar_texto(
                dados_form.get("nome")
            ),
            "email": UsuarioService._normalizar_email(
                dados_form.get("email")
            ),
            "celular": UsuarioService._normalizar_texto(
                dados_form.get("celular")
            ),
            "whatsapp": UsuarioService._normalizar_texto(
                dados_form.get("whatsapp")
            ),
            "perfil": dados_form.get("perfil"),
            "empresa_id": (
                dados_form.get("empresa_id")
                or None
            ),
            "assessoria_id": (
                dados_form.get("assessoria_id")
                or None
            ),
            "ativo": dados_form.get(
                "ativo",
                1
            )
        }

        editando_proprio_usuario = (
            int(usuario_id)
            == int(
                session.get(
                    "usuario_id",
                    0
                )
            )
        )

        validacao = (
            UsuarioService._validar_criacao_usuario(
                perfil_logado=perfil_logado,
                dados=dados
            )
        )

        if not validacao["sucesso"]:
            return validacao

        if (
            perfil_logado != "SUPER_ADMIN"
            and dados["perfil"] == "SUPER_ADMIN"
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Você não pode atribuir o perfil SUPER_ADMIN."
                )
            }

        repo = UsuarioRepository()

        try:
            atualizado = repo.atualizar_usuario(
                usuario_id,
                dados
            )

            if not atualizado:
                usuario_existente = (
                    repo.obter_usuario(
                        usuario_id
                    )
                )

                if not usuario_existente:
                    return {
                        "sucesso": False,
                        "mensagem": "Usuário não encontrado."
                    }

            AuditService.registrar(
                modulo="usuarios",
                acao="editar_usuario",
                registro_id=usuario_id,
                valor_antigo={
                    "nome": usuario_atual.get("nome"),
                    "email": usuario_atual.get("email"),
                    "perfil": usuario_atual.get("perfil"),
                    "empresa_id": usuario_atual.get("empresa_id"),
                    "assessoria_id": usuario_atual.get(
                        "assessoria_id"
                    ),
                    "ativo": usuario_atual.get("ativo")
                },
                valor_novo=dados
            )

            return {
                "sucesso": True
            }

        finally:
            repo.close()

    @staticmethod
    def validar_senha_forte(
        senha: str | None
    ) -> dict:
        senha_normalizada = (
            senha or ""
        )

        if len(
            senha_normalizada
        ) < UsuarioService.TAMANHO_MINIMO_SENHA:
            return {
                "sucesso": False,
                "mensagem": (
                    UsuarioService.MENSAGEM_SENHA_FORTE
                )
            }

        if not re.search(
            r"[A-Z]",
            senha_normalizada
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    UsuarioService.MENSAGEM_SENHA_FORTE
                )
            }

        if not re.search(
            r"[a-z]",
            senha_normalizada
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    UsuarioService.MENSAGEM_SENHA_FORTE
                )
            }

        if not re.search(
            r"\d",
            senha_normalizada
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    UsuarioService.MENSAGEM_SENHA_FORTE
                )
            }

        padrao_especial = (
            "["
            + re.escape(
                UsuarioService.CARACTERES_ESPECIAIS
            )
            + "]"
        )

        if not re.search(
            padrao_especial,
            senha_normalizada
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    UsuarioService.MENSAGEM_SENHA_FORTE
                )
            }

        return {
            "sucesso": True
        }

    @staticmethod
    def _normalizar_texto(
        valor
    ):
        if valor is None:
            return None

        return str(
            valor
        ).strip()

    @staticmethod
    def _normalizar_email(
        email
    ):
        return (
            str(
                email or ""
            )
            .strip()
            .lower()
        )

    @staticmethod
    def _perfis_disponiveis():
        perfil_logado = session.get("perfil")

        if perfil_logado == "SUPER_ADMIN":
            return [
                "SUPER_ADMIN",
                "ADM_ASSESSORIA",
                "ADMIN_EMPRESA",
                "GESTOR",
                "INVESTIGADOR",
                "VISUALIZADOR"
            ]

        if perfil_logado == "ADM_ASSESSORIA":
            return [
                "ADMIN_EMPRESA",
                "GESTOR",
                "INVESTIGADOR",
                "VISUALIZADOR"
            ]

        if perfil_logado == "ADMIN_EMPRESA":
            return [
                "GESTOR",
                "INVESTIGADOR",
                "VISUALIZADOR"
            ]

        return []

    @staticmethod
    def _validar_criacao_usuario(
        perfil_logado,
        dados
    ):
        perfil_novo = dados.get("perfil")

        if not dados.get("nome"):
            return {
                "sucesso": False,
                "mensagem": "Informe o nome do usuário."
            }

        if not dados.get("email"):
            return {
                "sucesso": False,
                "mensagem": "Informe o e-mail do usuário."
            }

        if perfil_novo not in UsuarioService._perfis_disponiveis():
            return {
                "sucesso": False,
                "mensagem": (
                    "O perfil selecionado não está disponível "
                    "para o usuário logado."
                )
            }

        if perfil_logado == "SUPER_ADMIN":
            if (
                perfil_novo == "ADM_ASSESSORIA"
                and not dados.get("assessoria_id")
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Informe a assessoria para usuários "
                        "ADM_ASSESSORIA."
                    )
                }

            if (
                perfil_novo in [
                    "ADMIN_EMPRESA",
                    "GESTOR",
                    "INVESTIGADOR",
                    "VISUALIZADOR"
                ]
                and not dados.get("empresa_id")
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Informe a empresa para este perfil "
                        "de usuário."
                    )
                }

            return {
                "sucesso": True
            }

        if perfil_logado == "ADM_ASSESSORIA":
            if perfil_novo not in [
                "ADMIN_EMPRESA",
                "GESTOR",
                "INVESTIGADOR",
                "VISUALIZADOR"
            ]:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Perfil não permitido para ADM_ASSESSORIA."
                    )
                }

            if not dados.get("empresa_id"):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Informe a empresa do usuário."
                    )
                }

            empresas_permitidas = (
                UsuarioService._empresas_da_assessoria_logada()
            )

            try:
                empresa_id = int(
                    dados["empresa_id"]
                )
            except (
                TypeError,
                ValueError
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A empresa selecionada é inválida."
                    )
                }

            if empresa_id not in empresas_permitidas:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A empresa selecionada não pertence "
                        "à assessoria logada."
                    )
                }

            dados["empresa_id"] = empresa_id

            # Usuários vinculados a uma empresa recebem o vínculo
            # pela própria empresa. Não precisam de assessoria_id direto.
            dados["assessoria_id"] = None

            return {
                "sucesso": True
            }

        if perfil_logado == "ADMIN_EMPRESA":
            if perfil_novo not in [
                "GESTOR",
                "INVESTIGADOR",
                "VISUALIZADOR"
            ]:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Perfil não permitido para ADMIN_EMPRESA."
                    )
                }

            dados["empresa_id"] = session.get(
                "empresa_id"
            )

            dados["assessoria_id"] = None

            return {
                "sucesso": True
            }

        return {
            "sucesso": False,
            "mensagem": (
                "Você não possui permissão para criar usuários."
            )
        }

    @staticmethod
    def alterar_senha_obrigatoria(
        usuario_id,
        nova_senha,
        confirmar_senha
    ):
        """
        Permite que o usuário autenticado substitua a senha
        temporária por uma senha pessoal e definitiva.
        """

        usuario_sessao_id = session.get(
            "usuario_id"
        )

        if not usuario_sessao_id:
            return {
                "sucesso": False,
                "mensagem": (
                    "Sua sessão não foi identificada. "
                    "Faça login novamente."
                )
            }

        try:
            usuario_id = int(
                usuario_id
            )

            usuario_sessao_id = int(
                usuario_sessao_id
            )

        except (
            TypeError,
            ValueError
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Usuário inválido para alteração de senha."
                )
            }

        if usuario_id != usuario_sessao_id:
            return {
                "sucesso": False,
                "mensagem": (
                    "Você não pode alterar a senha "
                    "de outro usuário."
                )
            }

        nova_senha = nova_senha or ""
        confirmar_senha = confirmar_senha or ""

        if nova_senha != confirmar_senha:
            return {
                "sucesso": False,
                "mensagem": (
                    "A confirmação da nova senha "
                    "não corresponde à senha informada."
                )
            }

        validacao = (
            UsuarioService.validar_senha_forte(
                nova_senha
            )
        )

        if not validacao["sucesso"]:
            return validacao

        repo = UsuarioRepository()

        try:
            dados_seguranca = (
                repo.buscar_dados_seguranca(
                    usuario_id
                )
            )

            if not dados_seguranca:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Usuário não encontrado."
                    )
                }

            if not dados_seguranca.get(
                "ativo"
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Este usuário está inativo."
                    )
                }

            senha_atual_hash = (
                dados_seguranca.get(
                    "senha_hash"
                )
            )

            if (
                senha_atual_hash
                and bcrypt.check_password_hash(
                    senha_atual_hash,
                    nova_senha
                )
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A nova senha deve ser diferente "
                        "da senha temporária."
                    )
                }

            nova_senha_hash = (
                bcrypt.generate_password_hash(
                    nova_senha
                ).decode(
                    "utf-8"
                )
            )

            atualizado = (
                repo.atualizar_senha_definitiva(
                    usuario_id=usuario_id,
                    senha_hash=nova_senha_hash
                )
            )

            if not atualizado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Não foi possível atualizar sua senha."
                    )
                }

            AuditService.registrar(
                modulo="usuarios",
                acao="alterar_senha_obrigatoria",
                registro_id=usuario_id,
                valor_antigo={
                    "troca_obrigatoria": True
                },
                valor_novo={
                    "troca_obrigatoria": False,
                    "alterado_pelo_proprio_usuario": True
                }
            )

            session[
                "trocar_senha_primeiro_acesso"
            ] = False

            return {
                "sucesso": True,
                "mensagem": (
                    "Senha atualizada com sucesso."
                )
            }

        finally:
            repo.close()

    @staticmethod
    def resetar_senha(
        usuario_id
    ):
        """
        Redefine administrativamente a senha de um usuário.

        A senha gerada é temporária e deverá ser substituída
        obrigatoriamente no próximo login.
        """

        repo = UsuarioRepository()

        try:
            usuario = (
                repo.buscar_por_id_global(
                    usuario_id
                )
            )

            if not usuario:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Usuário não encontrado."
                    )
                }

            if (
                int(usuario.get("id"))
                == int(
                    session.get(
                        "usuario_id",
                        0
                    )
                )
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Utilize a opção de alteração de senha "
                        "para modificar sua própria senha."
                    )
                }

            if not UsuarioService.pode_acessar_usuario(
                usuario
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Acesso não autorizado para redefinir "
                        "a senha deste usuário."
                    )
                }

            perfil_logado = session.get(
                "perfil"
            )

            perfil_usuario = usuario.get(
                "perfil"
            )

            if (
                perfil_logado == "ADM_ASSESSORIA"
                and perfil_usuario
                in [
                    "SUPER_ADMIN",
                    "ADM_ASSESSORIA"
                ]
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "O administrador da assessoria não pode "
                        "redefinir a senha deste perfil."
                    )
                }

            if (
                perfil_logado == "ADMIN_EMPRESA"
                and perfil_usuario
                not in [
                    "GESTOR",
                    "INVESTIGADOR",
                    "VISUALIZADOR",
                    "AUDITOR"
                ]
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "O administrador da empresa não pode "
                        "redefinir a senha deste perfil."
                    )
                }

            senha_temporaria = (
                UsuarioService
                ._gerar_senha_temporaria()
            )

            senha_hash = (
                bcrypt.generate_password_hash(
                    senha_temporaria
                ).decode(
                    "utf-8"
                )
            )

            atualizado = repo.atualizar_senha(
                usuario_id=usuario_id,
                senha_hash=senha_hash
            )

            if not atualizado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Não foi possível atualizar "
                        "a senha do usuário."
                    )
                }

            AuditService.registrar(
                modulo="usuarios",
                acao="resetar_senha",
                registro_id=usuario_id,
                valor_antigo={
                    "usuario": usuario.get(
                        "nome"
                    ),
                    "email": usuario.get(
                        "email"
                    ),
                    "perfil": perfil_usuario
                },
                valor_novo={
                    "resetado_por": session.get(
                        "usuario_id"
                    ),
                    "senha_temporaria": True,
                    "troca_obrigatoria": True,
                    "bloqueio_removido": True
                }
            )

            return {
                "sucesso": True,
                "usuario": usuario,
                "senha_temporaria": senha_temporaria
            }

        finally:
            repo.close()

    @staticmethod
    def _gerar_senha_temporaria(
        tamanho=10
    ):
        tamanho_final = max(
            int(tamanho),
            UsuarioService.TAMANHO_MINIMO_SENHA
        )

        caracteres_obrigatorios = [
            secrets.choice(
                string.ascii_uppercase
            ),
            secrets.choice(
                string.ascii_lowercase
            ),
            secrets.choice(
                string.digits
            ),
            secrets.choice(
                UsuarioService.CARACTERES_ESPECIAIS
            )
        ]

        conjunto_completo = (
            string.ascii_letters
            + string.digits
            + UsuarioService.CARACTERES_ESPECIAIS
        )

        caracteres_restantes = [
            secrets.choice(
                conjunto_completo
            )
            for _ in range(
                tamanho_final
                - len(caracteres_obrigatorios)
            )
        ]

        caracteres_senha = (
            caracteres_obrigatorios
            + caracteres_restantes
        )

        secrets.SystemRandom().shuffle(
            caracteres_senha
        )

        return "".join(
            caracteres_senha
        )
