from falae.repositories.admin_dashboard_repository import AdminDashboardRepository


class AdminDashboardService:

    @staticmethod
    def obter_dashboard():
        repo = AdminDashboardRepository()

        try:
            total_assessorias = repo.total_assessorias()
            total_empresas = repo.total_empresas()
            total_usuarios = repo.total_usuarios()
            total_denuncias = repo.total_denuncias()
            total_denuncias_criticas = repo.total_denuncias_criticas()
            total_empresas_inativas = repo.total_empresas_inativas()
            total_assessorias_inativas = repo.total_assessorias_inativas()
            ultimas_assessorias = repo.ultimas_assessorias()
            ultimas_empresas = repo.ultimas_empresas()
            ultimos_usuarios = repo.ultimos_usuarios()
            empresas_sem_admin = repo.empresas_sem_admin()
            assessorias_sem_empresas = repo.assessorias_sem_empresas()
        finally:
            repo.close()

        return {
            "cards_principais": [
                {
                    "titulo": "Assessorias",
                    "valor": total_assessorias,
                    "descricao": "Assessorias ativas",
                    "icone": "🏥",
                    "classe": "metric-primary"
                },
                {
                    "titulo": "Empresas",
                    "valor": total_empresas,
                    "descricao": "Empresas ativas",
                    "icone": "🏢",
                    "classe": "metric-success"
                },
                {
                    "titulo": "Usuários",
                    "valor": total_usuarios,
                    "descricao": "Usuários ativos",
                    "icone": "👥",
                    "classe": "metric-warning"
                },
                {
                    "titulo": "Denúncias",
                    "valor": total_denuncias,
                    "descricao": "Registros na plataforma",
                    "icone": "📢",
                    "classe": "metric-danger"
                }
            ],

            "cards_alertas": [
                {
                    "titulo": "Denúncias críticas",
                    "valor": total_denuncias_criticas,
                    "descricao": "Críticas em aberto",
                    "icone": "🔴",
                    "classe": "metric-danger"
                },
                {
                    "titulo": "Empresas inativas",
                    "valor": total_empresas_inativas,
                    "descricao": "Empresas desativadas",
                    "icone": "⚠️",
                    "classe": "metric-warning"
                },
                {
                    "titulo": "Assessorias inativas",
                    "valor": total_assessorias_inativas,
                    "descricao": "Assessorias desativadas",
                    "icone": "⚪",
                    "classe": "metric-secondary"
                }
            ],

            "ultimas_assessorias": ultimas_assessorias,
            "ultimas_empresas": ultimas_empresas,
            "ultimos_usuarios": ultimos_usuarios,

            "acoes_rapidas": [
                {
                    "titulo": "Nova Assessoria",
                    "descricao": "Cadastrar uma nova assessoria.",
                    "icone": "🏥",
                    "url": "/admin/assessorias/nova"
                },
                {
                    "titulo": "Nova Empresa",
                    "descricao": "Cadastrar uma nova empresa.",
                    "icone": "🏢",
                    "url": "/admin/empresas/nova"
                },
                {
                    "titulo": "Usuários",
                    "descricao": "Gerenciar usuários da plataforma.",
                    "icone": "👥",
                    "url": "/admin/usuarios"
                },
                {
                    "titulo": "Empresas",
                    "descricao": "Visualizar empresas cadastradas.",
                    "icone": "📋",
                    "url": "/admin/empresas"
                }
            ],

            "alertas_plataforma": AdminDashboardService._montar_alertas_plataforma(
                empresas_sem_admin=empresas_sem_admin,
                assessorias_sem_empresas=assessorias_sem_empresas
            )
        }

    @staticmethod
    def _montar_alertas_plataforma(empresas_sem_admin, assessorias_sem_empresas):
        alertas = []

        for empresa in empresas_sem_admin:
            alertas.append({
                "icone": "🔴",
                "titulo": "Empresa sem administrador",
                "descricao": empresa["nome"],
                "url": f"/admin/usuarios/novo?empresa_id={empresa['id']}",
                "acao": "Criar ADMIN_EMPRESA"
                
            })

        for assessoria in assessorias_sem_empresas:
            alertas.append({
                "icone": "🟡",
                "titulo": "Assessoria sem empresas",
                "descricao": assessoria["nome"],
                "url": f"/admin/assessorias/{assessoria['id']}",
                "acao": "Ver assessoria"
            })

        return alertas