document.addEventListener("DOMContentLoaded", () => {
    carregarClientes(); // Carrega os clientes ao carregar a página.

    const form = document.getElementById("formCliente");
    const btnNovoCliente = document.getElementById("btnNovoCliente");
    const btnCancelarCliente = document.getElementById("cancelarCliente");

    // Exibe/oculta o formulário de cadastro ao clicar no botão "Novo Cliente"
    btnNovoCliente.addEventListener("click", () => {
        form.reset(); // Limpa os campos do formulário
        document.getElementById("idCliente").value = ""; // Limpa o ID do cliente para novo cadastro
        form.style.display = form.style.display === "none" ? "block" : "none"; // Alterna a visibilidade do formulário
    });

    // Cancela a ação e oculta o formulário ao clicar no botão "Cancelar"
    btnCancelarCliente.addEventListener("click", () => {
        form.style.display = "none"; // Oculta o formulário
    });

    // Submissão do formulário de cadastro (criar ou editar)
    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Evita o comportamento padrão de envio do formulário

        const btn = e.submitter; // Obtém o botão que foi clicado (Cadastrar Cliente)
        btn.disabled = true; // Desabilita o botão para evitar múltiplos envios
        btn.textContent = "Enviando..."; // Altera o texto do botão

        // Obtém os valores dos campos do formulário
        const idCliente = document.getElementById("idCliente").value;
        const nome = document.getElementById("nome").value.trim();
        const email = document.getElementById("email").value.trim();
        const cpf = document.getElementById("cpf").value.trim();
        const data_nascimento = document.getElementById("data_nascimento").value.trim();
        const endereco = document.getElementById("endereco").value.trim();

        // Validação simples para verificar se todos os campos foram preenchidos
        if (!nome || !email || !cpf || !data_nascimento || !endereco) {
            alert("Todos os campos são obrigatórios.");
            btn.disabled = false; // Habilita o botão novamente
            btn.textContent = "Cadastrar Cliente"; // Restaura o texto do botão
            return;
        }

        const payload = { nome, email, cpf, data_nascimento, endereco };

        // Determina a URL e o método HTTP dependendo se é um novo cliente ou uma edição
        const url = idCliente ? `/api/clientes/${idCliente}` : "/api/clientes";
        const method = idCliente ? "PUT" : "POST";

        try {
            // Envia a requisição para o servidor
            const response = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message || "Cliente salvo com sucesso!");
                form.reset(); // Limpa o formulário
                document.getElementById("idCliente").value = ""; // Limpa o ID
                form.style.display = "none"; // Oculta o formulário
                carregarClientes(); // Recarrega a lista de clientes
            } else {
                alert(result.error || "Erro ao salvar cliente.");
            }
        } catch (err) {
            console.error("Erro ao salvar cliente:", err);
        }

        btn.disabled = false; // Habilita o botão novamente
        btn.textContent = "Cadastrar Cliente"; // Restaura o texto do botão
    });
});

// Função para carregar clientes
function carregarClientes() {
    fetch("/api/clientes")  // Requisição para obter os clientes
        .then(res => res.json())  // Converte a resposta para JSON
        .then(clientes => {
            console.log("Clientes carregados:", clientes);
            const tbody = document.querySelector("#tabelaClientes tbody");
            tbody.innerHTML = "";  // Limpa a tabela antes de preenchê-la

            clientes.forEach(cliente => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td>${cliente.id}</td>
                    <td>${cliente.nome}</td>
                    <td>${cliente.email}</td>
                    <td>${cliente.cpf}</td>
                    <td>${new Date(cliente.data_nascimento).toLocaleDateString()}</td>
                    <td>${cliente.endereco}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editarCliente(${cliente.id})">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="excluirCliente(${cliente.id})">Excluir</button>
                    </td>
                `;

                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Erro ao carregar clientes:", err));
}

// Função para editar cliente
function editarCliente(id) {
    fetch(`/api/clientes/${id}`)
        .then(res => res.json())
        .then(cliente => {
            document.getElementById("idCliente").value = cliente.id;
            document.getElementById("nome").value = cliente.nome;
            document.getElementById("email").value = cliente.email;
            document.getElementById("cpf").value = cliente.cpf;
            document.getElementById("data_nascimento").value = cliente.data_nascimento;
            document.getElementById("endereco").value = cliente.endereco;

            // Exibe o formulário para edição
            const form = document.getElementById("formCliente");
            form.style.display = "block";
        })
        .catch(err => console.error("Erro ao carregar cliente para edição:", err));
}

// Função para excluir cliente
function excluirCliente(id) {
    if (confirm("Tem certeza que deseja excluir este cliente?")) {
        fetch(`/api/clientes/${id}`, { method: "DELETE" })
            .then(res => {
                if (!res.ok) throw new Error("Falha ao excluir.");
                return res.json();
            })
            .then(() => carregarClientes()) // Recarrega a lista de clientes
            .catch(err => console.error("Erro ao excluir cliente:", err));
    }
}
