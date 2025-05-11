document.addEventListener("DOMContentLoaded", () => {
    carregarPedidos(); // Carrega todos os pedidos ao abrir a página

    // Ação do formulário de criação de pedido
    document.getElementById("formPedido").addEventListener('submit', async (e) => {
        e.preventDefault();

        const btn = e.submitter;
        btn.disabled = true;
        btn.textContent = "Enviando...";

        const cliente_id = document.getElementById('cliente_id').value;

        const itemElements = document.querySelectorAll('#itensPedido .item');
        const itens = Array.from(itemElements).map(div => {
            const descricao = div.querySelector(".descricao_item")?.value?.trim() || "";
            const quantidade = parseInt(div.querySelector(".quantidade")?.value);
            const preco = parseFloat(div.querySelector(".preco_unitario")?.value);

            return {
                descricao_item: descricao,
                quantidade,
                preco_unitario: preco
            };
        });

        const camposInvalidos = itens.some(item =>
            item.descricao_item === "" ||
            isNaN(item.quantidade) || item.quantidade <= 0 ||
            isNaN(item.preco_unitario) || item.preco_unitario <= 0
        );

        if (camposInvalidos) {
            alert("Preencha todos os campos corretamente.");
            btn.disabled = false;
            btn.textContent = "Enviar Pedido";
            return;
        }

        const response = await fetch('/pedidos/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cliente_id, itens })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            carregarPedidos(); // Atualiza a tabela após inserir
            document.getElementById("formPedido").reset(); // Limpa o formulário
            document.getElementById("itensPedido").innerHTML = ""; // Limpa os itens adicionados
        } else {
            alert(result.error || "Erro ao cadastrar Pedido");
        }

        btn.disabled = false;
        btn.textContent = "Enviar Pedido";
    });
});

