from falae.repositories.denuncia_repository import DenunciaRepository


def test_repository_instancia():

    repo = DenunciaRepository()

    assert repo is not None

    repo.close()