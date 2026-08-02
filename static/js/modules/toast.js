/*!
 * ==========================================================
 * FALAE Enterprise
 * Módulo: Toast
 * Versão: 1.0.0
 * ==========================================================
 */

(function (window, document) {
    "use strict";

    const DEFAULT_DURATION = 5000;

    const CONFIG = {
        success: {
            title: "Sucesso",
            icon: "circle-check"
        },
        error: {
            title: "Erro",
            icon: "circle-x"
        },
        danger: {
            title: "Erro",
            icon: "circle-x"
        },
        warning: {
            title: "Atenção",
            icon: "triangle-alert"
        },
        info: {
            title: "Informação",
            icon: "info"
        },
        message: {
            title: "Informação",
            icon: "info"
        }
    };

    function normalizeType(type) {
        const normalizedType = String(type || "info")
            .trim()
            .toLowerCase();

        return CONFIG[normalizedType]
            ? normalizedType
            : "info";
    }

    function getContainer() {
        let container = document.querySelector(
            ".toast-container"
        );

        if (container) {
            return container;
        }

        container = document.createElement("div");
        container.className = "toast-container";
        container.setAttribute(
            "aria-label",
            "Notificações do sistema"
        );

        document.body.appendChild(container);

        return container;
    }

    function refreshIcons() {
        if (
            window.Falae &&
            typeof window.Falae.icons === "function"
        ) {
            window.Falae.icons();
            return;
        }

        if (
            window.lucide &&
            typeof window.lucide.createIcons === "function"
        ) {
            window.lucide.createIcons();
        }
    }

    function removeToast(toast) {
        if (!toast || toast.dataset.removing === "true") {
            return;
        }

        toast.dataset.removing = "true";
        toast.classList.add("is-leaving");

        window.setTimeout(function () {
            toast.remove();
        }, 220);
    }

    function createToast(
        message,
        type = "info",
        options = {}
    ) {
        const normalizedType = normalizeType(type);
        const config = CONFIG[normalizedType];

        const title =
            options.title ||
            config.title;

        const duration = Number.isFinite(options.duration)
            ? options.duration
            : DEFAULT_DURATION;

        const toast = document.createElement("div");

        toast.className =
            `falae-toast falae-toast--${normalizedType}`;

        toast.setAttribute(
            "role",
            normalizedType === "error" ||
            normalizedType === "danger"
                ? "alert"
                : "status"
        );

        toast.setAttribute("aria-atomic", "true");

        const icon = document.createElement("span");
        icon.className = "falae-toast__icon";
        icon.setAttribute("aria-hidden", "true");

        const iconElement = document.createElement("i");
        iconElement.setAttribute(
            "data-lucide",
            config.icon
        );

        icon.appendChild(iconElement);

        const content = document.createElement("div");
        content.className = "falae-toast__content";

        const titleElement = document.createElement("p");
        titleElement.className = "falae-toast__title";
        titleElement.textContent = title;

        const messageElement = document.createElement("p");
        messageElement.className = "falae-toast__message";
        messageElement.textContent = String(message || "");

        content.appendChild(titleElement);
        content.appendChild(messageElement);

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "falae-toast__close";
        closeButton.setAttribute(
            "aria-label",
            "Fechar notificação"
        );

        const closeIcon = document.createElement("i");
        closeIcon.setAttribute("data-lucide", "x");

        closeButton.appendChild(closeIcon);

        closeButton.addEventListener("click", function () {
            removeToast(toast);
        });

        toast.appendChild(icon);
        toast.appendChild(content);
        toast.appendChild(closeButton);

        getContainer().appendChild(toast);

        refreshIcons();

        if (duration > 0) {
            window.setTimeout(function () {
                removeToast(toast);
            }, duration);
        }

        return toast;
    }

    function initializeFlashMessages() {
        const flashMessages = document.querySelectorAll(
            ".flash-message"
        );

        flashMessages.forEach(function (flashMessage) {
            const type =
                flashMessage.dataset.toastType ||
                extractFlashType(flashMessage);

            const message =
                flashMessage.textContent.trim();

            if (message) {
                createToast(message, type);
            }

            flashMessage.remove();
        });

        const flashContainer = document.querySelector(
            ".flash-container"
        );

        if (
            flashContainer &&
            !flashContainer.children.length
        ) {
            flashContainer.remove();
        }
    }

    function extractFlashType(element) {
        const typeClass = Array
            .from(element.classList)
            .find(function (className) {
                return className.startsWith("flash-") &&
                    className !== "flash-message";
            });

        if (!typeClass) {
            return "info";
        }

        return typeClass.replace("flash-", "");
    }

    const Toast = {
        init() {
            initializeFlashMessages();
        },

        show(message, type = "info", options = {}) {
            return createToast(message, type, options);
        },

        success(message, options = {}) {
            return createToast(
                message,
                "success",
                options
            );
        },

        error(message, options = {}) {
            return createToast(
                message,
                "error",
                options
            );
        },

        warning(message, options = {}) {
            return createToast(
                message,
                "warning",
                options
            );
        },

        info(message, options = {}) {
            return createToast(
                message,
                "info",
                options
            );
        }
    };

    window.FalaeToast = Toast;

})(window, document);