document.addEventListener("DOMContentLoaded",()=>{
    const form = document.getElementById("formCliente");
    form.addEventListener('submit', async (e) =>{
        e.preventDefault();
        
        const nome = document.getElementById('nome').value;
        const email = document.getElementById('email').value;
        const cpf = document.getElementById('cpf').value;
        const data_nascimento = document.getElementById('data_nascimento').value;
        const endereco = document.getElementById('endereco').value;
        console.log ({nome, email,cpf,data_nascimento, endereco});
        const response = await fetch('/clientes',{
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({nome, email, cpf, data_nascimento, endereco})
        })


        const result = await response.json();
        alert(result.message || result.error);


        carregarClientes(); // Atualiza a tabela de clientes após o envio do formulário
        form.reset(); //Limpa o formulário
    })
    carregarClientes(); //Carrega os clientes ao abrir a
})


function carregarClientes(){
    fetch('/clientes/getClientes')
        .then(response => response.json())
        .then(clientes =>{
            const tabela = document.querySelector('#tabelaClientes tbody');
            tabela.innerHTML = ""; //Limpando a tabela 

            clientes.forEach(cliente =>{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${cliente.id}</td>
                    <td>${cliente.nome}</td>
                    <td>${cliente.email}</td>
                    <td>${cliente.cpf}</td>
                    <td>${cliente.data_nascimento}</td>
                    <td>${cliente.endereco}</td>
                    <td>
                        <button class="btn-editar" data-id="${cliente.id}">Editar</button>
                        <button class="btn-excluir" data-id="${cliente.id}">Excluir</button>
                    </td>
                    `;
                    tabela.appendChild(tr);
            });

            //Criando os eventos para os botões de editar e excluir
            document.querySelectorAll(".btn-excluir").forEach(button =>{
                button.addEventListener('click', async (e)=>{
                    const id = button.dataset.id;
                    if(confirm("Tem certeza que deseja excluir este cliente?")){
                        fetch(`/clientes/${id}`,{
                            method: 'DELETE'
                        }).then(res => res.json())
                          .then(data => {
                            alert(data.message || data.error);
                            carregarClientes();
                          });
                    };
                });
            }); 
            document.querySelectorAll(".btn-editar").forEach(button =>{
                button.addEventListener('click', async (e)=>{
                    const id = button.dataset.id;
                    alert("Funcionalidade de edição ainda não implementada.");
                })
            })

        })
        .catch(error => {
            console.error('Erro ao carregar clientes:', error);
        })
}