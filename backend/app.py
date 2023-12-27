from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)


cnx = mysql.connector.connect(user='potter2',
                              password='RemoteConnect',
                              host='ec2-52-53-124-242.us-west-1.compute.amazonaws.com',
                              port=3306,
                              database='PotteryInventory')


@app.route('/api/data/retrieve', methods=['POST', 'GET'])
def retrieve_data():
    try:
        crsr = cnx.cursor(dictionary=True)
        query = request.data.decode()
        query = eval(query)
        searchTerm = query['searchTerm']
        colName = query['colName']
        q = ""
        if (colName == 'Item_ID') or (colName == 'Price'):
            q = "SELECT * FROM Inventory WHERE {} = {}".format(colName, searchTerm)
        else:
            q = "SELECT * FROM Inventory WHERE {} = {!r}".format(colName, searchTerm)
        print(q)
        crsr.execute(q)
        result_list = []
        for entry in crsr:
            result_list.append(entry)
            print(entry)
        j_res = jsonify(result_list)
        crsr.close()
        print("Query complete.")
        return j_res
    except mysql.connector.Error as err:
        err_str = "Something went wrong: {}".format(err)
        err_resp = {"err": True, "resp": err_str}
        return jsonify(err_resp)


@app.route('/api/data/create', methods=['POST', 'GET'])
def create_data():
    try:
        crsr = cnx.cursor(dictionary=True)
        query = request.data.decode()
        print(query)
        query = eval(query)
        print(query['Color'])
        q = ("INSERT INTO Inventory (Color, Type, Price, Description)"
             " VALUES ({!r}, {!r}, {!r}, {!r});").format(query['Color'], query['Type'], query['Price'],
                                                         query['Description'])
        print(q)
        crsr.execute(q)
        cnx.commit()
        crsr.execute("SELECT * FROM Inventory WHERE Item_ID = (SELECT LAST_INSERT_ID());")
        result_list = []
        for entry in crsr:
            result_list.append(entry)
            print(entry)
        j_res = jsonify(result_list)
        crsr.close()
        return j_res
    except mysql.connector.Error as err:
        err_str = "Something went wrong: {}".format(err)
        return jsonify(err_str)


if __name__ == '__main__':
    app.run(debug=True)
