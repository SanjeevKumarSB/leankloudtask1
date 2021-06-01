from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
from flask_restplus import Resource, Api, reqparse
from functools import wraps

add=reqparse.RequestParser()
add.add_argument('taskname',type=str,required=True)
add.add_argument('status',type=str,choices=['Not started','In Progress','Finished'],required=True)
add.add_argument('duedate',type=str,required=True)

up=reqparse.RequestParser()
up.add_argument('taskname',type=str,required=True)
up.add_argument('status',type=str,choices=['Not started','In Progress','Finished'],required=True)

authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'name' : 'X-API-KEY'
    }
}


app=Flask(__name__)
api = Api(app,authorizations=authorizations)
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="root"
app.config["MYSQL_DB"]="leankloud"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql=MySQL(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return "ENTER THE TOKEN", 401

        if token != 'sanjeev':
            return "YOUR TOKEN IS WRONG.ENTER THE CORRECT TOKEN", 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated


@api.route("/display")
class Display(Resource):
    def get(self):
        con = mysql.connection.cursor()
        sql = "SELECT * FROM task"
        con.execute(sql)
        res = con.fetchall()
        return jsonify(res)


@api.route("/addtask")
class Addtask(Resource):
    @api.doc(security='apikey')
    @token_required

    @api.expect(add)
    def post(self):
            args=add.parse_args(request)
            taskname=args.get('taskname')
            date = args.get('duedate')
            status = args.get('status')
            con = mysql.connection.cursor()
            sql = "insert into task value (%s,%s,%s)"
            con.execute(sql, [taskname,status,date])
            mysql.connection.commit()
            con.close()
            return "TASK ADDED"




class Duedate(Resource):
    def get(self,duedate):
        con = mysql.connection.cursor()
        sql = "select * from task where duedate=%s"
        con.execute(sql, [duedate])
        res = con.fetchall()
        mysql.connection.commit()
        con.close()
        return jsonify(res)

class Overdue(Resource):
    def get(self):
        str='finished'
        con = mysql.connection.cursor()
        sql = "select * from task where duedate<CURDATE() AND statuss!=%s"
        con.execute(sql,[str])
        res = con.fetchall()
        mysql.connection.commit()
        con.close()
        return jsonify(res)

class Finished(Resource):
    def get(self):
        str='finished'
        con = mysql.connection.cursor()
        sql = "select * from task where statuss=%s"
        con.execute(sql,[str])
        res = con.fetchall()
        mysql.connection.commit()
        con.close()
        return jsonify(res)

class Update(Resource):
    @api.expect(up)
    @api.doc(security='apikey')
    @token_required

    def put(self):
        args = up.parse_args(request)
        taskname = args.get('taskname')
        status = args.get('status')
        con = mysql.connection.cursor()
        sql = "update task set statuss=%s where taskname=%s"
        con.execute(sql,[status,taskname])
        mysql.connection.commit()
        con.close()
        return "Task updated"




api.add_resource(Duedate,'/<string:duedate>')
api.add_resource(Overdue,'/overdue')
api.add_resource(Finished,'/finished')
api.add_resource(Update,'/update')


if(__name__=='__main__'):
    app.secret_key="abc123"
    app.run(debug=True)

