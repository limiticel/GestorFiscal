from flask import Flask, render_template,request, redirect, url_for, jsonify, flash
from .utils import SystemUtils, DatabaseModules
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from datetime import datetime
from collections import defaultdict
import locale

sys_utils = SystemUtils() #classe de Utils, instancia um objeto da classe SystemUtils
db_utils = DatabaseModules() # instancia um objeto da classe DatabaseModules

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
def set_routes(app):

    @app.route("/", methods=["GET","POST"]) #decorador de rotas do flask

    def login():

        ''' 
        Login na sessão.

        - Recebe a credencial via POST.
        - Verifica as crendenciais (se existe ou não no banco de dados).
        - Armazena o id do usuario na sessão.
        - Direciona à pagina principal do app.

        '''
        try:
            if request.method == "POST":
                credential = request.form["credential"] #armazena o valor inserido na credentials 
                session["user_id"] = db_utils.get_data_register(credential) #configura o id do usario logado na sessão de acordo com a credencial

                if sys_utils.verify_credentials('system_app/templates/register.html'): #verifica se as credenciais existem no banco de dados
                    return redirect(url_for("main"))
        except Exception as error:
            flash("verifique os dados e tente novamente")#mensagem flash do flask
     
        return render_template("login.html")


    @app.route("/register", methods = ["GET","POST"])
    def register():
        '''
        registra um novo usuario no sistema.

        - Recebe parametros via POST.
        - Gera uma hash para senha do usuario.
        - Cadastra o usuario e hash de senha no banco de dados.
        - Cria uma tabela no banco de dados (produtcts ) de acordo com o ID gerado.
    
        '''

        if request.method == "POST":
            data_form = sys_utils.get_data_form("system_app/templates/register.html") #pega todos os dados do formulario
            original_password = data_form["password"] #senha sem hash
            if original_password:
                data_form["password"] = generate_password_hash(original_password)#gerador de hash

            db_utils.set_data_register(data_form) #cadastra o usuario de acordo com os dados do formulario


            #criando o banco de dados dos produtos de acordo com o id
            credential = request.form["credential"] #novamente pegando os dados do formulario
            id = db_utils.get_data_register(credential) #pegando o id da credencial 
            
            db_utils.create_table(id) #função que cria o banco de dados(users) de acordo como id 

        return render_template("register.html")
    
    @app.route("/main")
    def main():
        return render_template("main.html")
    
    @app.route("/search", methods=["POST", "GET"])
    def search():
        '''
        filtra produtos por letra ou pelo nome
        
        - Recebe parametros via POST
        - Busca dados no banco de acordo com parametros recebidos
        - Retorna dados (em JSON) à pagina 
        '''

       
        id = session.get("user_id")#recebe o id logado na sessão
        datadict = db_utils.get_informations(id) #pega as informações do banco de dados de acordo com o id logado

        text = request.json.get("texto", "").lower() #recebe o texto digitado na busca (com js)

        result = []

        for item in datadict:
            nome = item["name"]
            preco = item["sale"]
            if text in nome.lower():
                result.append({"name": nome, "sale": float(preco)})

        return jsonify(result) #devolve ao html o valor encontrado na busca


    @app.route("/products", methods=['GET','POST'])
    def products():

        '''
        lista de produtos
        - Recebe parametros via POST
        - Filtra os parametros no banco de dados
        - Retorna dados encontrados no banco de dados

        '''

        id=session.get('user_id')#recebe o id logado
        datadict = db_utils.get_informations(id)#recebe os dados do banco de dados de produtos
        datalist = []
        for i in range(len(datadict)):
            datalist.append(datadict[i]['name']) #cria uma lista com o nome dos produtos

        result = datalist

        if request.method == "POST":
            search = request.form.get("busca", "").lower() #rece o texto digitado na busca
            result = [p for p in datalist if search in p.lower()] #verfica se existe algum objeto no banco de dados que possua essas letras

        return render_template("products.html", result =  result)
    
    @app.route("/set_products", methods=['GET','POST'])
    def set_products():#edita produtos

        '''
        regsitra os produtos
        - Recebe parametros via POST.
        - Atualiza o banco de dados de acordo com os parametros.
        '''

        if request.method == 'POST':
            id=session.get("user_id") #recebe o id do usuario logado
            
            datadict = sys_utils.get_data_form("system_app/templates/set_products.html") #recebe todos os dados do fomulario do html
            datalist = list(datadict.keys())
            print(datadict['quantity'])
            db_utils.data_products_registration(datadict, id)#registra os produtos de acordo com o id

        return render_template("set_products.html")
    
    @app.route("/finalize", methods=["POST"])
    def finalize():#finalizar compras
        '''
        Finaliza a venda realizada pelo usuario.
        - Recebe a tabela do main.html como parametros.
        - Atualiza o banco de dados products { id do usuario logado}.

        '''
        data = request.get_json() #recebe os dados da tabela da venda
        id = session.get("user_id")#recebe o id logado na sessão
        datalist = {}
        for item in data:
            name=item
            quantity = data[item]
            datalist[f'{name}']=quantity
        
        datadict = db_utils.get_informations(id)#recebe informações do banco de dados dos produtos
        
        stock = {p["name"]: p for p in datadict}  # Dicionário para facilitar o acesso por nome do produto

        new_data = {}
        for item in datalist:
            new_data[item] = stock[item]["quantity"] - datalist[item] #adaptação para auxiliar na atualização do banco de dados

        data_list = []
        for item in datalist:
            data_list.append({"name": item, "quantity": stock[item]["quantity"]-datalist[item]}) 

        #atualiza o banco de dados com as novas quantidade
        for object in data_list:
            print(object["name"])
            db_utils.set_products(id,object) #edita(atualiza) os produtos 

        return redirect(url_for("main"))
    
    @app.route("/report",methods=["GET","POST"])
    def report():
        '''
       Gera o relatório da venda e atualiza o histórico no banco de dados.
        - Recebe itens e total na tabela via JSON.
        - Gera um recibo de venda para a pagina (report).
        - Atualiza o banco de dados history.
        '''

        id = session.get("user_id")#recebe o id logado no banco de dados
        data_db = db_utils.get_informations(id)#recebe os dados do banco de dados produtos
        datadict = {}
        pis=0
        cofins=0
        date = datetime.now().strftime("%d-%m-%Y") #recebe a data em tempo real

        db_utils.create_history(id)#cria o banco de dados de historico de venda caso não exista

        if request.method == "POST":
            data = request.get_json()#recebe os dados do html (via js) ao finalizar a compra attribuition
            itens = data.get("itens", []) 
            total = data.get("total", 0)
            total_web = 0
            for obj in data_db:
                for item in itens:
                    if item["nome"] in list(obj.values()):
                        datadict["data"] = date
                        datadict["name"] = obj["name"]
                        datadict["pis"]=obj["pis"]
                        datadict["cofins"]=obj["cofins"]
                        datadict["cost"] = obj["cost"]
                        datadict["sale"] = obj["sale"]
                        datadict["aliq"] = obj["tax_rate"]
                        datadict['total'] = item["total"]
                        total_web += item["total"]
                        datadict["quantity"] = item["quantidade"]
                        db_utils.update_history(id, datadict)# registra a venda no banco de dados de historico
                        
                        

            return render_template("report.html", itens=itens, total=total)
        

        return render_template("report.html", itens=[], total=0)
    
    @app.route("/update_products",methods=["GET",'POST'])
    def update_products():
        '''
        Atualiza os dados de um produto no banco de dados.

        - Recebe o nome do produto via query string (`?nome=Produto`).
        - Carrega os dados do produto para exibir no formulário.
        - Recebe os novos dados via POST e atualiza o banco de dados.
        '''
        name = request.args.get("nome")
        id = session.get("user_id")
        data = db_utils.get_specific(id,name, 'name')
        data=data[0]
        print(id)
        if request.method == "POST":
            datadict = sys_utils.get_data_form("system_app/templates/update_products.html")
            print(datadict)
            db_utils.update_product(id, datadict)
            return redirect(url_for("products"))

        return render_template("update_products.html", nome=name, db=data)
    
    @app.route("/history")
    def history():

        '''
        Pagina com historico de vendas e filtro por trimestre(IRPJ e CSLL) e mensal (PIS, COFINS)
        
        - Recebe dados do banco de dados
        - Realiza calculos de acordo com o regime tributario do usuario logado
        - Retorna um relatorio completo de vendas na pagina
        '''
        def format_brl(valor): #formata em moeda local os valores 
            return locale.currency(valor, grouping=True)
        
        id = session.get("user_id")
        user = db_utils.get_user_information(id) # recebe informações do usuario logado
        datadict = db_utils.get_table_history(id) # Recebe dados do banco history

        trimestre = request.args.get("trimestre")
        meses_por_trimestre = {
            "1": ["01", "02", "03"],  #datas dos impostos trimestrais (IRPJ, CSLL).
            "2": ["04", "05", "06"],
            "3": ["07", "08", "09"],
            "4": ["10", "11", "12"]
        }

        total = 0
        irpj = 0
        csll = 0
        das = 0
        datadict_filtrado = []

        # Relatório mensal de PIS e COFINS
        pis_mensal = defaultdict(float)
        cofins_mensal = defaultdict(float)

        for item in datadict:
            mes = item["data"][3:5]
            if not trimestre or mes in meses_por_trimestre.get(trimestre, []):
                datadict_filtrado.append(item)
                total += float(item["total"])
                pis_mensal[mes] += (float(item["pis"]) / 100) * float(item["total"])
                cofins_mensal[mes] += (float(item["cofins"]) / 100) * float(item["total"])
                
        if user[0]["tax_regim"] == "PRESUMIDO":
            irpj = (total * 0.08) * 0.15
            irpj += ((total * 0.08) - 60000) * 0.015 if (total * 0.08) > 60000 else 0
            csll = (total * 0.12) * 0.09

        if user[0]["tax_regim"] == "LUCRO REAL":
            irpj = (total * 0.15)
            irpj += ((total-60000)*0.1) if total > 60000 else 0
            csll = total * 0.09
        
        if user[0]["tax_regim"] == "SIMPLES NACIONAL":
            irpj = 0
            csll = 0
            das = total * 0.06
    
        return render_template(
            'history.html',
            user_regim = user[0]["tax_regim"],
            das = locale.currency(round(das, 2), grouping=True),
            datadict=datadict_filtrado,
            total=locale.currency(round(total, 2), grouping=True),
            irpj=locale.currency(round(irpj, 2), grouping= True), 
            csll=locale.currency(round(csll, 2), grouping=True),
            trimestre_selecionado=trimestre,
            pis_mensal=pis_mensal,
            cofins_mensal=cofins_mensal,
            format_brl = format_brl
        )