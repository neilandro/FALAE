import re
import secrets
import string

from flask import session

from extensions import bcrypt
from falae.repositories.usuario_repository import (
    UsuarioRepository
)
from falae.services.audit_service import AuditService
from falae.services.context_service import ContextService


class UsuarioService:

    TAMANHO_MINIMO_SENHA = 8
    CARACTERES_ESPECIAIS = "@#$%&*!_-"

    PERFIS_OPERACIONAIS = {
        "GESTOR",
        "INVESTIGADOR",
        "VISUALIZADOR"
    }

    MENSAGEM_SENHA_FORTE = (
        "A senha deve possuir no mínimo 8 caracteres, "
        "incluindo letra maiúscula, letra minúscula, "
        "número e caractere especial."
    )

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar_texto(valor):
        if valor is None:
            return None

        texto = str(valor).strip()

        if not texto:
            return None

        return " ".join(texto.split())

    @staticmethod
    def _normalizar_email(email):
        return str(email or "").strip().lower()

    @staticmethod
    def _normalizar_id(valor):
        if valor in (None, ""):
            return None

        try:
            valor = int(valor)
        except (TypeError, ValueError):
            return None

        return valor if valor > 0 else None

    @staticmethod
    def _normalizar_ativo(valor):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            return 1

        return valor if valor in (0, 1) else 1

    @staticmethod
    def _montar_dados_usuario(dados_form):
        return {
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
            "perfil": UsuarioService._normalizar_texto(
                dados_form.get("perfil")
            ),
            "empresa_id": UsuarioService._normalizar_id(
                dados_form.get("empresa_id")
            ),
            "assessoria_id": UsuarioService._normalizar_id(
                dados_form.get("assessoria_id")
            ),
            "ativo": UsuarioService._normalizar_ativo(
                dados_form.get("ativo", 1)
            )
        }

    # =========================================================
    # LISTAGEM E CONSULTA
    # =========================================================

    @staticmethod
    def listar_usuarios():
        perfil = session.get("perfil")
        repo = UsuarioRepository()

        try:
            if perfil == "SUPER_ADMIN":
                return repo.listar_usuarios_global()

            if perfil == "ADM_ASSESSORIA":
                assessoria_id = UsuarioService._normalizar_id(
                    session.get("assessoria_id")
                )

                if not assessoria_id:
                    return []

                return repo.listar_usuarios_por_assessoria(
                    assessoria_id
                )

            if perfil == "ADMIN_EMPRESA":
                empresa_id = ContextService.empresa()

                if not empresa_id:
                    return []

                return repo.listar_usuarios_por_empresa(
                    empresa_id
                )

            return []

        finally:
            repo.close()

    @staticmethod
    def pode_acessar_usuario(usuario):
        if not usuario:
            return False

        perfil_logado = session.get("perfil")

        if perfil_logado == "SUPER_ADMIN":
            return True

        if usuario.get("perfil") == "SUPER_ADMIN":
            return False

        if perfil_logado == "ADM_ASSESSORIA":
            assessoria_id = UsuarioService._normalizar_id(
                session.get("assessoria_id")
            )

            if not assessoria_id:
                return False

            if (
                usuario.get("perfil") == "ADM_ASSESSORIA"
                and usuario.get("assessoria_id") == assessoria_id
                and usuario.get("empresa_id") is None
            ):
                return True

            empresa_id = UsuarioService._normalizar_id(
                usuario.get("empresa_id")
            )

            return (
                empresa_id
                in UsuarioService._empresas_da_assessoria_logada()
            )

        if perfil_logado == "ADMIN_EMPRESA":
            empresa_id = ContextService.empresa()

            return (
                usuario.get("empresa_id") == empresa_id
                and usuario.get("perfil")
                in UsuarioService.PERFIS_OPERACIONAIS
            )

        return False

    @staticmethod
    def _empresas_da_assessoria_logada():
        assessoria_id = UsuarioService._normalizar_id(
            session.get("assessoria_id")
        )

        if not assessoria_id:
            return []

        repo = UsuarioRepository()

        try:
            empresas = repo.listar_empresas_por_assessoria(
                assessoria_id
            )

            return [
                empresa["id"]
                for empresa in empresas
            ]

        finally:
            repo.close()

    @staticmethod
    def obter_usuario(usuario_id):
        usuario_id = UsuarioService._normalizar_id(
            usuario_id
        )

        if not usuario_id:
            return None

        perfil = session.get("perfil")
        repo = UsuarioRepository()

        try:
            if perfil == "SUPER_ADMIN":
                return repo.buscar_por_id_global(
                    usuario_id
                )

            if perfil == "ADM_ASSESSORIA":
                assessoria_id = UsuarioService._normalizar_id(
                    session.get("assessoria_id")
                )

                if not assessoria_id:
                    return None

                return repo.buscar_por_id_assessoria(
                    usuario_id=usuario_id,
                    assessoria_id=assessoria_id
                )

            if perfil == "ADMIN_EMPRESA":
                empresa_id = ContextService.empresa()

                if not empresa_id:
                    return None

                usuario = repo.buscar_por_id(
                    usuario_id=usuario_id,
                    empresa_id=empresa_id
                )

                if (
                    usuario
                    and usuario.get("perfil")
                    in UsuarioService.PERFIS_OPERACIONAIS
                ):
                    return usuario

            return None

        finally:
            repo.close()

    @staticmethod
    def preparar_formulario_usuario():
        perfil = session.get("perfil")
        repo = UsuarioRepository()

        try:
            empresas = []
            assessorias = []

            if perfil == "SUPER_ADMIN":
                empresas = repo.listar_empresas()
                assessorias = repo.listar_assessorias()

            elif perfil == "ADM_ASSESSORIA":
                assessoria_id = UsuarioService._normalizar_id(
                    session.get("assessoria_id")
                )

                if assessoria_id:
                    empresas = (
                        repo.listar_empresas_por_assessoria(
                            assessoria_id
                        )
                    )

                    assessoria = repo.buscar_assessoria_ativa(
                        assessoria_id
                    )

                    if assessoria:
                        assessorias = [assessoria]

            elif perfil == "ADMIN_EMPRESA":
                empresa_id = ContextService.empresa()

                if empresa_id:
                    empresa = repo.buscar_empresa_ativa(
                        empresa_id
                    )

                    if empresa:
                        empresas = [empresa]

            return {
                "empresas": empresas,
                "assessorias": assessorias,
                "perfis": UsuarioService._perfis_disponiveis()
            }

        finally:
            repo.close()

    # =========================================================
    # CRIAÇÃO
    # =========================================================

    @staticmethod
    def criar_usuario(dados_form):
        perfil_logado = session.get("perfil")
        senha = dados_form.get("senha") or ""

        validacao_senha = UsuarioService.validar_senha_forte(
            senha
        )

        if not validacao_senha["sucesso"]:
            return validacao_senha

        dados = UsuarioService._montar_dados_usuario(
            dados_form
        )

        validacao = UsuarioService._validar_dados_usuario(
            perfil_logado=perfil_logado,
            dados=dados
        )

        if not validacao["sucesso"]:
            return validacao

        dados["senha_hash"] = (
            bcrypt.generate_password_hash(
                senha
            ).decode("utf-8")
        )

        repo = UsuarioRepository()

        try:
            if repo.existe_email(dados["email"]):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe um usuário cadastrado "
                        "com este e-mail."
                    )
                }

            validacao_vinculo = (
                UsuarioService._validar_vinculos_no_banco(
                    repo=repo,
                    dados=dados
                )
            )

            if not validacao_vinculo["sucesso"]:
                return validacao_vinculo

            usuario_id = repo.criar_usuario(dados)

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
                "mensagem": "Usuário cadastrado com sucesso.",
                "usuario_id": usuario_id
            }

        finally:
            repo.close()

    # =========================================================
    # EDIÇÃO
    # =========================================================

    @staticmethod
    def editar_usuario(usuario_id, dados_form):
        usuario_id = UsuarioService._normalizar_id(
            usuario_id
        )

        if not usuario_id:
            return {
                "sucesso": False,
                "mensagem": "Usuário inválido."
            }

        perfil_logado = session.get("perfil")
        usuario_atual = UsuarioService.obter_usuario(
            usuario_id
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

        dados = UsuarioService._montar_dados_usuario(
            dados_form
        )

        validacao = UsuarioService._validar_dados_usuario(
            perfil_logado=perfil_logado,
            dados=dados
        )

        if not validacao["sucesso"]:
            return validacao

        usuario_sessao_id = UsuarioService._normalizar_id(
            session.get("usuario_id")
        )

        if (
            usuario_sessao_id == usuario_id
            and dados["ativo"] == 0
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Você não pode desativar o próprio usuário."
                )
            }

        repo = UsuarioRepository()

        try:
            if repo.existe_email(
                email=dados["email"],
                usuario_id=usuario_id
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe outro usuário cadastrado "
                        "com este e-mail."
                    )
                }

            validacao_vinculo = (
                UsuarioService._validar_vinculos_no_banco(
                    repo=repo,
                    dados=dados
                )
            )

            if not validacao_vinculo["sucesso"]:
                return validacao_vinculo

            if perfil_logado == "SUPER_ADMIN":
                atualizado = repo.atualizar_usuario_global(
                    usuario_id=usuario_id,
                    dados=dados
                )

            elif perfil_logado == "ADM_ASSESSORIA":
                atualizado = (
                    repo.atualizar_usuario_por_assessoria(
                        usuario_id=usuario_id,
                        assessoria_id=session.get(
                            "assessoria_id"
                        ),
                        dados=dados
                    )
                )

            elif perfil_logado == "ADMIN_EMPRESA":
                atualizado = (
                    repo.atualizar_usuario_por_empresa(
                        usuario_id=usuario_id,
                        empresa_id=ContextService.empresa(),
                        dados=dados
                    )
                )

            else:
                atualizado = False

            if not atualizado:
                usuario_existente = repo.buscar_por_id_global(
                    usuario_id
                )

                if not usuario_existente:
                    return {
                        "sucesso": False,
                        "mensagem": "Usuário não encontrado."
                    }

                # rowcount pode ser zero quando os dados enviados
                # são exatamente iguais aos valores atuais.
                dados_iguais = UsuarioService._dados_iguais(
                    usuario_existente,
                    dados
                )

                if not dados_iguais:
                    return {
                        "sucesso": False,
                        "mensagem": (
                            "Não foi possível atualizar o usuário."
                        )
                    }

            AuditService.registrar(
                modulo="usuarios",
                acao="editar_usuario",
                registro_id=usuario_id,
                valor_antigo={
                    "nome": usuario_atual.get("nome"),
                    "email": usuario_atual.get("email"),
                    "perfil": usuario_atual.get("perfil"),
                    "empresa_id": usuario_atual.get(
                        "empresa_id"
                    ),
                    "assessoria_id": usuario_atual.get(
                        "assessoria_id"
                    ),
                    "ativo": usuario_atual.get("ativo")
                },
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
                "mensagem": "Usuário atualizado com sucesso."
            }

        finally:
            repo.close()

    @staticmethod
    def _dados_iguais(usuario, dados):
        campos = (
            "nome",
            "email",
            "celular",
            "whatsapp",
            "perfil",
            "empresa_id",
            "assessoria_id",
            "ativo"
        )

        return all(
            usuario.get(campo) == dados.get(campo)
            for campo in campos
        )

    # =========================================================
    # VALIDAÇÕES
    # =========================================================

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
    def _validar_dados_usuario(perfil_logado, dados):
        if not dados.get("nome"):
            return {
                "sucesso": False,
                "mensagem": "Informe o nome do usuário."
            }

        if len(dados["nome"]) > 150:
            return {
                "sucesso": False,
                "mensagem": (
                    "O nome deve possuir no máximo 150 caracteres."
                )
            }

        if not dados.get("email"):
            return {
                "sucesso": False,
                "mensagem": "Informe o e-mail do usuário."
            }

        if len(dados["email"]) > 255:
            return {
                "sucesso": False,
                "mensagem": (
                    "O e-mail deve possuir no máximo 255 caracteres."
                )
            }

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            dados["email"]
        ):
            return {
                "sucesso": False,
                "mensagem": "Informe um endereço de e-mail válido."
            }

        perfil_novo = dados.get("perfil")

        if perfil_novo not in UsuarioService._perfis_disponiveis():
            return {
                "sucesso": False,
                "mensagem": (
                    "O perfil selecionado não está disponível "
                    "para o usuário logado."
                )
            }

        if perfil_logado == "SUPER_ADMIN":
            return UsuarioService._aplicar_vinculos_super_admin(
                dados
            )

        if perfil_logado == "ADM_ASSESSORIA":
            return UsuarioService._aplicar_vinculos_assessoria(
                dados
            )

        if perfil_logado == "ADMIN_EMPRESA":
            return UsuarioService._aplicar_vinculos_empresa(
                dados
            )

        return {
            "sucesso": False,
            "mensagem": (
                "Você não possui permissão para gerenciar usuários."
            )
        }

    # Mantido para compatibilidade com referências anteriores.
    @staticmethod
    def _validar_criacao_usuario(perfil_logado, dados):
        return UsuarioService._validar_dados_usuario(
            perfil_logado=perfil_logado,
            dados=dados
        )

    @staticmethod
    def _aplicar_vinculos_super_admin(dados):
        perfil_novo = dados.get("perfil")

        if perfil_novo == "SUPER_ADMIN":
            dados["empresa_id"] = None
            dados["assessoria_id"] = None

        elif perfil_novo == "ADM_ASSESSORIA":
            if not dados.get("assessoria_id"):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Informe a assessoria para o usuário."
                    )
                }

            dados["empresa_id"] = None

        else:
            if not dados.get("empresa_id"):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Informe a empresa para este perfil."
                    )
                }

            dados["assessoria_id"] = None

        return {"sucesso": True}

    @staticmethod
    def _aplicar_vinculos_assessoria(dados):
        if dados.get("perfil") not in {
            "ADMIN_EMPRESA",
            "GESTOR",
            "INVESTIGADOR",
            "VISUALIZADOR"
        }:
            return {
                "sucesso": False,
                "mensagem": (
                    "Perfil não permitido para ADM_ASSESSORIA."
                )
            }

        if not dados.get("empresa_id"):
            return {
                "sucesso": False,
                "mensagem": "Informe a empresa do usuário."
            }

        empresas_permitidas = (
            UsuarioService._empresas_da_assessoria_logada()
        )

        if dados["empresa_id"] not in empresas_permitidas:
            return {
                "sucesso": False,
                "mensagem": (
                    "A empresa selecionada não pertence "
                    "à assessoria logada."
                )
            }

        dados["assessoria_id"] = None
        return {"sucesso": True}

    @staticmethod
    def _aplicar_vinculos_empresa(dados):
        if dados.get("perfil") not in (
            UsuarioService.PERFIS_OPERACIONAIS
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Perfil não permitido para ADMIN_EMPRESA."
                )
            }

        empresa_id = ContextService.empresa()

        if not empresa_id:
            return {
                "sucesso": False,
                "mensagem": (
                    "Nenhuma empresa ativa foi identificada."
                )
            }

        dados["empresa_id"] = empresa_id
        dados["assessoria_id"] = None

        return {"sucesso": True}

    @staticmethod
    def _validar_vinculos_no_banco(repo, dados):
        perfil = dados.get("perfil")

        if perfil == "SUPER_ADMIN":
            return {"sucesso": True}

        if perfil == "ADM_ASSESSORIA":
            assessoria = repo.buscar_assessoria_ativa(
                dados.get("assessoria_id")
            )

            if not assessoria:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A assessoria selecionada não existe "
                        "ou está inativa."
                    )
                }

            return {"sucesso": True}

        empresa = repo.buscar_empresa_ativa(
            dados.get("empresa_id")
        )

        if not empresa:
            return {
                "sucesso": False,
                "mensagem": (
                    "A empresa selecionada não existe "
                    "ou está inativa."
                )
            }

        if session.get("perfil") == "ADM_ASSESSORIA":
            assessoria_id = UsuarioService._normalizar_id(
                session.get("assessoria_id")
            )

            if not repo.empresa_pertence_assessoria(
                empresa_id=dados["empresa_id"],
                assessoria_id=assessoria_id
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "A empresa selecionada não pertence "
                        "à assessoria logada."
                    )
                }

        return {"sucesso": True}

    # =========================================================
    # SENHAS
    # =========================================================

    @staticmethod
    def validar_senha_forte(senha: str | None) -> dict:
        senha_normalizada = senha or ""

        if (
            len(senha_normalizada)
            < UsuarioService.TAMANHO_MINIMO_SENHA
        ):
            return {
                "sucesso": False,
                "mensagem": UsuarioService.MENSAGEM_SENHA_FORTE
            }

        if not re.search(r"[A-Z]", senha_normalizada):
            return {
                "sucesso": False,
                "mensagem": UsuarioService.MENSAGEM_SENHA_FORTE
            }

        if not re.search(r"[a-z]", senha_normalizada):
            return {
                "sucesso": False,
                "mensagem": UsuarioService.MENSAGEM_SENHA_FORTE
            }

        if not re.search(r"\d", senha_normalizada):
            return {
                "sucesso": False,
                "mensagem": UsuarioService.MENSAGEM_SENHA_FORTE
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
                "mensagem": UsuarioService.MENSAGEM_SENHA_FORTE
            }

        return {"sucesso": True}

    @staticmethod
    def alterar_senha_obrigatoria(
        usuario_id,
        nova_senha,
        confirmar_senha
    ):
        usuario_sessao_id = UsuarioService._normalizar_id(
            session.get("usuario_id")
        )

        usuario_id = UsuarioService._normalizar_id(
            usuario_id
        )

        if not usuario_sessao_id:
            return {
                "sucesso": False,
                "mensagem": (
                    "Sua sessão não foi identificada. "
                    "Faça login novamente."
                )
            }

        if not usuario_id:
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

        validacao = UsuarioService.validar_senha_forte(
            nova_senha
        )

        if not validacao["sucesso"]:
            return validacao

        repo = UsuarioRepository()

        try:
            dados_seguranca = repo.buscar_dados_seguranca(
                usuario_id
            )

            if not dados_seguranca:
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado."
                }

            if not dados_seguranca.get("ativo"):
                return {
                    "sucesso": False,
                    "mensagem": "Este usuário está inativo."
                }

            senha_atual_hash = dados_seguranca.get(
                "senha_hash"
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
                ).decode("utf-8")
            )

            atualizado = repo.atualizar_senha_definitiva(
                usuario_id=usuario_id,
                senha_hash=nova_senha_hash
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
                "mensagem": "Senha atualizada com sucesso."
            }

        finally:
            repo.close()

    @staticmethod
    def resetar_senha(usuario_id):
        usuario_id = UsuarioService._normalizar_id(
            usuario_id
        )

        if not usuario_id:
            return {
                "sucesso": False,
                "mensagem": "Usuário inválido."
            }

        repo = UsuarioRepository()

        try:
            usuario = repo.buscar_por_id_global(
                usuario_id
            )

            if not usuario:
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado."
                }

            usuario_sessao_id = UsuarioService._normalizar_id(
                session.get("usuario_id")
            )

            if usuario_id == usuario_sessao_id:
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

            perfil_logado = session.get("perfil")
            perfil_usuario = usuario.get("perfil")

            if (
                perfil_logado == "ADM_ASSESSORIA"
                and perfil_usuario
                in {
                    "SUPER_ADMIN",
                    "ADM_ASSESSORIA"
                }
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
                not in UsuarioService.PERFIS_OPERACIONAIS
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "O administrador da empresa não pode "
                        "redefinir a senha deste perfil."
                    )
                }

            senha_temporaria = (
                UsuarioService._gerar_senha_temporaria()
            )

            senha_hash = (
                bcrypt.generate_password_hash(
                    senha_temporaria
                ).decode("utf-8")
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
                    "usuario": usuario.get("nome"),
                    "email": usuario.get("email"),
                    "perfil": perfil_usuario
                },
                valor_novo={
                    "resetado_por": usuario_sessao_id,
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
    def _gerar_senha_temporaria(tamanho=10):
        try:
            tamanho = int(tamanho)
        except (TypeError, ValueError):
            tamanho = 10

        tamanho_final = max(
            tamanho,
            UsuarioService.TAMANHO_MINIMO_SENHA
        )

        caracteres_obrigatorios = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
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
            secrets.choice(conjunto_completo)
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

        return "".join(caracteres_senha)