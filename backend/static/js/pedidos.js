// Quando o conteúdo da página for totalmente carregado
document.addEventListener("DOMContentLoaded", () => {
    carregarPedidos(); // Carrega todos os pedidos ao carregar a página

    const form = document.getElementById("formPedido"); // Obtém o formulário de pedidos

    // Exibe/oculta o formulário de criação de pedido ao clicar no botão "Novo Pedido"
    document.getElementById("btnNovoPedido").addEventListener("click", () => {
        form.reset(); // Limpa os campos do formulário
        document.getElementById("idPedido").value = ""; // Limpa o campo de ID (novo pedido)
        document.getElementById("itensPedido").innerHTML = ""; // Limpa os itens do pedido
        form.style.display = form.style.display === "none" ? "block" : "none"; // Alterna entre exibir ou ocultar o formulário
    });

    // Evento para submeter o formulário
    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Previne o envio padrão do formulário

        const btn = e.submitter; // Obtém o botão que enviou o formulário
        btn.disabled = true; // Desabilita o botão durante o envio
        btn.textContent = "Enviando..."; // Modifica o texto do botão

        // Obtém os dados do formulário
        const pedidoId = document.getElementById("idPedido").value; // ID do pedido (se estiver editando)
        const cliente_id = document.getElementById("cliente_id").value; // ID do cliente

        // Obtém os itens do pedido
        const itens = Array.from(document.querySelectorAll('#itensPedido .item')).map(div => {
            return {
                id: div.dataset.itemId || null, // Obtém o ID do item (se existir)
                descricao_item: div.querySelector(".descricao_item")?.value?.trim(), // Descrição do item
                quantidade: parseInt(div.querySelector(".quantidade")?.value), // Quantidade
                preco_unitario: parseFloat(div.querySelector(".preco_unitario")?.value) // Preço unitário
            };
        });

        // Valida os campos dos itens
        const camposInvalidos = itens.some(item =>
            !item.descricao_item || isNaN(item.quantidade) || item.quantidade <= 0 ||
            isNaN(item.preco_unitario) || item.preco_unitario <= 0
        );

        if (camposInvalidos) {
            alert("Preencha todos os campos corretamente."); // Exibe mensagem de erro se algum campo estiver inválido
            btn.disabled = false; // Habilita o botão novamente
            btn.textContent = "Enviar Pedido"; // Restaura o texto do botão
            return; // Interrompe a execução
        }

        // Prepara o payload para enviar
        const payload = { cliente_id, itens };
        const url = pedidoId ? `/api/pedidos/${pedidoId}` : "/api/pedidos"; // Define a URL dependendo se é um novo pedido ou edição
        const method = pedidoId ? "PUT" : "POST"; // Usa PUT para edição e POST para criação

        // Envia os dados para o backend
        const response = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload) // Envia o corpo como JSON
        });

        const result = await response.json(); // Converte a resposta para JSON

        // Verifica se o pedido foi salvo com sucesso
        if (response.ok) {
            alert(result.message || "Pedido salvo com sucesso!"); // Exibe mensagem de sucesso
            form.reset(); // Limpa o formulário
            document.getElementById("idPedido").value = ""; // Limpa o ID do pedido
            document.getElementById("itensPedido").innerHTML = ""; // Limpa os itens
            form.style.display = "none"; // Oculta o formulário
            carregarPedidos(); // Recarrega a lista de pedidos
        } else {
            alert(result.error || "Erro ao salvar o pedido."); // Exibe mensagem de erro
        }

        btn.disabled = false; // Habilita o botão novamente
        btn.textContent = "Enviar Pedido"; // Restaura o texto do botão
    });
});

