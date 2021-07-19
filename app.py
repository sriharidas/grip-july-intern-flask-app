import mysql.connector
from flask import Flask,jsonify,request
import datetime

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

mydb = mysql.connector.connect(host="127.0.0.1", username="root", password="", port="3309", database="banking_system")



''' updating datetime  '''
# query = "update customers set acc_created = '" + str(timestamp)+"'"
# mydb_cursor.execute(query)
# mydb.commit()

# print(query)
mydb_cursor = mydb.cursor()
mydb_cursor.execute("USE banking_system")

@app.route('/customers')
def index():
    # mydb_cursor = mydb.cursor()
    # fetching column name
    mydb_cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'customers'")
    mydb_columns = mydb_cursor.fetchall()
    mydb_columns = [ list(x).pop() for x in mydb_columns ]
    mydb_cursor.execute("select * from customers")
    customers_db = mydb_cursor.fetchall()
    print(list(customers_db))
    return jsonify({
        "fields": mydb_columns
    })
@app.route('/view/customer', methods=["POST"])
def customer():
    cust = request.json['customer']
    print(cust)
   
    mydb_cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'customers'")
  
    mydb_columns = mydb_cursor.fetchall()
    mydb_columns = [ list(x).pop() for x in mydb_columns ]
    mydb_cursor.execute("SELECT * FROM customers WHERE cust_name = '" + str(cust) +"'" )
    customer_details = mydb_cursor.fetchall()
    return jsonify({
        "columns": mydb_columns ,
        "customer": customer_details
    })

@app.route('/transaction', methods=['POST'])
def transaction():
    trans_data = request.json['transaction']
    # mydb_cursor = mydb.cursor()
    mydb_cursor.execute("SELECT * FROM customers WHERE cust_name = '" + \
        trans_data['sender_username']+"' AND acc_no = "+ trans_data['sender_acc_no'])
    sender = mydb_cursor.fetchall()


    mydb_cursor.execute("SELECT * FROM customers WHERE cust_name = '" +\
        trans_data['reciever_username']+"' AND acc_no = "+ trans_data['reciever_acc_no'])
    reciever = mydb_cursor.fetchall()
    print("reciever", reciever)
    if len(reciever)>0:
        mydb_cursor.execute("SELECT balance FROM customers WHERE cust_name = '" +\
            trans_data['sender_username']+"' AND acc_no = "+ trans_data['sender_acc_no'])
        sender_balance = mydb_cursor.fetchall()
        sender_balance = int(list(sender_balance[0]).pop())
        mydb_cursor.execute("SELECT balance FROM customers WHERE cust_name = '" +\
            trans_data['reciever_username']+"' AND acc_no = "+ trans_data['reciever_acc_no'])
        reciever_balance = mydb_cursor.fetchall()
        reciever_balance = int(list(reciever_balance[0]).pop())
        if(sender_balance>int(trans_data['amount'])):
            mydb_cursor.execute("UPDATE customers SET balance = "+ str(sender_balance-int(trans_data['amount'])) +\
                 " WHERE cust_name = '" +trans_data['sender_username']+"' AND acc_no = "+ trans_data['sender_acc_no'] )
            mydb_cursor.execute("UPDATE customers SET balance = "+ str(reciever_balance+int(trans_data['amount'])) +\
                 " WHERE cust_name = '" +trans_data['reciever_username']+"' AND acc_no = "+ trans_data['reciever_acc_no'] )
            mydb.commit()
            query = "INSERT INTO transactions (sender_username, sender_acc_no, reciever_username, reciever_acc_no, amount) VALUES ('"+\
                 trans_data['sender_username'] +"', "+ trans_data['sender_acc_no'] + ", '"+ trans_data['reciever_username']+"', "+\
                     trans_data['reciever_acc_no'] +', '+ trans_data['amount']+ ")"
            # print(query)
            mydb_cursor.execute(query)
            mydb.commit()
        else:
            return "Not enough balance for the transaction"
        
        return "sucess"
    else:
        return "No match found"
  
@app.route('/view/transaction', methods=['POST'])
def history():
    user = request.json['customer']
    query = "SELECT * FROM transactions WHERE sender_acc_no = " + str(user['acc_no']) +\
         " OR reciever_acc_no = " + str(user['acc_no'])
    mydb_cursor.execute(query)
    trans_history = mydb_cursor.fetchall()
    # trans_history = [ str(list(x).pop()) for x in trans_history]
    print(trans_history)
    mydb_cursor.execute("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME= N'transactions'")
    trans_columns= mydb_cursor.fetchall()
    trans_columns = [ str(list(x).pop()) for x in trans_columns]

    if len(trans_history)>0:
        return jsonify({
            "columns": trans_columns,
            "transactions": trans_history
        })
    else:
        return "No Recent Transactions"

    print(query)
if __name__ == "__main__":
    app.run(debug=True)
