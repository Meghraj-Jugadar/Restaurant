from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import uuid

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Monu848'
app.config['MYSQL_DB'] = 'restaurant'

mysql = MySQL(app)
app.secret_key = 'myKey'

'''///////////////////////////////////////////////////
/////////////////// Admin ////////////////////////////
//////////////////////////////////////////////////////'''

@app.route('/admin_register', methods=['POST', 'GET'])
def admin_register():
    try:
        if request.method == 'POST':
            user_name = request.form['name']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            user_type = request.form['type']
            if password != confirm_password:
                flash('Password mismatched.', 'error')
                return render_template('admin_register.html')
            cur = mysql.connection.cursor()
            cur.execute(''' INSERT INTO admin_reg VALUES(%s,%s,%s)''', (user_name, password,user_type))
            mysql.connection.commit()
            cur.close()
            flash('You were successfully registered.', 'success')
            return render_template('/admin_login.html')
    except:
        flash('You have an account please go to login page.', 'error')
        return render_template('/admin_register.html')
    finally:
        return render_template('/admin_login.html')

@app.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = 'Select user_name from admin_reg'
        cur.execute(query)
        admin = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/admin_login.html', admin=admin)
    if request.method == 'POST':
        user_name=request.form['username']
        password=request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM admin_reg WHERE user_name = %s AND password = %s''', (user_name, password))
        user=cur.fetchone()
        mysql.connection.commit()
        cur.close()
        if user:
            session['username'] = user[0]
            return redirect('/counter')
        else:
            flash('Invalid Password', 'error')
            cur = mysql.connection.cursor()
            query = 'Select user_name from admin_reg'
            cur.execute(query)
            admin = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('/admin_login.html', admin=admin)
    else:
        flash('Invalid Password', 'error')
        return render_template('/admin_login.html')

@app.route('/admin_logout', methods=['POST', 'GET'])
def admin_logout():
    session.pop('username',None)
    return redirect(url_for('admin_login'))

@app.route('/admin_forget_pass', methods=['POST', 'GET'])
def admin_forget_pass():
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin_reg WHERE user_name = %s", (username,))
        user = cur.fetchone()
        if user:
            session['username'] = user[0]
            return redirect(url_for('admin_reset_pass'))
        else:
            flash('Username not registered.', 'error')
            return render_template('/admin_forget_pass.html')
    else:
        return render_template('/admin_forget_pass.html')

@app.route('/admin_reset_pass', methods=['POST', 'GET'])
def admin_reset_pass():
    if 'username' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password and Confirm Password do not match.', 'error')
            return redirect(url_for('admin_reset_pass'))

        try:
            cur = mysql.connection.cursor()
            query = "UPDATE admin_reg SET password = %s WHERE user_name=%s"
            val = (password, session['username'],)
            cur.execute(query, val)
            mysql.connection.commit()
            affected_rows = cur.rowcount
            cur.close()

            if affected_rows > 0:
                flash('Password Reset Successfully.', 'success')
            else:
                flash('Failed to reset password.', 'error')

            return redirect(url_for('admin_login'))

        except Exception as e:
            flash(f'An error occurred while resetting password: {str(e)}', 'error')
            return redirect(url_for('admin_reset_pass'))

    return render_template('/admin_reset_pass.html')

@app.route('/staff_regist', methods=['POST','GET'])
def staff_regist():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    else:
        try:
            if request.method == 'POST':
                name = request.form['name']
                number = request.form['number']
                addr = request.form['addr']
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cur = mysql.connection.cursor()
                cur.execute(''' INSERT INTO staff_reg(name, number, addr, date_time) VALUES(%s,%s,%s,Now())''', (name, number, addr))
                mysql.connection.commit()
                cur.close()
                flash('You were successfully registered.', 'success')
        except:
            flash('You have an account please go to login page.', 'error')
            return render_template('staff_regist.html')
        return render_template('staff_regist.html')

'''///////////////////////////////////////////////////
/////////////////// Counter //////////////////////////
//////////////////////////////////////////////////////'''
@app.route('/counter')
def counter():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    else:
        date = datetime.now().strftime('%Y-%m-%d')
        day_name = datetime.now().strftime("%A")
        cur = mysql.connection.cursor()
        query = "SELECT ord.custId, ord.table_no, pay.time, pay.pay_id, pay.amount, pay.method, pay.status FROM orders ord JOIN payment pay ON ord.custId = pay.cust_ID WHERE ord.date = %s AND pay.date = %s"
        val = (date,date)
        cur.execute(query, val)
        payment_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('counter.html', payment_data=payment_data, date=date, day_name=day_name)

