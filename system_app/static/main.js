function buscar() {
    /*
    Função responsável por buscar produtos com base no valor digitado no input com id "search".

    - Captura o texto digitado no campo de busca.
    - Envia esse texto via método POST para a rota "/search" (Flask), que consulta o banco de dados.
    - Recebe os resultados em JSON e atualiza o DOM com os itens encontrados.
    - Para cada item, cria um elemento <li> com um campo numérico de quantidade e um botão de adicionar.
    - Ao clicar no botão "+", o item é adicionado ao carrinho através da função adicionarAoCarrinho().
    */
    
    const texto = document.getElementById("search").value.trim();
    
    // limpa o campo caso nao há nada no input
    if (texto === "") {
        document.getElementById("results").innerHTML = "";
        return;
    }

    //Manda o texto adquirido no search do html para a rota /search que por sua vez é o decorador da função search em routes.py
    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }) //transforma o texto em string em Json
    })
    .then(response => response.json()) //retorna os itens buscados do banco de dados 
    .then(data => { //gera os itens de busca em uma lista suspensa juntamente com campos de quantidade e botao de adicionar
        const lista = document.getElementById("results"); 
        lista.innerHTML = "";

        if (data.length > 0) {
            data.forEach(item => {
                const li = document.createElement("li"); // cria uma lista
                const btn = document.createElement("button"); // cria um botao
                const input = document.createElement("input"); // cria um input

                input.type = "number"; // determina o tipo numero para o input
                input.min = 1; // valor minimo é 1
                input.value = 1; // começa com o valor 1
                btn.className = "to-add"; // adiciona uma classe para css
                btn.textContent = "+";// botao de adicionar mais

                li.textContent = item.name; // o nome do produto é atribuido a li
                li.appendChild(input); //adiciona a li o input definido
                li.appendChild(btn);//adiciona a li o botao de adicionar mais
                lista.appendChild(li);//adiciona a lista geral o li

                btn.addEventListener("click", function(e) { //configuração do evento de clique do botao de adicionar
                    e.stopPropagation(); //impede alterações diretas ao elemento pai.
                    const quantidade = parseInt(input.value) || 1; // transforma em inteiro ou em 1
                    adicionarAoCarrinho(item.name, quantidade, item.sale);
                });
            });
        } else {
            lista.innerHTML = "<li>Nenhum resultado</li>";
        }
    });
}



function adicionarAoCarrinho(nome, quantidade, precoUnitario) {
    /*
    Adiciona ao carrinho 
    - Recebe parametros passados aos inputs do produto selecionado.
    - Adiciona à lista de compras o produto selecionado.
    - Adiciona à frente do produto um botão de exclusão.
    */ 
    
    const shoppingList = document.getElementById("shopping-list"); //Definimos o elemento Pai aqui, irá receber os produtos

    const jaExiste = [...shoppingList.children].some(div => //verifica se os itens ja foram adicionados à lista
        div.getAttribute("data-nome") === nome
    );
    if (jaExiste) return;

    const total = (quantidade * precoUnitario).toFixed(2); 

    const div = document.createElement("div");
    div.className = "itens";

   
    div.setAttribute("data-nome", nome); 
    div.setAttribute("data-quantidade", quantidade);
    div.setAttribute("data-total", total);

    div.textContent = `${nome} - Quantidade: ${quantidade} - Total: R$ ${total} `;

    const btnExcluir = document.createElement("button"); // Botão de excluir
    btnExcluir.textContent = "❌";// Icone para o botao 
    btnExcluir.className = "remove-btn";// Classe do botao
    btnExcluir.style.marginLeft = "10px";

    btnExcluir.addEventListener("click", function () {
        shoppingList.removeChild(div); //Remove o item de acordo com o botão
        atualizarTotal(); 
    });

    div.appendChild(btnExcluir);
    shoppingList.appendChild(div);

    atualizarTotal();
}

function atualizarTotal() {
    /*
    Apenas atualiza o total do item adicionado (Singularmente por produto)
    */


    const shoppingList = document.getElementById("shopping-list");
    let total = 0;

    [...shoppingList.children].forEach(div => {
        // O texto está no formato: "nome - Quantidade: X - Total: R$ Y"
        // Vamos extrair o valor Y com regex
        const texto = div.textContent;
        const match = texto.match(/Total: R\$ ([\d,.]+)/);//Recebe os dados da string(recebe apenas o valor após o "Total")
        if (match && match[1]) {
            // Trocar vírgula por ponto se existir e converter pra número
            const valor = parseFloat(match[1].replace(',', '.'));
            if (!isNaN(valor)) {
                total += valor;
            }
        }
    });

    document.getElementById("total-compra").textContent = total.toFixed(2);
}



function complete_purchase(){

    /*
    Converte os dados e retorna em lista
    */

    let dictdata = {}
    const data = document.getElementById("shopping-list").children;

    [...data].forEach(e => {
    const text = e.textContent
    let quantity = text.match(/Quantidade:\s*(\d+)/)
    let name = text.match(/^(.*?)\s+-\s+Quantidade:/);
    quantity = parseInt(quantity[1])
    name = name[1].trim()

    dictdata[name]=quantity

});
    
    return dictdata
}


function attribution(){
    /*
    Passa os dados ao Backend (para salvar no banco de dados)
    */


    let dict = complete_purchase()

    fetch("/finalize",{ //função do backend que atualiza o banco de dados
        method : "POST",
        headers:{
            "Content-type" : "application/json"
        },

        body: JSON.stringify(dict) // passa ao backend os dados

    }).then(response => response.text())
    .then(data => {
        console.log('')
    })


   
    atualizarTotal();

    send_text()//função que manda o texto pro backend 
}


function send_text() {

    /*
    Envia o texto ao backend para gerar uma lista em outra pagina.

    */ 

    const divs = document.querySelectorAll(".itens");
    const texts = [];

    divs.forEach(div => {
        const nome = div.getAttribute("data-nome");
        const quantidade = parseInt(div.getAttribute("data-quantidade"));
        const total = parseFloat(div.getAttribute("data-total"));

        texts.push({ nome, quantidade, total });
    });

     const totalCompra = parseFloat(document.getElementById("total-compra").textContent);

    fetch("/report", { //função do backend que gera o relatorio após a venda ser finalizada
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ itens: texts, total: totalCompra })
    })
    .then(response => response.text())
    .then(data => {
        document.body.innerHTML = data;
    });
}
