/* ===== Proteção de sessão e logout – ToschiBook ===== */

(function () {
    "use strict";

    const usuario = localStorage.getItem("toschibook_usuario");

    // Se não há sessão salva, redireciona para login
    if (!usuario) {
        window.location.href = "/html/index.html";
        return;
    }

    const dados = JSON.parse(usuario);

    // Preenche nome do usuário na sidebar (se existir o elemento)
    const adminNome = document.getElementById("adminNome");
    const adminAvatar = document.querySelector(".admin-avatar");

    if (adminNome) {
        adminNome.textContent = dados.nome || "Usuário";
    }

    if (adminAvatar && dados.nome) {
        adminAvatar.textContent = dados.nome.charAt(0).toUpperCase();
    }

    // Logout
    const logoutLink = document.getElementById("logoutLink");

    if (logoutLink) {
        logoutLink.addEventListener("click", async (event) => {
            event.preventDefault();

            try {
                await fetch("/api/auth/logout", { method: "POST" });
            } catch (_) {
                // Se falhar, limpa local mesmo assim
            }

            localStorage.removeItem("toschibook_usuario");
            window.location.href = "/html/index.html";
        });
    }
})();
