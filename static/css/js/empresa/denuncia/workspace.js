document.addEventListener("DOMContentLoaded", function () {
    const botoes = document.querySelectorAll("[data-denuncia-tab]");
    const paineis = document.querySelectorAll("[data-denuncia-panel]");

    if (!botoes.length) {
        console.error("FALAE: nenhuma aba de denúncia encontrada.");
        return;
    }

    if (!paineis.length) {
        console.error("FALAE: nenhum painel de denúncia encontrado.");
        return;
    }

    function ativarAba(nomeAba) {
        botoes.forEach(function (botao) {
            const abaAtiva = botao.dataset.denunciaTab === nomeAba;

            botao.classList.toggle("ativa", abaAtiva);
            botao.setAttribute("aria-selected", abaAtiva ? "true" : "false");
        });

        paineis.forEach(function (painel) {
            const painelAtivo = painel.dataset.denunciaPanel === nomeAba;

            painel.classList.toggle("ativo", painelAtivo);
            painel.hidden = !painelAtivo;
        });

        sessionStorage.setItem(
            "falae-denuncia-aba-ativa",
            nomeAba
        );
    }

    botoes.forEach(function (botao) {
        botao.addEventListener("click", function () {
            const nomeAba = botao.dataset.denunciaTab;

            ativarAba(nomeAba);
        });
    });

    const abaSalva = sessionStorage.getItem(
        "falae-denuncia-aba-ativa"
    );

    const abaSalvaExiste = Array.from(botoes).some(function (botao) {
        return botao.dataset.denunciaTab === abaSalva;
    });

    const abaInicial = abaSalvaExiste
        ? abaSalva
        : botoes[0].dataset.denunciaTab;

    ativarAba(abaInicial);
});