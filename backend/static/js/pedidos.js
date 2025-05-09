document.addEventListener("DOMContentLoaded",()=>{
    carregarPedidos(); // Carrega todos os pedidos ao abrir a página


    document.getElementById("formPedido").addEventListener('submit', async (e) =>{
        e.preventDefault();

        const cliente_id = document.getElementById('cliente_id').value;
        const itens = Array.from(document.querySelectorAll('.item')).map( div=>({
            descricao_item: div.querySelector(".descricao_item").value,
            quantidade: div.parseInt(div.querySelector(".quantidade").value),
            preco_unitario: div.parseFloat(div.querySelector(".preco_unitario").value)
        }));
    
        const response = await fetch('/pedidos',{
            method: 'POST',
            headers:{'Content-Type': 'application/json'},
            body: JSON.stringify({cliente_id, itens})
        });
    
        const result = await response.json();
        alert(result.message || result.error);
        carregarPedidos(); // Atualizando a tabela de pedidos após o envio do formulario
    });

});


function carregarPedidos(){
    fetch('/pedidos')
        .then(response => response.json())
        .then(pedidos =>{
            const tbody = document.querySelector('#tabelaPedidos tbody');
            tbody.innerHTML = ""; // Limpando a tabela

            pedidos.forEach(pedido =>{
                const tr = document.createElement('tr');
                const itensHTML = pedido.itens.map(item=>`
                    ${item.descricao_item} - (${item.quantidade}) - R$ ${item.preco_unitario.toFixed(2)}
                    `).join("<br>");

                tr.innerHTML = `
                    <td>${pedido.id}</td>
                    <td>${pedido.cliente}</td>
                    <td>${new Date(pedido.data_pedido).toLocaleDateString()}</td>
                    <td>R$ ${pedido.valor_total.toFixed(2)}</td>
                    <td>${itensHTML}</td>
                    <td>
                        <button onclick="excluirPedido(${pedido.id})">Excluir</button>
                        <button onclick="editarPedido(${pedido.id})">Editar</button>
                `;
                tbody.appendChild(tr);
            });
        }); 
    }

function excluirPedido(id){
    if(confirm("Tem certeza que deseja excluir este pedido?")){
        fetch(`/pedidos/${id}`,{method: 'DELETE',})
            .then(res => res.json())
            .then(data =>{
                alert(data.message || data.error);
                carregarPedidos(); // Aqui atualizamos a tabela de pedidos após a exclusão da mesma
            });
    }
}

function adicionarItem(){
    const div = document.createElement('div');
    div.classList.add('item');
    div.innerHTML = `
        <input type="text" placeholder="Descrição" class="descricao_item"> required><br>
        <input type="number" placeholder="Quantidade" class="quantidade"> required><br>
        <input type="number" placeholder="Preço Unitario" class="preco_unitario"> required> 

    `;
    document.getElementById("itensPedido").appendChild(div);
}


async function editarPedido(id){
    const response = await fetch(`/pedidos/${id}`);
    const pedido = await response.json();

    if ( pedido.error){
        alert(pedido.error);
        return;
    }

    document.getElementById('editarPedidoId').value = id;

    const container = document.getElementById('edit-itens-container');
    container.innerHTML = ""; // Limpa os itens existentes

    pedido.itens.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('item');
        div.innerHTML = `
            <input type="text" class="descricao_item" value="${item.descricao_item}" required>
            <input type="number" class="quantidade" value="${item.quantidade}" required>
            <input type="number" class="preco_unitario" value="${item.preco_unitario}" required>
        `;
        container.appendChild(div);
    })
    //Abrir o Modal 
    const modal = new bootstrap.Modal(document.getElementById('modalEditarPedido'));
    modal.show();
}

// Função para adicionar um novo item no modal de edição
function adicionarItemEdit() {
    const container = document.getElementById('edit-itens-container');
    const div = document.createElement('div');
    div.classList.add('item');
    div.innerHTML = `
        <input type="text" placeholder="Descrição" class="descricao_item" required>
        <input type="number" placeholder="Quantidade" class="quantidade" required>
        <input type="number" placeholder="Preço Unitário" class="preco_unitario" required>
    `;
    container.appendChild(div);
}

// Função para salvar a edição do pedido
async function salvarEdicaoPedido(){
    const pedidoId = document.getElementBy('editPedidoId').value;

    const itens = Array.from(document.querySelectorAll('#edit-itens-container .item')).map(div =>({
        descricao_item: div.querySelector('.descricao_item').value,
        quantidade: parseInt(div.querySelector('.quantidade').value),
        preco_unitario: parseFloat(div.querySelector('.preco_unitario').value)
    }));

    const response = await fetch(`/pedidos/${pedidoId}`,{
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({itens}),
    });

    const result = await response.json();
    alert(result.message || result.error);


    const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarPedido'));
    modal.hide(); // Fecha o modal
    carregarPedidos(); // Atualiza a tabela de pedidos após a edição
}