@app.route('/veg_edit', methods=['POST', 'GET'])
def veg_edit():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM veg")
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('/veg_edit.html', data=data)

@app.route('/insertveg', methods = ['POST'])
def insertveg():
    try:
        if request.method == "POST":
            flash("Data Inserted Successfully")
            name = request.form['name']
            price = request.form['price']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO veg (name, price) VALUES (%s, %s)", (name, price))
            mysql.connection.commit()
            return redirect(url_for('veg_edit'))
    except:
        flash('Enter Proper details.', 'error')
        return redirect(url_for('veg_edit'))

@app.route('/deleteveg/<int:id_data>', methods = ['GET'])
def deleteveg(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM veg WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('veg_edit'))

@app.route('/updateveg', methods= ['POST', 'GET'])
def updateveg():
    try:
        if request.method == 'POST':
            id_data = request.form['id']
            name = request.form['name']
            price = request.form['price']

            cur = mysql.connection.cursor()
            query = "UPDATE veg SET name=%s,price=%s WHERE id=%s"
            val = (name, price, id_data)
            cur.execute(query, val)
            mysql.connection.commit()
            flash("Data Updated Successfully")
            return redirect(url_for('veg_edit'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/dessert_edit', methods=['POST','GET'])
def dessert_edit():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    query = 'SELECT * FROM dessert;'
    cur.execute(query)
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('/dessert_edit.html', data=data)

@app.route('/insertdessert', methods = ['POST'])
def insertdessert():
    try:
        if request.method == "POST":
            flash("Data Inserted Successfully")
            name = request.form['name']
            price = request.form['price']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO dessert (name, price) VALUES (%s, %s)", (name, price))
            mysql.connection.commit()
            return redirect(url_for('dessert_edit'))
    except:
        flash('Enter Proper details.', 'error')
        return redirect(url_for('dessert_edit'))

@app.route('/deletedessert/<int:id_data>', methods = ['GET'])
def deletedessert(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM dessert WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('dessert_edit'))

@app.route('/updatedessert', methods= ['POST', 'GET'])
def updatedessert():
    try:
        if request.method == 'POST':
            id_data = request.form['id']
            name = request.form['name']
            price = request.form['price']

            cur = mysql.connection.cursor()
            query = "UPDATE dessert SET name=%s,price=%s WHERE id=%s"
            val = (name, price, id_data)
            cur.execute(query, val)
            mysql.connection.commit()
            flash("Data Updated Successfully")
            return redirect(url_for('dessert_edit'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/nonveg_edit', methods=['POST', 'GET'])
def nonveg_edit():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM nonveg")
        data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/nonveg_edit.html', data=data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/insertnonveg', methods = ['POST'])
def insertnonveg():
    try:
        if request.method == "POST":
            flash("Data Inserted Successfully")
            name = request.form['name']
            price = request.form['price']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO nonveg (name, price) VALUES (%s, %s)", (name, price))
            mysql.connection.commit()
            return redirect(url_for('nonveg_edit'))
    except:
        flash('Enter Proper details.', 'error')
        return redirect(url_for('nonveg_edit'))

@app.route('/deletenonveg/<int:id_data>', methods = ['GET'])
def deletenonveg(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM nonveg WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('nonveg_edit'))

@app.route('/updatenonveg', methods= ['POST', 'GET'])
def updatenonveg():
    try:
        if request.method == 'POST':
            id_data = request.form['id']
            name = request.form['edit-name']
            price = request.form['edit-price']
            cur = mysql.connection.cursor()
            query = "UPDATE nonveg SET name=%s,price=%s WHERE id=%s"
            val = (name, price, id_data)
            cur.execute(query, val)
            mysql.connection.commit()
            flash("Data Updated Successfully")
            return redirect(url_for('nonveg_edit'))
    except:
        #return jsonify({'error': str(e)}), 400
        flash("Please enter valid details.")
        return redirect(url_for('nonveg_edit'))

@app.route('/cust_data')
def cust_data():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    query = "SELECT * FROM cust_reg"
    cur.execute(query)
    custdata = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template("cust_data.html", custdata=custdata)

@app.route('/insertcust', methods = ['POST'])
def insertcust():
    try:
        if request.method == "POST":
            flash("Data Inserted Successfully")
            name = request.form['name']
            number = request.form['number']
            password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO cust_reg (name, number, password) VALUES (%s, %s, %s)", (name, number, password))
            mysql.connection.commit()
            return redirect(url_for('cust_data'))
    except:
        flash('Enter Proper details.', 'error')
        return redirect(url_for('cust_data'))

@app.route('/updatecust', methods= ['POST', 'GET'])
def updatecust():
    try:
        if request.method == 'POST':
            id_data = request.form['id']
            name = request.form['name']
            number = request.form['number']
            password = request.form['password']
            cur = mysql.connection.cursor()
            query = "UPDATE cust_reg SET name=%s, number=%s, password=%s WHERE id=%s"
            val = (name, number, password, id_data)
            cur.execute(query, val)
            mysql.connection.commit()
            flash("Data Updated Successfully")
            return redirect(url_for('cust_data'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/pay_details')
def pay_details():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    query = "SELECT * FROM cust_reg"
    cur.execute(query)
    custdata = cur.fetchall()
    cur.close()
    return render_template("pay_details.html", custdata=custdata)

@app.route('/kitchen', methods=['POST','GET'])
def kitchen():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    try:
        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM orders where date = %s",(now,))
        ord_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/kitchen.html', ord_data=ord_data)
    except:
        return render_template('/kitchen.html')

@app.route('/ord_view_kitchen/<int:id_data>', methods=['POST','GET'])
def ord_view_kitchen(id_data):
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    now = datetime.now().strftime('%Y-%m-%d')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cart where cust_id = %s and date = %s", (id_data, now))
    cart_data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cust_reg WHERE number=%s", (id_data,))
    customer_data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE custId=%s and date = %s", (id_data, now))
    ord_data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('/ord_view_kitchen.html', cart_data=cart_data, customer_data=customer_data, ord_data=ord_data)

@app.route('/report', methods=['POST','GET'])
def report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    return render_template('/report.html')

@app.route('/cust_report', methods=['POST','GET'])
def cust_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM cust_reg"
        cur.execute(query)
        custdata = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('cust_report.html', custdata=custdata)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM cust_reg WHERE name LIKE %s or number LIKE %s or date_time LIKE %s"
        val = ('%' + search + '%', '%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        custdata = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('cust_report.html', custdata=custdata)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM cust_reg"
        cur.execute(query)
        custdata = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('cust_report.html', custdata=custdata)

@app.route('/pay_report', methods=['POST','GET'])
def pay_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM payment"
        cur.execute(query)
        payment_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('pay_report.html', payment_data=payment_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM payment WHERE pay_id LIKE %s or order_id LIKE %s or cust_ID LIKE %s or method LIKE %s or date LIKE %s or amount LIKE %s"
        val = ('%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        payment_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('pay_report.html', payment_data=payment_data)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM payment"
        cur.execute(query)
        payment_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('pay_report.html', payment_data=payment_data)
    return render_template('pay_report.html')

@app.route('/staff_report', methods=['POST','GET'])
def staff_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM staff_reg"
        cur.execute(query)
        staff_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('staff_report.html', staff_data=staff_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM staff_reg WHERE name LIKE %s or number LIKE %s or addr LIKE %s or date_time LIKE %s"
        val = ('%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        staff_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('staff_report.html', staff_data=staff_data)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM staff_reg"
        cur.execute(query)
        staff_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('staff_report.html', staff_data=staff_data)
    return render_template('staff_report.html')

@app.route('/feed_report', methods=['POST','GET'])
def feed_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM feedback"
        cur.execute(query)
        feed_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('feed_report.html', feed_data=feed_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM feedback WHERE name LIKE %s or number LIKE %s or date LIKE %s or time LIKE %s"
        val = ('%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        feed_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('feed_report.html', feed_data=feed_data)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM feedback"
        cur.execute(query)
        feed_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('feed_report.html', feed_data=feed_data)
    return render_template('feed_report.html')

@app.route('/adm_report', methods=['POST','GET'])
def adm_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM admin_reg"
        cur.execute(query)
        admin_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('adm_report.html', admin_data=admin_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM admin_reg WHERE user_name LIKE %s or user_type LIKE %s"
        val = ('%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        admin_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('adm_report.html', admin_data=admin_data)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM admin_reg"
        cur.execute(query)
        admin_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('adm_report.html', admin_data=admin_data)
@app.route('/ord_report', methods=['POST','GET'])
def ord_report():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM orders"
        cur.execute(query)
        ord_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('ord_report.html', ord_data=ord_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM orders WHERE custId LIKE %s or date LIKE %s "
        val = ('%' + search + '%', '%' + search + '%')
        cur.execute(query, val)
        ord_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('ord_report.html', ord_data=ord_data)
    else:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM orders"
        cur.execute(query)
        ord_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('ord_report.html', ord_data=ord_data)

@app.route('/order_data/<int:id_data>', methods=['POST','GET'])
def order_data(id_data):
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        #now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE cust_id = %s ", (id_data,))
        cart_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cust_reg WHERE number=%s", (id_data,))
        custoer_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('order_data.html', cart_data=cart_data, custoer_data=custoer_data)
    elif request.method == 'POST':
        search = request.form.get('search')
        cur = mysql.connection.cursor()
        query = "SELECT * FROM cart WHERE date LIKE %s and cust_id = %s"
        val = ('%' + search + '%', id_data)
        cur.execute(query, val)
        cart_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('order_data.html', cart_data=cart_data)
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE cust_id = %s ", (id_data,))
        cart_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cust_reg WHERE number=%s", (id_data,))
        custoer_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('order_data.html', cart_data=cart_data, custoer_data=custoer_data)
'''
///////////////////////////////////////////////////
/////////////////// Customer /////////////////////////
//////////////////////////////////////////////////////'''

@app.route('/', methods=['POST', 'GET'])
def cust_register():

    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if password != confirm_password:
            flash('Password and Confirm Password fields do not match.', 'error')
            return render_template('/cust_register.html')
        try:
            cur = mysql.connection.cursor()
            cur.execute(''' INSERT INTO cust_reg(name, number, password, date_time) VALUES(%s,%s,%s, Now())''', (name, number, password))
            mysql.connection.commit()
            cur.close()
            flash('You were successfully registered.', 'success')
            return render_template('/cust_login.html')
        except:
            flash('You have an account please login.', 'error')
            return render_template('/cust_login.html')
    return render_template('/cust_register.html')

@app.route('/cust_login', methods=['POST', 'GET'])
def cust_login():
    try:
        if request.method == 'POST':
            number = request.form['number']
            password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute('''SELECT number, password FROM cust_reg WHERE number = %s and password = %s ''', (number,password))
            user=cur.fetchone()
            mysql.connection.commit()
            cur.close()
            if user:
                session['number']=user[0]
                return redirect('/home')
            else:
                flash('Please enter valid number and password.', 'error')
                return render_template('/cust_login.html')
        return render_template('/cust_login.html')
    except:
        flash('You have not registered.', 'error')
        return render_template('/cust_login.html')

@app.route('/cust_logout', methods=['POST', 'GET'])
def cust_logout():
    session.pop('number',None)
    return redirect(url_for('cust_login'))

@app.route('/forget_password', methods=['POST', 'GET'])
def forget_password():
    if request.method == 'POST':
        number = request.form['number']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cust_reg WHERE number = %s", [number])
        user = cur.fetchone()
        if user:
            session['number'] = user[2]
            return redirect(url_for('reset_password'))
        else:
            flash('Number not registered.', 'error')
            return render_template('/forget_password.html')
    else:
        return render_template('/forget_password.html')

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if 'number' not in session:
        return redirect(url_for('cust_login'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password and Confirm Password do not match.', 'error')
            return redirect(url_for('reset_password'))

        try:
            cur = mysql.connection.cursor()
            query = "UPDATE cust_reg SET password = %s WHERE number=%s"
            val = (password, session['number'],)
            cur.execute(query, val)
            mysql.connection.commit()
            affected_rows = cur.rowcount
            cur.close()

            if affected_rows > 0:
                flash('Password Reset Successfully.', 'success')
            else:
                flash('Failed to reset password.', 'error')

            return redirect(url_for('cust_login'))

        except Exception as e:
            flash(f'An error occurred while resetting password: {str(e)}', 'error')
            return redirect(url_for('reset_password'))

    return render_template('/reset_password.html')

'''///////////////////////////////////////////////////
/////////////////// Customer UI //////////////////////////
//////////////////////////////////////////////////////'''

@app.route('/home', methods=['GET'])
def home():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cust_reg WHERE number=%s",(user,))
        custdata = cur.fetchall()
        mysql.connection.commit()
        cur.close()

        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM orders WHERE custId=%s and date = %s",(user, now))
        orddata = cur.fetchall()
        mysql.connection.commit()
        cur.close()

        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE cust_id = %s and date = %s", (user, now))
        cart_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()

        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM payment WHERE cust_ID = %s and date = %s", (user, now))
        payment_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()

        return render_template('/home.html', custdata=custdata, orddata=orddata, cart_data=cart_data, payment_data=payment_data)

'''  Contact Page '''

@app.route('/contact', methods=['POST','GET'])
def contact():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        if request.method == 'POST':
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            name = request.form['name']
            number = request.form['number']
            message = request.form['message']
            cur = mysql.connection.cursor()
            cur.execute(''' INSERT INTO feedback(name, number, message, date, time) VALUES(%s,%s,%s,%s,%s)''',
                (name, number, message, date, time))
            mysql.connection.commit()
            cur.close()
            flash('Thank you for your feedback.', 'success')
        return render_template('/contact.html')

@app.route('/nonveg_list',methods=['POST','GET'])
def nonveg_list():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM nonveg"
        cur.execute(query)
        nonveg = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/nonveg_list.html', nonveg=nonveg)
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user=cur.fetchone()[0]
        try:
            if request.method == 'POST':
                id = request.form['id']
                name = request.form['name']
                price = request.form['price']
                quantity = request.form['quantity']
                subtotal = request.form['subtotal']
                datetime.now().strftime('%Y-%m-%d')
                cur = mysql.connection.cursor()
                cur.execute(''' INSERT INTO cart(food_id, name, price, quantity, sub_total, cust_id, date) VALUES(%s,%s,%s,%s,%s,%s,Now())''', (id, name, price, quantity, subtotal, user))
                mysql.connection.commit()
                cur.close()
                flash('Item added to cart.', 'success')
        except Exception:
            flash('Please Enter Quantity.', 'error')
            #return jsonify({'error': str(e)}), 400
            return render_template('/nonveg_list.html')
        finally:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM nonveg"
            cur.execute(query)
            nonveg = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('/nonveg_list.html', nonveg=nonveg)
    return render_template('/nonveg_list.html')

@app.route('/dessert_list', methods=['POST','GET'])
def dessert_list():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM dessert"
        cur.execute(query)
        dessert = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/dessert_list.html', dessert=dessert)
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user=cur.fetchone()[0]
        try:
            if request.method == 'POST':
                id = request.form['id']
                name = request.form['name']
                price = request.form['price']
                quantity = request.form['quantity']
                subtotal = request.form['subtotal']
                datetime.now().strftime('%Y-%m-%d')
                cur = mysql.connection.cursor()
                cur.execute(''' INSERT INTO cart(food_id, name, price, quantity, sub_total, cust_id, date) VALUES(%s,%s,%s,%s,%s,%s,Now())''', (id, name, price, quantity, subtotal,user))
                mysql.connection.commit()
                cur.close()
                flash('Item added to cart.', 'success')
                return render_template('/dessert_list.html')
        except:
            flash('Please Enter Quantity.', 'error')
            return render_template('/dessert_list.html')
        finally:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM dessert"
            cur.execute(query)
            dessert = cur.fetchall()
            cur.close()
            mysql.connection.commit()
            return render_template('/dessert_list.html', dessert=dessert)
    return render_template('/dessert_list.html')

@app.route('/veg_list',methods=['POST','GET'])
def veg_list():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = "SELECT * FROM veg"
        cur.execute(query)
        veg = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('/veg_list.html', veg=veg)
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]
        try:
            if request.method == 'POST':
                id = request.form['id']
                name = request.form['name']
                price = request.form['price']
                quantity = request.form['quantity']
                subtotal = request.form['subtotal']
                datetime.now().strftime('%Y-%m-%d')
                cur = mysql.connection.cursor()
                cur.execute(''' INSERT INTO cart(food_id, name, price, quantity, sub_total, cust_id, date) 
                VALUES(%s,%s,%s,%s,%s,%s,Now())''', (id, name, price, quantity, subtotal, user))
                mysql.connection.commit()
                cur.close()
                flash('Item added to cart.', 'success')
        except Exception:
            flash('Please Enter Quantity.', 'error')
            #return jsonify({'error': str(e)}), 400
            return render_template('/veg_list.html')
        finally:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM veg"
            cur.execute(query)
            veg = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('/veg_list.html', veg=veg)
    return render_template('/veg_list.html')

@app.route('/cart', methods=['POST','GET'])
def cart():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT table_no FROM table_number")
        table_no = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]
        if request.method == 'GET':
            now = datetime.now().strftime('%Y-%m-%d')
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM cart WHERE cust_id = %s and date=%s",(user,now))
            cart_data = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('/cart.html', cart_data=cart_data, table_no=table_no)

@app.route('/updatecart', methods= ['POST', 'GET'])
def updatecart():
    try:
        if request.method == 'POST':
            id_data = request.form['id']
            quantity = request.form['quantity']
            subtotal = request.form['subtotal']
            cur = mysql.connection.cursor()
            query = "UPDATE cart SET quantity=%s,sub_total=%s WHERE cart_id=%s"
            val = (quantity, subtotal, id_data)
            cur.execute(query, val)
            mysql.connection.commit()
            flash("Updated Successfully",'success')
            return redirect(url_for('cart'))
    except Exception:
        flash("Something is wrong, error")
        return redirect(url_for('cart'))

@app.route('/delete_cart/<int:id_data>', methods=['GET'])
def delete_cart(id_data):
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        try:
            flash("Removed Successfully",'success')
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM cart WHERE cart_id=%s", (id_data,))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('cart'))
        except Exception:
            flash("Something Wrong",'error')
            return redirect(url_for('cart'))


@app.route('/place_order', methods=['POST','GET'])
def place_order():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]
        try:
            if request.method == 'POST':
                table = request.form['table']
                total = request.form['total']
                now = datetime.now().strftime('%Y-%m-%d')
                time = datetime.now().strftime('%H:%M:%S')
                order_id = uuid.uuid4().hex[:10]
                cur = mysql.connection.cursor()
                query="INSERT INTO orders VALUES(%s, %s, %s, %s, %s, %s)"
                val = (user,now, time, table, total, order_id)
                cur.execute(query, val)
                mysql.connection.commit()
                cur.close()
                flash('Order Placed.', 'success')
                return render_template('/ord_msg.html')
        except Exception:
            flash('Order Not Placed.', 'error')
            #return jsonify({'error': str(e)}), 400
            return render_template('/cart.html')

@app.route('/update_order', methods=['POST','GET'])
def update_order():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]
        try:
            if request.method == 'POST':
                table = request.form['table']
                total = request.form['total']
                now = datetime.now().strftime('%Y-%m-%d')
                time = datetime.now().strftime('%H:%M:%S')
                cur = mysql.connection.cursor()
                query = "UPDATE orders SET time=%s, table_no=%s, total=%s WHERE custId=%s and date=%s"
                val = (time, table, total, user, now)
                cur.execute(query, val)
                mysql.connection.commit()
                cur.close()
                flash('Order Placed.', 'success')
                return render_template('/ord_update_msg.html')
        except Exception:
            flash('Order Not Placed.', 'error')
            #return jsonify({'error': str(e)}), 400
            return render_template('/cart.html')

@app.route('/cancel_order/<string:order_id>', methods=['POST','GET'])
def cancel_order(order_id):
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM orders WHERE ord_id=%s", (order_id,))
            mysql.connection.commit()
            cur.close()
            flash('Order Canceled.', 'error')
            return redirect(url_for('home'))
        except Exception:
            #return jsonify({'error': str(e)}), 400
            flash('Order Not Canceled.', 'error')
            return render_template('/home.html')

@app.route('/pay', methods=['POST','GET'])
def pay():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT number FROM cust_reg WHERE number = %s ''', (session['number'],))
        mysql.connection.commit()
        user = cur.fetchone()[0]
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT ord_id FROM orders WHERE custId = %s and date = %s''', (session['number'],now))
        mysql.connection.commit()
        ord_id = cur.fetchone()[0]
        try:
            if request.method == 'POST':
                pay_id = request.form['utr']
                method = request.form['mt']
                datetime.now().strftime('%Y-%m-%d')
                time = datetime.now().strftime('%H:%M:%S')
                amount = request.form['amt']
                status = request.form['pay_status']
                cur = mysql.connection.cursor()
                query = "INSERT INTO payment VALUES(%s, %s, %s, %s, NOW(), %s, %s, %s)"
                val = (pay_id, ord_id, user, method, time, amount, status)
                cur.execute(query, val)
                mysql.connection.commit()
                cur.close()
                flash('Payment Done.', 'success')
            return redirect(url_for('home'))
        except Exception:
            #return jsonify({'error': str(e)}), 400
            flash('Submit valid 12 digit UTR number.', 'error')
            return redirect(url_for('home'))
    return render_template('/home.html')

@app.route('/ord_msg')
def ord_msg():
    if 'number' not in session:
        return redirect(url_for('cust_login'))
    else:
        return render_template('/ord_msg.html')

if __name__=='__main__':
    app.run(debug=True)