// Função para carregar todos os pedidos
function carregarPedidos() {
    fetch("/api/pedidos") // Faz uma requisição para buscar os pedidos
        .then(res => res.json()) // Converte a resposta para JSON
        .then(pedidos => {
            const tbody = document.querySelector("#tabelaPedidos tbody"); // Obtém o corpo da tabela de pedidos
            tbody.innerHTML = ""; // Limpa a tabela antes de preencher

            pedidos.forEach(pedido => {
                const tr = document.createElement("tr"); // Cria uma nova linha na tabela

                // Garantir valores válidos para exibição
                const id = pedido.id || "";
                const cliente = pedido.cliente || "";
                const data = new Date(pedido.data_pedido).toLocaleDateString(); // Formata a data do pedido

                // Monta o HTML para exibir os itens do pedido
                const itensHTML = (pedido.itens || []).map(item => {
                    const preco = parseFloat(item.preco_unitario || 0);
                    return `<li>${item.quantidade}x ${item.descricao_item} - R$${preco.toFixed(2)}</li>`;
                }).join(''); // Cria uma lista de itens do pedido

                // Calcula o total do pedido
                const total = (pedido.itens || []).reduce((soma, item) => {
                    const preco = parseFloat(item.preco_unitario || 0);
                    const qtd = parseInt(item.quantidade || 0);
                    return soma + (qtd * preco); // Calcula a soma do preço total
                }, 0);

                // Cria a linha da tabela com os dados do pedido
                tr.innerHTML = `
                    <td>${id}</td>
                    <td>${cliente}</td>
                    <td>${data}</td>
                    <td>
                        <ul>
                            ${itensHTML}
                            <li><strong>Total: R$ ${total.toFixed(2)}</strong></li>
                        </ul>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-warning me-2" onclick="editarPedido(${id})">Editar</button>
                        <button class="btn btn-sm btn-danger" onclick="excluirPedido(${id})">Excluir</button>
                    </td>
                `;
                tbody.appendChild(tr); // Adiciona a linha na tabela
            });
        })
        .catch(err => console.error("Erro ao carregar pedidos:", err)); // Trata erros na requisição
}

// Função para editar um pedido
function editarPedido(id) {
    fetch(`/api/pedidos/${id}`) // Faz uma requisição para buscar o pedido pelo ID
        .then(res => res.json()) // Converte a resposta para JSON
        .then(pedido => {
            const form = document.getElementById("formPedido");
            document.getElementById("idPedido").value = pedido.id; // Preenche o ID do pedido
            document.getElementById("cliente_id").value = pedido.cliente_id; // Preenche o ID do cliente

            const container = document.getElementById("itensPedido");
            container.innerHTML = ""; // Limpa os itens do pedido no formulário

            // Adiciona os itens do pedido ao formulário
            (pedido.itens || []).forEach(item => adicionarItem(item));

            form.style.display = "block"; // Exibe o formulário de edição
        })
        .catch(err => console.error("Erro ao carregar pedido:", err)); // Trata erros na requisição
}

// Função para excluir um pedido
function excluirPedido(id) {
    if (confirm("Tem certeza que deseja excluir este pedido?")) { // Solicita confirmação do usuário
        fetch(`/api/pedidos/${id}`, { method: "DELETE" }) // Faz a requisição para excluir o pedido
            .then(res => {
                if (!res.ok) throw new Error("Falha ao excluir."); // Lança erro se a resposta não for OK
                return res.json(); // Converte a resposta para JSON
            })
            .then(() => carregarPedidos()) // Recarrega a lista de pedidos após a exclusão
            .catch(err => console.error("Erro ao excluir pedido:", err)); // Trata erros na requisição
    }
}

// Função para adicionar um item ao pedido
function adicionarItem(item = {}) {
    const container = document.getElementById("itensPedido");
    const div = document.createElement("div");
    div.classList.add("item", "mb-3"); // Adiciona classes de estilo

    if (item.id) div.dataset.itemId = item.id; // Define o ID do item (se existir)

    // Cria o HTML para o item do pedido
    div.innerHTML = `
        <input type="text" class="form-control mb-1 descricao_item" value="${item.descricao_item || ""}" placeholder="Nome do Item" required>
        <input type="number" class="form-control mb-1 quantidade" value="${item.quantidade || ""}" placeholder="Quantidade" required>
        <input type="number" class="form-control mb-1 preco_unitario" value="${item.preco_unitario || ""}" placeholder="Preço Unitário" step="0.01" required>
        <button type="button" class="btn btn-danger btn-sm mb-3" onclick="this.parentElement.remove()">Remover</button>
    `;

    container.appendChild(div); // Adiciona o item no container
}
