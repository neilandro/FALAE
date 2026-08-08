/* ==========================================================
   FALAE

   Arquivo:
      site.js

   Domínio:
      Site Institucional

   Responsabilidade:
      Controlar as interações da Landing Page.

   Funcionalidades:
      - Menu responsivo
      - Fechamento por Escape
      - Fechamento ao clicar fora
      - Fechamento após selecionar um link
      - Estado visual da Navbar durante o scroll

   Sprint:
      20.1 — Produção Landing Page
========================================================== */

"use strict";


document.addEventListener("DOMContentLoaded", function () {

    const header = document.querySelector(
        "[data-site-header]"
    );

    const toggle = document.querySelector(
        "[data-navbar-toggle]"
    );

    const menu = document.querySelector(
        "[data-navbar-menu]"
    );

    const links = document.querySelectorAll(
        "[data-navbar-link]"
    );


    function atualizarEstadoHeader() {
        if (!header) {
            return;
        }

        header.classList.toggle(
            "is-scrolled",
            window.scrollY > 12
        );
    }


    function menuEstaAberto() {
        return Boolean(
            toggle
            && toggle.getAttribute("aria-expanded") === "true"
        );
    }


    function abrirMenu() {
        if (!toggle || !menu) {
            return;
        }

        toggle.setAttribute(
            "aria-expanded",
            "true"
        );

        toggle.setAttribute(
            "aria-label",
            "Fechar menu de navegação"
        );

        menu.classList.add(
            "is-open"
        );

        document.body.classList.add(
            "site-menu-open"
        );
    }


    function fecharMenu() {
        if (!toggle || !menu) {
            return;
        }

        toggle.setAttribute(
            "aria-expanded",
            "false"
        );

        toggle.setAttribute(
            "aria-label",
            "Abrir menu de navegação"
        );

        menu.classList.remove(
            "is-open"
        );

        document.body.classList.remove(
            "site-menu-open"
        );
    }


    function alternarMenu() {
        if (menuEstaAberto()) {
            fecharMenu();
            return;
        }

        abrirMenu();
    }


    if (toggle && menu) {

        toggle.addEventListener(
            "click",
            alternarMenu
        );

        links.forEach(function (link) {
            link.addEventListener(
                "click",
                fecharMenu
            );
        });

        document.addEventListener(
            "keydown",
            function (event) {
                if (
                    event.key === "Escape"
                    && menuEstaAberto()
                ) {
                    fecharMenu();
                    toggle.focus();
                }
            }
        );

        document.addEventListener(
            "click",
            function (event) {
                if (!menuEstaAberto()) {
                    return;
                }

                const alvoDentroDoMenu = (
                    menu.contains(event.target)
                    || toggle.contains(event.target)
                );

                if (!alvoDentroDoMenu) {
                    fecharMenu();
                }
            }
        );

        window.addEventListener(
            "resize",
            function () {
                if (window.innerWidth >= 992) {
                    fecharMenu();
                }
            }
        );
    }


    atualizarEstadoHeader();

    window.addEventListener(
        "scroll",
        atualizarEstadoHeader,
        {
            passive: true
        }
    );

});