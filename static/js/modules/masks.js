/*!
 * ==========================================================
 * FALAE Enterprise
 * Módulo: Máscaras
 * Versão: 1.1.0
 *
 * Compatível com:
 * - CNPJ numérico existente
 * - CNPJ alfanumérico
 * - CEP
 * - UF
 * ==========================================================
 */

(function (window, document) {
    "use strict";

    function somenteNumeros(valor) {
        return String(valor || "").replace(/\D/g, "");
    }

    function somenteAlfanumericos(valor) {
        return String(valor || "")
            .replace(/[^a-zA-Z0-9]/g, "")
            .toUpperCase();
    }

    function aplicarMascaraCnpj(valor) {
        const caracteres = somenteAlfanumericos(valor)
            .slice(0, 14);

        let resultado = "";

        if (caracteres.length > 0) {
            resultado = caracteres.slice(0, 2);
        }

        if (caracteres.length > 2) {
            resultado += "." + caracteres.slice(2, 5);
        }

        if (caracteres.length > 5) {
            resultado += "." + caracteres.slice(5, 8);
        }

        if (caracteres.length > 8) {
            resultado += "/" + caracteres.slice(8, 12);
        }

        if (caracteres.length > 12) {
            resultado += "-" + caracteres.slice(12, 14);
        }

        return resultado;
    }

    function aplicarMascaraCep(valor) {
        const numeros = somenteNumeros(valor).slice(0, 8);

        return numeros.replace(
            /^(\d{5})(\d)/,
            "$1-$2"
        );
    }

    function aplicarMascaraUf(valor) {
        return String(valor || "")
            .replace(/[^a-zA-Z]/g, "")
            .toUpperCase()
            .slice(0, 2);
    }

    function obterValorCalculoDv(caractere) {
        return caractere.charCodeAt(0) - 48;
    }

    function calcularDigito(base, pesos) {
        let soma = 0;

        for (
            let indice = 0;
            indice < pesos.length;
            indice += 1
        ) {
            soma += (
                obterValorCalculoDv(base[indice]) *
                pesos[indice]
            );
        }

        const resto = soma % 11;

        return resto < 2
            ? 0
            : 11 - resto;
    }

    function cnpjValido(valor) {
        const cnpj = somenteAlfanumericos(valor);

        /*
         * Doze primeiras posições:
         * letras ou números.
         *
         * Duas últimas posições:
         * dígitos verificadores numéricos.
         */
        if (!/^[A-Z0-9]{12}\d{2}$/.test(cnpj)) {
            return false;
        }

        const base = cnpj.slice(0, 12);
        const digitosInformados = cnpj.slice(12, 14);

        const primeiroDigito = calcularDigito(
            base,
            [
                5, 4, 3, 2,
                9, 8, 7, 6,
                5, 4, 3, 2
            ]
        );

        const segundoDigito = calcularDigito(
            base + primeiroDigito,
            [
                6, 5, 4, 3, 2,
                9, 8, 7, 6,
                5, 4, 3, 2
            ]
        );

        return digitosInformados ===
            `${primeiroDigito}${segundoDigito}`;
    }

    function obterFormatador(tipoMascara) {
        const formatadores = {
            cnpj: aplicarMascaraCnpj,
            cep: aplicarMascaraCep,
            uf: aplicarMascaraUf
        };

        return formatadores[tipoMascara] || null;
    }

    function aplicarMascaraAoCampo(campo) {
        const tipoMascara = String(
            campo.dataset.mask || ""
        )
            .trim()
            .toLowerCase();

        const formatador = obterFormatador(
            tipoMascara
        );

        if (!formatador) {
            return;
        }

        campo.value = formatador(campo.value);
    }

    function configurarCampo(campo) {
        if (
            campo.dataset.maskInitialized ===
            "true"
        ) {
            return;
        }

        const tipoMascara = String(
            campo.dataset.mask || ""
        )
            .trim()
            .toLowerCase();

        const formatador = obterFormatador(
            tipoMascara
        );

        if (!formatador) {
            console.warn(
                "FALAE: máscara não reconhecida:",
                tipoMascara
            );

            return;
        }

        campo.dataset.maskInitialized = "true";

        campo.addEventListener(
            "input",
            function () {
                campo.value = formatador(
                    campo.value
                );
            }
        );

        aplicarMascaraAoCampo(campo);
    }

    function inicializar(contexto = document) {
        contexto
            .querySelectorAll("[data-mask]")
            .forEach(configurarCampo);
    }

    const Masks = {
        init(contexto = document) {
            inicializar(contexto);
        },

        somenteNumeros,

        somenteAlfanumericos,

        format: {
            cnpj: aplicarMascaraCnpj,
            cep: aplicarMascaraCep,
            uf: aplicarMascaraUf
        },

        validate: {
            cnpj: cnpjValido
        }
    };

    window.FalaeMasks = Masks;

})(window, document);