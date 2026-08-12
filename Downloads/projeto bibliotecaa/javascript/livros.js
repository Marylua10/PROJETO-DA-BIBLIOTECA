/* ===== Página de Livros - ToschiBook ===== */

const btnNovoLivro = document.getElementById("btnNovoLivro");
const buscaLivro = document.getElementById("buscaLivro");
const livrosCount = document.getElementById("livrosCount");
const livrosEmpty = document.getElementById("livrosEmpty");
const livrosTable = document.getElementById("livrosTable");
const livrosBody = document.getElementById("livrosBody");

const modalLivro = document.getElementById("modalLivro");
const modalTitulo = document.getElementById("modalTitulo");
const fecharModal = document.getElementById("fecharModal");
const cancelarModal = document.getElementById("cancelarModal");
const formLivro = document.getElementById("formLivro");
const livroIdInput = document.getElementById("livroId");
const tituloInput = document.getElementById("titulo");
const autorInput = document.getElementById("autor");
const anoInput = document.getElementById("ano");
const quantidadeInput = document.getElementById("quantidade");
const categoriaInput = document.getElementById("categoria");
const salvarLivro = document.getElementById("salvarLivro");

let livros = [];
let termoBusca = "";

async function buscar(url, opcoes) {
    const resposta = await fetch(apiUrl(url), opcoes);

    if (!resposta.ok) {
        const erro = await resposta.json().catch(() => ({}));
        throw new Error(erro.erro || `Erro ${resposta.status}`);
    }

    return resposta.json();
}

function abrirModal(livro = null) {
    modalTitulo.textContent = livro ? "Editar livro" : "Novo livro";
    livroIdInput.value = livro ? livro.id : "";

    tituloInput.value = livro ? livro.titulo : "";
    autorInput.value = livro ? livro.autor : "";
    anoInput.value = livro ? livro.ano ?? "" : "";
    quantidadeInput.value = livro ? livro.quantidade ?? 1 : 1;
    categoriaInput.value = livro ? livro.categoria ?? "" : "";

    modalLivro.hidden = false;
    tituloInput.focus();
}

function fecharModalLivro() {
    modalLivro.hidden = true;
    formLivro.reset();
}

function mostrarErro(mensagem) {
    livrosTable.hidden = true;

    livrosEmpty.hidden = false;
    livrosEmpty.innerHTML = "";

    const aviso = document.createElement("div");
    aviso.className = "load-error";
    aviso.textContent = mensagem;
    livrosEmpty.appendChild(aviso);
}

function renderizarLivros() {
    const filtrados = livros.filter((livro) => {
        if (!termoBusca) {
            return true;
        }

        const termo = termoBusca.toLowerCase();
        return (
            livro.titulo.toLowerCase().includes(termo) ||
            livro.autor.toLowerCase().includes(termo)
        );
    });

    livrosCount.textContent = `${filtrados.length} registro(s)`;

    const temLivros = filtrados.length > 0;
    livrosTable.hidden = !temLivros;
    livrosEmpty.hidden = temLivros;

    if (!temLivros) {
        livrosEmpty.innerHTML = "";
        const icone = document.createElement("span");
        icone.className = "empty-icon";
        icone.textContent = "📚";

        const texto = document.createElement("p");
        texto.textContent = termoBusca
            ? "Nenhum livro encontrado para esta busca."
            : "Nenhum livro cadastrado ainda.";

        livrosEmpty.append(icone, texto);
        return;
    }

    livrosBody.innerHTML = "";

    filtrados.forEach((livro) => {
        const linha = document.createElement("tr");

        const celulaTitulo = document.createElement("td");
        celulaTitulo.className = "book-title-cell";
        celulaTitulo.textContent = livro.titulo;

        const celulaAutor = document.createElement("td");
        celulaAutor.textContent = livro.autor;

        const celulaAno = document.createElement("td");
        celulaAno.className = "small-text";
        celulaAno.textContent = livro.ano ?? "—";

        const celulaCategoria = document.createElement("td");
        celulaCategoria.className = "small-text";
        celulaCategoria.textContent = livro.categoria || "—";

        const celulaQuantidade = document.createElement("td");
        celulaQuantidade.textContent = livro.quantidade ?? 1;

        const celulaAcoes = document.createElement("td");
        celulaAcoes.className = "table-actions";

        const btnEditar = document.createElement("button");
        btnEditar.type = "button";
        btnEditar.className = "btn btn-secondary btn-small";
        btnEditar.textContent = "Editar";
        btnEditar.addEventListener("click", () => abrirModal(livro));

        const btnExcluir = document.createElement("button");
        btnExcluir.type = "button";
        btnExcluir.className = "btn btn-danger btn-small";
        btnExcluir.textContent = "Excluir";
        btnExcluir.addEventListener("click", () => excluirLivro(livro));

        celulaAcoes.append(btnEditar, btnExcluir);
        linha.append(celulaTitulo, celulaAutor, celulaAno, celulaCategoria, celulaQuantidade, celulaAcoes);
        livrosBody.appendChild(linha);
    });
}

async function carregarLivros() {
    try {
        livros = await buscar("/api/livros");
        renderizarLivros();
    } catch (erro) {
        mostrarErro("Não foi possível carregar os livros. Verifique se o servidor está rodando.");
    }
}

async function excluirLivro(livro) {
    const confirmacao = confirm(`Excluir o livro "${livro.titulo}"?`);

    if (!confirmacao) {
        return;
    }

    try {
        await buscar(`/api/livros/${livro.id}`, { method: "DELETE" });
        await carregarLivros();
    } catch (erro) {
        alert(erro.message);
    }
}

async function salvarLivroHandler(event) {
    event.preventDefault();

    const dados = {
        titulo: tituloInput.value.trim(),
        autor: autorInput.value.trim(),
        ano: anoInput.value ? Number(anoInput.value) : null,
        quantidade: quantidadeInput.value ? Number(quantidadeInput.value) : 1,
        categoria: categoriaInput.value.trim()
    };

    if (!dados.titulo || !dados.autor) {
        alert("Título e autor são obrigatórios.");
        return;
    }

    const id = livroIdInput.value;

    salvarLivro.disabled = true;

    try {
        if (id) {
            await buscar(`/api/livros/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });
        } else {
            await buscar("/api/livros", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });
        }

        fecharModalLivro();
        await carregarLivros();
    } catch (erro) {
        alert(erro.message);
    } finally {
        salvarLivro.disabled = false;
    }
}

btnNovoLivro.addEventListener("click", () => abrirModal());
fecharModal.addEventListener("click", fecharModalLivro);
cancelarModal.addEventListener("click", fecharModalLivro);

modalLivro.addEventListener("click", (event) => {
    if (event.target === modalLivro) {
        fecharModalLivro();
    }
});

formLivro.addEventListener("submit", salvarLivroHandler);

buscaLivro.addEventListener("input", (event) => {
    termoBusca = event.target.value.trim();
    renderizarLivros();
});

carregarLivros();
