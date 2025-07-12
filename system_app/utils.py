import pymysql
import pymysql.cursors
from bs4 import BeautifulSoup
from flask import request, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import locale

class DatabaseModules:
    def __init__(self):
        self.conn =  self.get_db_connection()
    
        with self.conn.cursor() as cursor:
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users(
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           credential VARCHAR(20) NOT NULL UNIQUE,
                           password TEXT NOT NULL,
                           tax_regim TEXT
                           )
                           ''')
            
            
        self.conn.commit()
        self.conn.close()


    def get_db_connection(self):
        conn = pymysql.connect(
            host = '127.0.0.1',
            user = 'root',
            password = "My$QLr00t@2025!",
            database = "ESTOQUE",
            port = 3306,
            cursorclass = pymysql.cursors.DictCursor
        )
    
        return conn
    
    def create_table(self, id):
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS products_{id}(
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            ncm INT NOT NULL UNIQUE,
                            name VARCHAR(20) NOT NULL UNIQUE,
                            cost DECIMAL(10,2) NOT NULL,
                            sale DECIMAL(10,2) NOT NULL,
                            cfop INT,
                            cst VARCHAR(20),
                            tax_rate INT,
                            quantity INT,
                            pis DECIMAL(10,2) NOT NULL,
                            cofins DECIMAL(10,2) NOT NULL
                            )
                
                ''')
        self.conn.commit()
        self.conn.close()

    def create_history(self, id):
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS history_{id}(
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            data TEXT NOT NULL,
                            name TEXT NOT NULL,
                            quantity INT NOT NULL,
                            sale DECIMAL(10,2),
                            cost DECIMAL(10,2) NOT NULL,
                            pis DECIMAL(10,2),
                            cofins DECIMAL(10,2),
                            aliq INT,
                            total DECIMAL(10,2)
                           )
                        ''')
            
    def update_history(self,id,datadict):
        self.conn = self.get_db_connection()

        with self.conn.cursor() as cursor:
            cursor.execute(f"INSERT INTO history_{id} (data, name, quantity , sale, cost, pis, cofins, aliq, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (datadict["data"],datadict["name"], datadict["quantity"],datadict['sale'],datadict['cost'],datadict["pis"],datadict["cofins"],datadict["aliq"], datadict["total"])
                           )
        self.conn.commit()
        self.conn.close()
    
    def get_table_history(self,id):
        data = []
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * from history_{id}")
            data = cursor.fetchall()

        self.conn.close()

        return data


    def set_data_register(self,dictdata):
        self.conn = self.get_db_connection()
        print(dictdata["tax_regim"])
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (credential,password,tax_regim) VALUES (%s, %s, %s)",
                    (dictdata['credential'],dictdata['password'],dictdata['tax_regim'])
                )
            self.conn.commit()
               
        except Exception as error:
            print("erro:", error)
            
        finally:
            self.conn.close()

    def set_products(self, id, data):
        self.conn = self.get_db_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"UPDATE products_{id} SET quantity = %s WHERE name = %s", (data["quantity"],data["name"]))
            self.conn.commit()
        except Exception as error:
            print(error)
        finally:
            self.conn.close()

    def set_federal_rate(self,id):
        self.conn = self.get_db_connection()
        tax_regim = ""
        pis = 0
        cofins = 0
        irpj = 0
        csll = 0
    
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT tax_regim FROM users WHERE id = %s", (id, ))
            tax_regim = cursor.fetchone()
        
        if str(tax_regim["tax_regim"]) == "PRESUMIDO":
            pis = 0.65
            cofins = 3
            irpj = 0.012
            csll = 0.0108
        if str(tax_regim["tax_regim"]) == "LUCRO REAL":
            pis = 1.65
            cofins = 7.6
            irpj = 0
            csll = 0
            
        
        return  pis, cofins, irpj, csll
    
    def get_data_register(self, datasearch):
        data = []
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE credential = %s", (datasearch, ))
            credential = cursor.fetchone()
            return credential['id']

        self.conn.close()
    
    def get_informations(self, id):
        data = []
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM products_{id}")
            data = cursor.fetchall()
        self.conn.close()
        return data

    def get_specific(self, id, data, field):
        newdt = []
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM products_{id} WHERE {field} = %s", (data))
            newdt = cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return newdt

    def data_products_registration(self,datadict, id):
        self.conn = self.get_db_connection()
        pis,cofins, irpj, csll = self.set_federal_rate(id)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO products_{id} (name, ncm, cost, sale, cst, cfop, tax_rate, quantity ,pis, cofins) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                               (datadict['name'], datadict['ncm'],datadict['cost'],datadict['sale'],datadict['cst'], datadict['cfop'],datadict['tax_rate'],datadict["quantity"],datadict["pis"],datadict["cofins"]))
            self.conn.commit()

        except Exception as error:
            print(error)

        finally:
            self.conn.close()

    def update_product(self,id,datadict={}):
        data = []
        self.conn = self.get_db_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                                f"""
                                UPDATE products_{id} 
                                SET ncm = %s, cost = %s, sale = %s, cst = %s, cfop = %s, tax_rate = %s, quantity = %s 
                                WHERE name = %s
                                """,
                                (
                                    datadict['ncm'],
                                    datadict['cost'],
                                    datadict['sale'],
                                    datadict['cst'],
                                    datadict['cfop'],
                                    datadict['tax_rate'],
                                    datadict['quantity'],
                                    datadict['name']  # Condição WHERE para identificar o registro
                                )
                            )
            self.conn.commit()
        except Exception as error:
            print(error)
        finally:
            self.conn.close()
            
    def get_user_information(self,id):
        data = []
        self.conn = self.get_db_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE id = %s",(id,))
            data = cursor.fetchall()
        self.conn.close()
        return data

class SystemUtils:
    def __init__(self):
        pass

    def extract_tags(self, template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        tags_with_name = soup.find_all(attrs={'name': True})

        names = [tag["name"] for tag in tags_with_name]

        return names

    def get_data_form(self, template):
        datalist = self.extract_tags(template)
        datadict = {}
        for object in datalist:
            if object not in("viewport"):
                datadict[object] = request.form.get(object)
        
        return datadict
    
    def verify_credentials(self, template):
        conn = DatabaseModules()
        conn = conn.get_db_connection()
        datadict = self.get_data_form(template)

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE credential = %s", (datadict["credential"], ))
            user = cursor.fetchone()
        
        if user and check_password_hash(user["password"], datadict["password"]):
           print("existe")
           return True
        print("nao existe")
        return False
    

    def format_brl(valor):
        return locale.currency(valor, grouping=True)