/*!
 * ==========================================================
 * FALAE Enterprise
 * Módulo: ViaCEP
 * Versão: 1.0.0
 * ==========================================================
 */

(function (window, document) {
    "use strict";

    const VIA_CEP_URL = "https://viacep.com.br/ws";
    const TIMEOUT_CONSULTA = 8000;

    function somenteNumeros(valor) {
        if (
            window.FalaeMasks &&
            typeof window.FalaeMasks.somenteNumeros === "function"
        ) {
            return window.FalaeMasks.somenteNumeros(valor);
        }

        return String(valor || "").replace(/\D/g, "");
    }

    function cepValido(valor) {
        return /^\d{8}$/.test(
            somenteNumeros(valor)
        );
    }

    function obterElemento(seletor, contexto) {
        if (!seletor) {
            return null;
        }

        try {
            return contexto.querySelector(seletor);
        } catch (erro) {
            console.error(
                "FALAE: seletor inválido no ViaCEP.",
                seletor,
                erro
            );

            return null;
        }
    }

    function obterContexto(campoCep) {
        return campoCep.closest("form") || document;
    }

    function obterCampos(campoCep) {
        const contexto = obterContexto(campoCep);

        return {
            endereco: obterElemento(
                campoCep.dataset.viacepEndereco || "#endereco",
                contexto
            ),

            bairro: obterElemento(
                campoCep.dataset.viacepBairro || "#bairro",
                contexto
            ),

            cidade: obterElemento(
                campoCep.dataset.viacepCidade || "#cidade",
                contexto
            ),

            estado: obterElemento(
                campoCep.dataset.viacepEstado || "#estado",
                contexto
            ),

            numero: obterElemento(
                campoCep.dataset.viacepNumero || "#numero",
                contexto
            ),

            feedback: obterElemento(
                campoCep.dataset.viacepFeedback || "#cep-feedback",
                contexto
            )
        };
    }

    function definirFeedback(
        elemento,
        mensagem,
        tipo
    ) {
        if (!elemento) {
            return;
        }

        elemento.textContent = mensagem || "";

        elemento.classList.remove(
            "feedback-success",
            "feedback-error",
            "feedback-info"
        );

        if (tipo) {
            elemento.classList.add(
                `feedback-${tipo}`
            );
        }
    }

    function dispararEvento(campo, nomeEvento) {
        if (!campo) {
            return;
        }

        campo.dispatchEvent(
            new Event(
                nomeEvento,
                {
                    bubbles: true
                }
            )
        );
    }

    function preencherCampo(campo, valor) {
        if (!campo) {
            return;
        }

        campo.value = valor || "";

        dispararEvento(
            campo,
            "input"
        );

        dispararEvento(
            campo,
            "change"
        );
    }

    function preencherEndereco(campos, dados) {
        preencherCampo(
            campos.endereco,
            dados.logradouro
        );

        preencherCampo(
            campos.bairro,
            dados.bairro
        );

        preencherCampo(
            campos.cidade,
            dados.localidade
        );

        preencherCampo(
            campos.estado,
            dados.uf
        );
    }

    function definirEstadoConsulta(
        campoCep,
        consultando
    ) {
        if (consultando) {
            campoCep.setAttribute(
                "aria-busy",
                "true"
            );

            campoCep.classList.add(
                "is-consulting"
            );

            return;
        }

        campoCep.removeAttribute(
            "aria-busy"
        );

        campoCep.classList.remove(
            "is-consulting"
        );
    }

    async function buscarCep(
        cep,
        signal
    ) {
        const resposta = await fetch(
            `${VIA_CEP_URL}/${cep}/json/`,
            {
                method: "GET",

                headers: {
                    "Accept": "application/json"
                },

                signal
            }
        );

        if (!resposta.ok) {
            throw new Error(
                `ViaCEP retornou HTTP ${resposta.status}.`
            );
        }

        return resposta.json();
    }

    function cancelarConsultaAnterior(campoCep) {
        if (!campoCep._falaeViaCepController) {
            return;
        }

        campoCep._falaeViaCepController.abort();
        campoCep._falaeViaCepController = null;
    }

    async function consultarCampo(campoCep) {
        if (!campoCep) {
            return null;
        }

        const cep = somenteNumeros(
            campoCep.value
        );

        const campos = obterCampos(
            campoCep
        );

        if (!cep) {
            definirFeedback(
                campos.feedback,
                "",
                ""
            );

            return null;
        }

        if (!cepValido(cep)) {
            definirFeedback(
                campos.feedback,
                "Informe um CEP válido com 8 números.",
                "error"
            );

            return null;
        }

        if (
            campoCep.dataset.ultimoCep === cep &&
            campoCep.dataset.ultimoCepStatus === "success"
        ) {
            return null;
        }

        cancelarConsultaAnterior(
            campoCep
        );

        const controller =
            new AbortController();

        campoCep._falaeViaCepController =
            controller;

        const timeoutId = window.setTimeout(
            function () {
                controller.abort();
            },
            TIMEOUT_CONSULTA
        );

        definirEstadoConsulta(
            campoCep,
            true
        );

        definirFeedback(
            campos.feedback,
            "Consultando CEP...",
            "info"
        );

        try {
            const dados = await buscarCep(
                cep,
                controller.signal
            );

            if (dados.erro) {
                campoCep.dataset.ultimoCep =
                    cep;

                campoCep.dataset.ultimoCepStatus =
                    "not-found";

                definirFeedback(
                    campos.feedback,
                    "CEP não encontrado.",
                    "error"
                );

                return null;
            }

            preencherEndereco(
                campos,
                dados
            );

            campoCep.dataset.ultimoCep =
                cep;

            campoCep.dataset.ultimoCepStatus =
                "success";

            definirFeedback(
                campos.feedback,
                "Endereço localizado.",
                "success"
            );

            if (campos.numero) {
                campos.numero.focus();
            }

            return dados;

        } catch (erro) {
            campoCep.dataset.ultimoCep = "";
            campoCep.dataset.ultimoCepStatus = "";

            if (erro.name === "AbortError") {
                definirFeedback(
                    campos.feedback,
                    "A consulta demorou mais que o esperado. Preencha o endereço manualmente.",
                    "error"
                );

                return null;
            }

            console.error(
                "FALAE: erro ao consultar o ViaCEP.",
                {
                    nome: erro.name,
                    mensagem: erro.message,
                    stack: erro.stack
                }
            );

            definirFeedback(
                campos.feedback,
                "Não foi possível consultar o CEP. Preencha o endereço manualmente.",
                "error"
            );

            return null;

        } finally {
            window.clearTimeout(
                timeoutId
            );

            definirEstadoConsulta(
                campoCep,
                false
            );

            if (
                campoCep._falaeViaCepController ===
                controller
            ) {
                campoCep._falaeViaCepController = null;
            }
        }
    }

    function limparConsultaAnterior(
        campoCep
    ) {
        const cepAtual = somenteNumeros(
            campoCep.value
        );

        if (
            campoCep.dataset.ultimoCep &&
            campoCep.dataset.ultimoCep !== cepAtual
        ) {
            campoCep.dataset.ultimoCep = "";
            campoCep.dataset.ultimoCepStatus = "";
        }

        if (!cepAtual) {
            const campos = obterCampos(
                campoCep
            );

            definirFeedback(
                campos.feedback,
                "",
                ""
            );
        }
    }

    function configurarCampo(campoCep) {
        if (
            campoCep.dataset.viacepInitialized ===
            "true"
        ) {
            return;
        }

        campoCep.dataset.viacepInitialized =
            "true";

        campoCep.addEventListener(
            "input",
            function () {
                limparConsultaAnterior(
                    campoCep
                );
            }
        );

        campoCep.addEventListener(
            "blur",
            function () {
                consultarCampo(
                    campoCep
                );
            }
        );
    }

    function inicializar(
        contexto = document
    ) {
        contexto
            .querySelectorAll("[data-viacep]")
            .forEach(configurarCampo);
    }

    const ViaCep = {
        init(contexto = document) {
            inicializar(contexto);
        },

        consultar(campoOuSeletor) {
            let campoCep = campoOuSeletor;

            if (
                typeof campoOuSeletor ===
                "string"
            ) {
                campoCep = document.querySelector(
                    campoOuSeletor
                );
            }

            return consultarCampo(
                campoCep
            );
        },

        validar: cepValido
    };

    window.FalaeViaCep = ViaCep;

})(window, document);