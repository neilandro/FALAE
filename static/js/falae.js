/*!
 * ==========================================================
 * FALAE Enterprise
 * Core Frontend Framework
 * Versão: 1.0.0
 * ==========================================================
 */

(function (window, document) {
    "use strict";

    const Falae = {

        version: "1.0.0",

        init() {

            this.console();

            this.csrf();

            this.icons();

            this.forms();

            this.loading();

            this.toast.init();

            if (
                window.FalaeMasks &&
                typeof window.FalaeMasks.init === "function"
            ) {
                window.FalaeMasks.init();
            }

            if (
                window.FalaeViaCep &&
                typeof window.FalaeViaCep.init === "function"
            ) {
                window.FalaeViaCep.init();
            }

        },

        console() {

            console.info(`
========================================================
 FALAE Enterprise
 Canal de Denúncias Corporativas

 Frontend : ${this.version}
 Status    : OK
========================================================
            `);

        },

        csrf() {

            const meta = document.querySelector(
                'meta[name="csrf-token"]'
            );

            if (!meta) {
                return;
            }

            const token = meta.content;

            document
                .querySelectorAll("form")
                .forEach(form => {

                    const method =
                        (form.method || "GET").toUpperCase();

                    if (method === "GET") {
                        return;
                    }

                    if (
                        form.querySelector(
                            'input[name="csrf_token"]'
                        )
                    ) {
                        return;
                    }

                    const input =
                        document.createElement("input");

                    input.type = "hidden";
                    input.name = "csrf_token";
                    input.value = token;

                    form.prepend(input);

                });

        },

        icons() {

            if (
                typeof lucide !== "undefined"
            ) {

                lucide.createIcons({

                    attrs: {

                        "aria-hidden": "true",

                        "focusable": "false"

                    }

                });

            }

        },

        forms() {

            document
                .querySelectorAll("form")
                .forEach(form => {

                    form.addEventListener(
                        "invalid",
                        event => {

                            event.target.classList.add(
                                "is-invalid"
                            );

                        },
                        true
                    );

                    form.addEventListener(
                        "input",
                        event => {

                            if (
                                event.target.matches(
                                    "input, select, textarea"
                                )
                            ) {
                                event.target.classList.remove(
                                    "is-invalid"
                                );
                            }

                        }
                    );

                });

        },

        loading() {

            document
                .querySelectorAll("form")
                .forEach(form => {

                    form.addEventListener("submit", event => {

                        if (form.dataset.submitting === "true") {
                            event.preventDefault();
                            return;
                        }

                        if (!form.checkValidity()) {
                            return;
                        }

                        const button = form.querySelector(
                            'button[type="submit"], input[type="submit"]'
                        );

                        if (!button) {
                            return;
                        }

                        form.dataset.submitting = "true";
                        form.classList.add("is-submitting");

                        button.disabled = true;
                        button.classList.add("is-loading");
                        button.setAttribute("aria-busy", "true");

                        if (button.tagName === "INPUT") {

                            if (!button.dataset.originalText) {
                                button.dataset.originalText = button.value;
                            }

                            button.value =
                                button.dataset.loading ||
                                "Salvando...";

                            return;
                        }

                        if (!button.dataset.originalText) {
                            button.dataset.originalText =
                                button.innerHTML;
                        }

                        const loadingText =
                            button.dataset.loading ||
                            "Salvando...";

                        button.innerHTML = `
                            <span
                                class="spinner"
                                aria-hidden="true"
                            ></span>
                            <span>${loadingText}</span>
                        `;

                    });

                });

        },

        toast: {

            init() {

                if (
                    window.FalaeToast &&
                    typeof window.FalaeToast.init === "function"
                ) {
                    window.FalaeToast.init();
                }

            },

            show(message, type = "info", options = {}) {

                if (!window.FalaeToast) {
                    console.log(message);
                    return null;
                }

                return window.FalaeToast.show(
                    message,
                    type,
                    options
                );

            },

            success(message, options = {}) {

                if (!window.FalaeToast) {
                    console.log(message);
                    return null;
                }

                return window.FalaeToast.success(
                    message,
                    options
                );

            },

            error(message, options = {}) {

                if (!window.FalaeToast) {
                    console.error(message);
                    return null;
                }

                return window.FalaeToast.error(
                    message,
                    options
                );

            },

            warning(message, options = {}) {

                if (!window.FalaeToast) {
                    console.warn(message);
                    return null;
                }

                return window.FalaeToast.warning(
                    message,
                    options
                );

            },

            info(message, options = {}) {

                if (!window.FalaeToast) {
                    console.info(message);
                    return null;
                }

                return window.FalaeToast.info(
                    message,
                    options
                );

            }

        },

        modal: {},

        utils: {}

    };

    window.Falae = Falae;

    document.addEventListener(
        "DOMContentLoaded",
        () => Falae.init()
    );

})(window, document);