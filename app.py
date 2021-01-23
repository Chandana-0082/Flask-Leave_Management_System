from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import logout_user
from flask_mysqldb import MySQL
import MySQLdb
from datetime import timedelta
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Hello admin"

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

app.config["MYSQL_HOST"]= "127.0.0.1"
app.config["MYSQL_USER"]= "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "leave_management_system"

db = MySQL(app)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/admin-login')
def admin_login():
    msg = ''
    return render_template('admin.html')

@app.route('/login')
def login():
    msg = ''
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/applyleave')
def applyleave():
    msg = ''
    return render_template('applyleave.html')

@app.route('/addemployee')
def addemployee():
    msg = ''
    return render_template('addemployee.html')

@app.route('/addleave')
def addleave():
    msg = ''
    return render_template('addleave.html')

@app.route('/adddepartment')
def adddepartment():
    msg = ''
    return render_template('adddepartment.html')

@app.route('/dash')
def dash():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT L.id,E.emp_id,L.emp_id,E.First_name,E.Last_name,L.leavetype,L.Status FROM employee_data E, leaves L WHERE E.emp_id=L.emp_id and L.Status="waiting for approval"')
        data = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM employee_data")
        total = cursor.fetchone()["COUNT(*)"]
        cursor.execute("SELECT SEC_TO_TIME(AVG(TIME_TO_SEC(TIMEDIFF(end_time,start_time)))) as average from timesheet")
        average = cursor.fetchone()["average"]
        return render_template("dash.html", data = data, total=total, average=average)
    return render_template('dash.html')

@app.route('/leavehistory')
def leavehistory():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT emp_id,leavetype,DATE_FORMAT(ToDate,'%%e/%%m/%%Y') as To_Date,DATE_FORMAT(FromDate,'%%e/%%m/%%Y') as From_Date,Description,Status,Posting_date FROM leaves WHERE emp_id=%s and Status in ('Approved','Rejected')", (session['emp_id'], ))
        account = cursor.fetchall()
        return render_template("leavehistory.html", account = account)

    return redirect(url_for('leavehistory'))

@app.route('/leavebalance')
def leavebalance():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT E.id,emp_id,L.leavetype,E.leavetype,no_of_leaves,datediff(ToDate,FromDate) as no_of_leaves_taken FROM  leaves L,leavety E WHERE emp_id=%s and L.leavetype=E.leavetype",(session['emp_id'], ))
        acc = cursor.fetchall()
        # cursor.execute("UPDATE ")
        # total = cursor.fetchone()
        return render_template("leave balance.html",acc=acc)

    return render_template("leave balance.html")