// Função para carregar pedidos
function carregarPedidos(){
    fetch('/pedidos/listAll')
        .then(response => response.json())
        .then(pedidos => {
            console.log("Pedidos recebidos:", pedidos);
            const tbody = document.querySelector('#tabelaPedidos tbody');
            tbody.innerHTML = ""; // Limpa a tabela

            pedidos.forEach(pedido => {
                const tr = document.createElement('tr');
                const itensHTML = pedido.itens.map(item => `
                    ${item.descricao_item} - (${item.quantidade}) - R$ ${parseFloat(item.preco_unitario).toFixed(2)}
                `).join("<br>");

                tr.innerHTML = `
                    <td>${pedido.id}</td>
                    <td>${pedido.cliente || 'Cliente não encontrado'}</td>
                    <td>${new Date(pedido.data_pedido).toLocaleDateString()}</td>
                    <td>R$ ${parseFloat(pedido.valor_total).toFixed(2)}</td>
                    <td>${itensHTML}</td>
                    <td>
                        <button onclick="excluirPedido(${pedido.id})">Excluir</button>
                        <button onclick="editarPedido(${pedido.id})">Editar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar Pedidos:", error);
            alert("Erro ao carregar Pedidos. Tente novamente mais tarde.");
        });
}

// Função para excluir pedido
function excluirPedido(id){
    if (confirm("Tem certeza que deseja excluir este pedido?")) {
        fetch(`/pedidos/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                alert(data.message || data.error);
                carregarPedidos(); // Atualiza a tabela de pedidos após a exclusão
            });
    }
}

// Função para adicionar item ao pedido
function adicionarItem() {
    const div = document.createElement('div');
    div.classList.add('item');
    div.innerHTML = `
        <input type="text" class="form-control mb-1 descricao_item" placeholder="Descrição" required>
        <input type="number" class="form-control mb-1 quantidade" placeholder="Quantidade" required>
        <input type="number" class="form-control mb-1 preco_unitario" placeholder="Preço Unitário" required> 
        <button type="button" class="btn btn-danger btn-sm mb-3" onclick="removerItemSalvo(this)">Remover</button>
    `;

    // Adiciona ao container de itens dentro do modal
    const container = document.getElementById('edit-itens-container');
    if (container) {
        container.appendChild(div);
    } else {
        console.error("Container de itens no modal não encontrado.");
    }
}


// Função para editar pedido
function editarPedido(pedidoId) {
    fetch(`/pedidos/${pedidoId}`)
        .then(response => response.json())
        .then(pedido => {
            // Garantir que os elementos do formulário existem
            const idClienteElement = document.getElementById('idCliente');
            const idPedidoElement = document.getElementById('idPedido');

            if (idClienteElement && idPedidoElement) {
                idClienteElement.value = pedido.id_cliente;
                idPedidoElement.value = pedido.id;
            } else {
                console.error("Elementos para editar o pedido não encontrados.");
                alert("Elementos para editar o pedido não encontrados.");
                return; // Saia da função caso não encontre os elementos
            }

            // Limpa os itens anteriores
            const container = document.getElementById('edit-itens-container');
            if (container) {
                container.innerHTML = ''; // Limpa o conteúdo dos itens
            }

            // Abre o modal primeiro
            const modalElement = document.getElementById('pedidoModal');
            const modal = new bootstrap.Modal(modalElement);

            if (modalElement) {
                modal.show(); // Agora, mostramos o modal
            } else {
                console.error("Modal não encontrado.");
                alert("Erro ao abrir o modal.");
                return; // Evita erros se o modal não for encontrado
            }

            // Aguarda um pequeno delay para garantir que o DOM do modal foi renderizado
            setTimeout(() => {
                pedido.itens.forEach(item => {
                    const div = document.createElement('div');
                    div.classList.add('item');

                    if (item.id) {
                        div.setAttribute('data-item-id', item.id);
                    }

                    div.innerHTML = `
                        <input type="text" class="form-control mb-1 descricao_item" value="${item.descricao_item}" required>
                        <input type="number" class="form-control mb-1 quantidade" value="${item.quantidade}" required>
                        <input type="number" class="form-control mb-1 preco_unitario" value="${item.preco_unitario}" step="0.01" required>
                        <button type="button" class="btn btn-danger btn-sm mb-3" onclick="removerItemSalvo(this)">Remover</button>
                    `;

                    container.appendChild(div);
                });
            }, 100); // Pequeno delay para esperar o DOM do modal

        })
        .catch(error => {
            console.error('Erro ao buscar pedido:', error);
            alert('Erro ao carregar pedido.');
        });
}


// Função para remover item salvo
async function removerItemSalvo(botao) {
    const div = botao.closest('.item');
    const itemId = div.dataset.itemId;

    if (!itemId) {
        div.remove();
        return;
    }

    if (!confirm("Tem certeza que deseja remover este item do pedido?")) return;

    try {
        const response = await fetch(`/itens_pedido/${itemId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Erro HTTP: ${response.status} - ${text}`);
        }

        let result;
        try {
            result = await response.json();
        } catch (e) {
            result = { message: 'Item removido com sucesso.' };
        }

        alert(result.message);
        div.remove();
    } catch (e) {
        console.error("Erro ao remover item:", e);
        alert("Erro ao remover item: " + e.message);
    }
}

// Função para salvar as alterações no pedido
async function salvarEdicaoPedido() {
    const idPedido = document.getElementById('idPedido').value;
    const itens = [];

    const itemElements = document.querySelectorAll('#edit-itens-container .item');
    itemElements.forEach(itemElement => {
        const descricao_item = itemElement.querySelector('.descricao_item').value;
        const quantidade = itemElement.querySelector('.quantidade').value;
        const preco_unitario = itemElement.querySelector('.preco_unitario').value;

        if (descricao_item && quantidade && preco_unitario) {
            itens.push({
                descricao_item,
                quantidade,
                preco_unitario
            });
        }
    });

    const response = await fetch(`/pedidos/${idPedido}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ itens }) //  Removido id_cliente
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        carregarPedidos();
        const modalElement = document.getElementById('pedidoModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
    } else {
        alert(result.error || "Erro ao salvar alterações no pedido.");
    }
}


function adicionarNovoProduto() {
    const div = document.createElement('div');
    div.classList.add('item');
    div.innerHTML = `
        <input type="text" placeholder="Descrição" class="descricao_item" required>
        <input type="number" placeholder="Quantidade" class="quantidade" required>
        <input type="number" placeholder="Preço Unitário" class="preco_unitario" required> 
    `;
    document.getElementById("itensPedido").appendChild(div);
}

