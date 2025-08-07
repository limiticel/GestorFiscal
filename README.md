Sistema de Gestão de Estoque com Cálculo Tributário

Este é um sistema web desenvolvido em **Flask** com **MySQL**, projetado para gerenciamento de estoque, cadastro de produtos e geração de relatórios com base no regime tributário do usuário.

## 🚀 Funcionalidades

- **Login e Cadastro de Usuário**
  - Armazena credencial e senha com hash (bcrypt).
  - Permite definir o regime tributário do usuário (Simples Nacional, Lucro Presumido, Lucro Real).

- **Cadastro de Produtos**
  - Produtos associados ao ID do usuário logado.
  - Armazena NCM, CFOP, CST, alíquota, quantidade, custo e venda.

- **Busca e Listagem**
  - Filtro por nome e letra com resposta em tempo real (AJAX).
  - Página de listagem e edição de produtos.

- **Finalização de Venda**
  - Atualiza o estoque.
  - Gera histórico de venda por produto com data e impostos.

- **Relatórios**
  - Relatório detalhado por trimestre (IRPJ e CSLL).
  - Relatório mensal com cálculo de PIS e COFINS.
  - Valores formatados com moeda brasileira (R$).

- **Atualização de Produtos**
  - Interface para editar dados de produtos existentes.

## 🧱 Tecnologias Utilizadas

- **Backend**: Python + Flask
- **Banco de Dados**: MySQL (via PyMySQL)
- **Frontend**: HTML, CSS, JavaScript (AJAX)
- **Bibliotecas**
  - `werkzeug.security` (hash de senha)
  - `BeautifulSoup` (leitura dinâmica dos campos de formulário)
  - `locale` (formatação em R$)
  - `flask.session` (sessões por ID)

## ⚙️ Como Rodar o Projeto

### Pré-requisitos

- Python 3.10+
- MySQL Server
- Pipenv ou virtualenv recomendado

### Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/limiticel/GestorFiscal.git
   cd GestorFiscal