@app.route('/login_validation', methods = ['GET','POST'])
def login_validation():
    msg = ''
    if request.method == 'POST':
        if 'Email' in request.form and 'Password' in request.form:
            Email = request.form['Email']
            Password = request.form['Password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM employee_data WHERE Email=%s AND Password=%s",(Email,Password))
            info = cursor.fetchone()
            if info:
                session['loggedin'] = True
                session['emp_id'] = info['emp_id']
                session['Email'] = info['Email']
                msg = 'Logged in successfully !'
                return render_template('dashboard.html', msg=msg)
                session.permanent = True
            else:
                msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('Email',None)
    session.pop('loggedin',None)
    return render_template('login.html');

@app.route('/admin_validation', methods = ['POST'])
def admin_validation():
    msg = ''
    if request.method == 'POST':
        if 'Email' in request.form and 'Password' in request.form:
            Email = request.form['Email']
            Password = request.form['Password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM admin WHERE Email=%s AND Password=%s",(Email,Password))
            info = cursor.fetchone()
            if info:
                session['loggedin'] = True
                session['Email'] = info['Email']
                msg = 'Logged in successfully !'
                return render_template('admin_dashboard.html', msg=msg)
                session.permanent = True
            else:
                msg = 'Incorrect username / password !'

    return render_template('admin.html',msg=msg)

@app.route('/admin_logout')
def admin_logout():
        session.pop('Email', None)
        session.pop('loggedin', None)
        return redirect(url_for('admin_login'))

@app.route('/adduser', methods = ['GET','POST'])
def new_user():
    msg = ''
    if request.method == 'POST':
        if 'First_name' in request.form and 'Email' in request.form:
            First_name = request.form['First_name']
            Last_name = request.form['Last_name']
            Email = request.form['Email']
            Password = request.form['Password']
            Gender = request.form['Gender']
            Dob = request.form['Dob']
            Department = request.form['Department']
            City = request.form['City']
            Country = request.form['Country']
            Phone_number = request.form['Phone_number']
            Date_of_joining = request.form['Date_of_joining']
            Status = "Active"
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO leave_management_system.employee_data(First_name,Last_name,Email,Password,Gender,Dob,Department,City,Country,Phone_number,Status,Date_of_joining) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(First_name,Last_name,Email,Password,Gender,Dob,Department,City,Country,Phone_number,Status,Date_of_joining))
            db.connection.commit()

        msg = 'Employee added successfully !'
        return render_template('addemployee.html', msg=msg)

    return render_template('addemployee.html')

@app.route('/addleave', methods=['POST'])
def add_leave():
    msg = ''
    if request.method == 'POST':
        if 'leavetype' in request.form:
            leavetype = request.form['leavetype']
            Description = request.form['Description']
            no_of_leaves = request.form['no_of_leaves']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO leave_management_system.leavety(leavetype,Description,no_of_leaves) VALUES (%s,%s,%s)",(leavetype,Description,no_of_leaves))
            db.connection.commit()
        msg = 'Added successfully !'
        return render_template('addleave.html', msg=msg)

    return render_template('addleave.html')

@app.route('/adddepartment', methods=['POST'])
def add_department():
    msg = ''
    if request.method == 'POST':
        if 'Department' in request.form:
            Department = request.form['Department']
            Department_shortname = request.form['Department_shortname']
            Department_code = request.form['Department_code']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(" INSERT INTO leave_management_system.department(`Department`,`Department_shortname`,`Department_code`) VALUES (%s,%s,%s)",(Department,Department_shortname,Department_code))
            db.connection.commit()
        msg = 'Added successfully !'
        return render_template('adddepartment.html', msg=msg)

    return render_template('adddepartment.html')

@app.route('/apply', methods=['POST'])
def apply():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST'and 'leavetype' in request.form:
            leavetype = request.form['leavetype']
            ToDate = request.form['ToDate']
            FromDate = request.form['FromDate']
            Description = request.form['Description']
            Status = "waiting for approval"
            leave_balance = 0
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO leave_management_system.leaves(leavetype,ToDate,FromDate,Description,emp_id,Status,leave_balance) VALUES (%s,%s,%s,%s,%s,%s,%s)",(leavetype,ToDate,FromDate,Description,session['emp_id'],Status,leave_balance))
            db.connection.commit()
        msg = 'Applied successfully !'
        return render_template('applyleave.html', msg=msg)

    return render_template('applyleave.html')

@app.route("/profile", methods = ['GET'])
def profile():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM leave_management_system.employee_data WHERE emp_id = %s', (session['emp_id'], ))
        info = cursor.fetchone()
        return render_template("profile.html", info = info)
    return redirect(url_for('login'))

@app.route('/approve/<EmpId>/<Leavetype>')
def approve(EmpId,Leavetype):
    msg = ''
    if 'loggedin' in session:
        action = 'Approved'
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE leave_management_system.leaves SET Status=%s WHERE emp_id=%s and leavetype=%s',(action,EmpId,Leavetype, ))
        db.connection.commit()
        # cursor1 = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor1.execute('UPDATE leaves SET leave_balance=leave_balance-datediff(ToDate,FromDate) as no_of_leaves_taken WHERE emp_id=%s and leavetype=%s',(action, EmpId, Leavetype,))
        # db.connection.commit()
        return "Approved successfully"

    return render_template('dash.html', msg=msg)


@app.route('/rejected/<EmpId>/<Leavetype>')
def rejected(EmpId,Leavetype):
    if 'loggedin' in session:
        action = 'Rejected'
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE leave_management_system.leaves SET Status=%s WHERE emp_id=%s and leavetype=%s',(action,EmpId,Leavetype))
        db.connection.commit()
        return "rejected successfully"

    return render_template("dash.html")

@app.route('/leaveapproval')
def leaveapproval():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT emp_id,leavetype,DATE_FORMAT(FromDate,"%%e/%%m/%%Y") as From_Date,DATE_FORMAT(ToDate,"%%e/%%m/%%Y") as To_Date,Description,Status,Posting_date FROM leaves WHERE emp_id=%s and Status="waiting for approval"', (session['emp_id'], ))
        account1 = cursor.fetchall()
        return render_template("leave approval.html", account1 = account1)

    return redirect(url_for('leave approval'))

@app.route('/cancel/<EmpId>/<Leavetype>')
def cancel(EmpId,Leavetype):
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM leaves WHERE emp_id=%s and leavetype=%s and Status="waiting for approval"',(EmpId,Leavetype))
        db.connection.commit()
        return "deleted successfully"

    return render_template("leavehistory.html")

@app.route('/managedepartment')
def man_dep():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id,Department,Department_shortname,Department_code FROM department")
        dep = cursor.fetchall()
        return render_template("managedepartment.html", dep=dep)

    return render_template("managedepartment.html")

@app.route('/manageleave')
def man_lev():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id,leavetype,Description,no_of_leaves FROM leavety")
        lev = cursor.fetchall()
        return render_template("manageleave.html", lev=lev)

    return render_template("manageleave.html")

@app.route('/manageemployee')
def man_emp():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM employee_data")
        emp = cursor.fetchall()
        return render_template("manageemployee.html", emp=emp)

    return render_template("manageemployee.html")

@app.route('/lev_delete/<rowData>')
def lev_delete(rowData):
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM leavety WHERE id LIKE %s",[rowData])
        db.connection.commit()
        return "deleted successfully"

    return render_template("manageleave.html")

@app.route('/dep_delete/<rowData>')
def dep_delete(rowData):
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM department WHERE id LIKE %s",[rowData])
        db.connection.commit()
        return "deleted successfully"

    return render_template("manageleave.html")

@app.route('/allleaves')
def allleaves():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT L.id,E.emp_id,L.emp_id,E.First_name,E.Last_name,L.leavetype,L.Status FROM employee_data E, leaves L WHERE E.emp_id=L.emp_id")
        idata = cursor.fetchall()
        return render_template("allleaves.html", idata=idata)

    return render_template("allleaves.html")

@app.route('/pending')
def pending():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT L.id,E.emp_id,L.emp_id,E.First_name,E.Last_name,L.leavetype,L.Status FROM employee_data E, leaves L WHERE E.emp_id=L.emp_id AND L.Status="waiting for approval"')
        data3 = cursor.fetchall()
        return render_template("pending.html", data3=data3)

    return render_template("pending.html")

@app.route('/approved')
def approved():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT L.id,E.emp_id,L.emp_id,E.First_name,E.Last_name,L.leavetype,L.Status FROM employee_data E, leaves L WHERE E.emp_id=L.emp_id AND L.Status="Approved"')
        data1 = cursor.fetchall()
        return render_template("approved.html", data1=data1)

    return render_template("allleaves.html")

@app.route('/reject')
def reject():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT L.id,E.emp_id,L.emp_id,E.First_name,E.Last_name,L.leavetype,L.Status FROM employee_data E, leaves L WHERE E.emp_id=L.emp_id AND L.Status="Rejected"')
        data2 = cursor.fetchall()
        return render_template("reject.html", data2=data2)

    return render_template("reject.html")

@app.route('/active/<rowData>')
def active(rowData):
    if 'loggedin' in session:
        action = 'Active'
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE leave_management_system.employee_data SET Status=%s WHERE emp_id=%s',(action,rowData, ))
        db.connection.commit()
        return "active"

@app.route('/inactive/<rowData>')
def inactive(rowData):
    if 'loggedin' in session:
        action = 'Inactive'
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE leave_management_system.employee_data SET Status=%s WHERE emp_id=%s',(action,rowData, ))
        db.connection.commit()
        return "Inactive"


@app.route("/update", methods =['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'First_name' in request.form and 'Last_name' in request.form and 'Password' in request.form and 'Gender' in request.form and 'Dob' in request.form and 'Department' in request.form and 'City' in request.form and 'Country' in request.form and 'Phone_number' in request.form:
            First_name = request.form['First_name']
            Last_name = request.form['Last_name']
            Password = request.form['Password']
            Gender = request.form['Gender']
            Dob = request.form['Dob']
            Department = request.form['Department']
            City = request.form['City']
            Country = request.form['Country']
            Phone_number = request.form['Phone_number']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM employee_data WHERE First_name = % s', (First_name, ))
            info = cursor.fetchone()
            if info:
                msg = 'Account already exists !'
            else:
                cursor.execute('UPDATE employee_data SET  First_name =% s,  Last_name =% s ,Password =% s, Gender =% s, Dob =% s, Department =% s, City =% s, Country =% s, Phone_number =% s WHERE emp_id =% s', (First_name, Last_name, Password, Gender, Dob, Department, City, Country, Phone_number, (session['emp_id'], ), ))
                db.connection.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("updateprofile.html", msg = msg)
    return redirect(url_for('login'))

@app.route('/timesheet', methods=['POST','GET'])
def timesheet():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST'and 'date' in request.form:
            weekday = request.form['weekday']
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO leave_management_system.timesheet(weekday,date,start_time,end_time,emp_id) VALUES (%s,%s,%s,%s,%s)",(weekday,date,start_time,end_time,session['emp_id']))
            db.connection.commit()
        return render_template("Timesheet.html")

    return render_template("Timesheet.html")

@app.route('/report')
def report():
    if 'loggedin' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT weekday,DATE_FORMAT(date,"%e/%m/%Y") as Date,emp_id,start_time,end_time,TIMEDIFF(end_time,start_time) as total_working_hours from timesheet')
        time = cursor.fetchall()
        return render_template("Report.html", time=time)

    return render_template("Report.html")

if __name__=="__main__":
    app.run(debug=True)