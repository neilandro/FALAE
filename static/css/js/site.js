<!-- ==========================================================
     FALAE

     Arquivo:
        navbar.html

     Componente:
        Navbar Institucional

     Responsabilidade:
        Disponibilizar a navegação principal do site e conduzir
        o visitante aos pontos de informação e conversão.

     Dependências:
        css/marketing/site-navbar.css
        css/marketing/site-buttons.css
        js/site.js

     Sprint:
        20.1 — Produção Landing Page
========================================================== -->

<header
    class="site-header"
    data-site-header
>
    <nav
        class="site-navbar"
        aria-label="Navegação principal"
    >
        <div class="site-container">

            <div class="site-navbar__content">

                <a
                    href="{{ url_for('public.home') }}"
                    class="site-navbar__brand"
                    aria-label="FALAE — Página inicial"
                >
                    <img
                        src="{{ url_for('static', filename='img/brand/logo.png') }}"
                        alt="FALAE"
                        class="site-navbar__logo"
                        width="132"
                        height="40"
                    >
                </a>

                <button
                    type="button"
                    class="site-navbar__toggle"
                    aria-label="Abrir menu de navegação"
                    aria-controls="site-navbar-menu"
                    aria-expanded="false"
                    data-navbar-toggle
                >
                    <span
                        class="site-navbar__toggle-line"
                        aria-hidden="true"
                    ></span>

                    <span
                        class="site-navbar__toggle-line"
                        aria-hidden="true"
                    ></span>

                    <span
                        class="site-navbar__toggle-line"
                        aria-hidden="true"
                    ></span>
                </button>

                <div
                    id="site-navbar-menu"
                    class="site-navbar__menu"
                    data-navbar-menu
                >
                    <ul
                        class="site-navbar__links"
                        role="list"
                    >
                        <li class="site-navbar__item">
                            <a
                                href="#plataforma"
                                class="site-navbar__link"
                                data-navbar-link
                            >
                                Plataforma
                            </a>
                        </li>

                        <li class="site-navbar__item">
                            <a
                                href="#como-funciona"
                                class="site-navbar__link"
                                data-navbar-link
                            >
                                Como funciona
                            </a>
                        </li>

                        <li class="site-navbar__item">
                            <a
                                href="#seguranca"
                                class="site-navbar__link"
                                data-navbar-link
                            >
                                Segurança
                            </a>
                        </li>

                        <li class="site-navbar__item">
                            <a
                                href="#contato"
                                class="site-navbar__link"
                                data-navbar-link
                            >
                                Contato
                            </a>
                        </li>
                    </ul>

                    <div class="site-navbar__actions">

                        <a
                            href="{{ url_for('auth.login') }}"
                            class="site-navbar__login"
                        >
                            Entrar
                        </a>

                        <a
                            href="#contato"
                            class="site-button site-button--primary site-navbar__cta"
                            data-navbar-link
                        >
                            Solicitar demonstração
                        </a>

                    </div>
                </div>

            </div>

        </div>
    </nav>
</header>