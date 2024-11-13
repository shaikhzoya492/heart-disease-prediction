from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from flask import session
import pickle
import os
from mysql.connector import Error


model_path = 'C:\\Users\\Zoya\\Heart disease prediction\\heart_disease_model.pkl'
with open(model_path, 'rb') as file:
    loaded_model = pickle.load(file)

app = Flask(__name__)
app.secret_key = '111'

db_config = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'heart_map'),
    'charset': 'utf8'
}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/view_appointments')
def appointment():
    db = None
    cursor = None
    appointment_list = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, gender, age, appoindate, email, phno, diseases, doctor, address FROM appointments")
        appointment_list = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching appointment data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('appointment.html', appointments=appointment_list)

@app.route('/predict', methods=['POST'])
def predict():
    inputs = [
        int(request.form['male']),
        int(request.form['age']),
        int(request.form['education']),
        int(request.form['currentSmoker']),
        int(request.form['cigsPerDay']),
        int(request.form['BPMeds']),
        int(request.form['prevalentStroke']),
        int(request.form['prevalentHyp']),
        int(request.form['diabetes']),
        int(request.form['totChol']),
        int(request.form['sysBP']),
        int(request.form['diaBP']),
        float(request.form['BMI']),
        int(request.form['heartRate']),
        int(request.form['glucose'])
    ]

    prediction = loaded_model.predict([inputs])


    has_disease = prediction[0] == 1
    message = "You have been diagnosed with heart disease. It's important to take immediate steps to manage your health." if has_disease else "You do not have heart disease. Keep up your healthy lifestyle and continue making choices that support your heart health!"

    return render_template('result.html', message=message, has_disease=has_disease)

@app.route('/select_doctor')
def select_doctor():
    db = None
    cursor = None
    doctors = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, qualification, phone FROM doctors")
        doctors = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching doctor data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('selectdoctor.html', doctors=doctors)

def check_credentials(email, password):
    db = None
    cursor = None
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        return user is not None
    except Error as e:
        flash(f'Error during login: {str(e)}', 'danger')
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_credentials(email, password):  
            flash('Login successful!', 'success')
            return redirect(url_for('user_page'))  
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('user_login.html')

@app.route('/user_page') 
def user_page():
    return render_template('userpage.html') 

@app.route('/logout')
def logout():
   
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('user_login')) 

def check_credential(email, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM doctors WHERE email = %s AND password = %s"  # Adjust the table name if necessary
    cursor.execute(query, (email, password))
    doctor = cursor.fetchone()
    cursor.close()
    connection.close()
    return doctor

@app.route('/doctorlogin', methods=['GET', 'POST'])
def doctor_login():
    error_msg = None  
    suc_msg = None   

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        doctor = check_credential(email, password)

        if doctor: 
            suc_msg = "Login successful!"  
            return redirect(url_for('doctorpage')) 
        else: 
            error_msg = 'Invalid email or password' 
    return render_template('doctorlogin.html', error_msg=error_msg, suc_msg=suc_msg)  


@app.route('/adminpage')
def admin_page():
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()


    cursor.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    appointment_count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template('adminpage.html', doctor_count=doctor_count, user_count=user_count, appointment_count=appointment_count)


@app.route('/appointment_page', methods=['GET'])
def appointment_page():
    appointment_message = request.args.get('appointment_message', '')  # Get appointment message from query params
    return render_template('appointment_page.html', appointment_message=appointment_message)

@app.route('/adminlogin')
def admin_login():
    return render_template('adminlogin.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor_page():
    if request.method == 'POST':
        return redirect(url_for('doctor_register'))
    return render_template('doctor.html')

@app.route('/viewappointments')
def view_appointments():
    db = None
    cursor = None
    appointment_list = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, gender, age, appoindate, email, phno, diseases, doctor, address FROM appointments")
        appointment_list = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching appointment data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('view_appointments.html', appointments=appointment_list)


@app.route('/viewdoctors')
def view_doctors():
    db = None
    cursor = None
    doctor_list = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, dob, qualification, email, phone FROM doctors")
        doctor_list = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching doctor data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('viewdoctors.html', doctors=doctor_list)

@app.route('/user_register', methods=['POST'])
def user_register():
    fullname = request.form['fullname']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    db = None
    cursor = None
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        sql = "INSERT INTO users (fullname, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (fullname, email, phone, password))
        db.commit()
        flash('Registration successful!', 'success')
    except Error as e:
        if db:
            db.rollback()
        flash(f'Registration failed: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

    return redirect(url_for('signup'))

@app.route('/user_appointment', methods=['POST'])
def user_appointment():
    fullname = request.form['fullname']
    gender = request.form['gender']
    age = request.form['age']
    appoindate = request.form['appoindate']
    email = request.form['email']
    phno = request.form['phno']
    diseases = request.form['diseases']
    doctor = request.form['doctor']
    address = request.form['address']
    
    appointment_message = ""  
    db1 = None
    cursor1 = None
    try:
        db1 = mysql.connector.connect(**db_config)
        cursor1 = db1.cursor()
        sql = """
        INSERT INTO appointments (fullname, gender, age, appoindate, email, phno, diseases, doctor, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor1.execute(sql, (fullname, gender, age, appoindate, email, phno, diseases, doctor, address))
        db1.commit()
        appointment_message = 'Appointment submitted successfully!'  
    except Error as e:
        if db1:
            db1.rollback()
        appointment_message = f'Appointment submission failed: {str(e)}'  
    finally:
        if cursor1 is not None:
            cursor1.close()
        if db1 is not None:
            db1.close()

    return redirect(url_for('appointment_page', appointment_message=appointment_message))  

@app.route('/userappointment', methods=['POST'])
def userappointment():
    fullname = request.form['fullname']
    gender = request.form['gender']
    age = request.form['age']
    appoindate = request.form['appoindate']
    email = request.form['email']
    phno = request.form['phno']
    diseases = request.form['diseases']
    doctor = request.form['doctor']
    address = request.form['address']
    
    appointment_message = ""  
    db1 = None
    cursor1 = None
    try:
        db1 = mysql.connector.connect(**db_config)
        cursor1 = db1.cursor()
        sql = """
        INSERT INTO appointments (fullname, gender, age, appoindate, email, phno, diseases, doctor, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor1.execute(sql, (fullname, gender, age, appoindate, email, phno, diseases, doctor, address))
        db1.commit()
        appointmentmessage = 'Appointment submitted successfully!'  
    except Error as e:
        if db1:
            db1.rollback()
        appointmentmessage = f'Appointment submission failed: {str(e)}'  
    finally:
        if cursor1 is not None:
            cursor1.close()
        if db1 is not None:
            db1.close()

    return redirect(url_for('appointment', appointment_message=appointment_message))  

@app.route('/doctor_register', methods=['POST'])
def doctor_register():
    fullname = request.form['fullname']
    dob = request.form['dob']
    qualification = request.form['qualification']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password'] 

    db = None
    cursor = None
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        sql = "INSERT INTO doctors (fullname, dob, qualification, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (fullname, dob, qualification, email, phone, password))
        db.commit()
        flash('Doctor registration successful!', 'success')
    except Error as e:
        if db:
            db.rollback()
        flash(f'Doctor registration failed: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

    return redirect(url_for('doctor_page'))

@app.route('/view_users')
def view_users():
    db = None
    cursor = None
    user_list = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, email, phone FROM users")  # Adjust fields as necessary
        user_list = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching user data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('view_users.html', users=user_list)

@app.route('/doctorpage')
def doctorpage():
    db = None
    cursor = None
    appointment_list = []
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT fullname, gender, age, appoindate, email, phno, diseases, doctor, address FROM appointments")
        appointment_list = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching appointment data: {str(e)}', 'danger')
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
    return render_template('doctorpage.html', appointments=appointment_list)

if __name__ == '__main__':
    app.run(debug=True)