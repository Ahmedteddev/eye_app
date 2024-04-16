from flask import Flask, render_template, request, url_for, redirect  # type: ignore
import sqlite3
from sqlite3 import Error
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

app = Flask(__name__)

# loading model 
model = load_model('ml_model.h5')
class_names = ['Mild', 'Moderate', 'No_DR', 'Proliferate_DR', 'Severe']

#default/login route 
@app.route("/")
def login():
    return render_template("login.html")

#login functionality 
@app.route('/login', methods=['POST'])
def dologin():
        username = request.form['username']
        password = request.form['password']
        con = sqlite3.connect("patient.db")
        cur = con.cursor()
        user = cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        con.commit()
        cur.close()
        if user:

            return redirect("/Home")
        else:
            return 'Invalid username or password'

#signup route 
@app.route("/signup")
def signup():
    return render_template("signup.html")

#signup functionality 
@app.route('/dosignup', methods=['POST'])
def dosignup():
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("patient.db")
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        cur.close()
        return redirect('/')

#Home route 
@app.route("/Home")
def home():
    return render_template("Home.html")

# Photo submission route 
@app.route("/submission")
def submission():
    return render_template("submission.html")

# patient form 
@app.route("/form")
def Patientform():
    return render_template("form.html")

# functionality for patient form 
@app.route("/dodatabase", methods=("POST",))
def formal():
    con = None
    try:
        con = sqlite3.connect("patient.db")
    except Error as e:
        return "Error connecting to database:" + str(e)
    
    try:
        cur = con.cursor()
        patient_id = request.form['patientID']
        patient_name = request.form['patientName']
        patient_age = int(request.form['patientage']) 
        patient_condition = request.form['patientcondition']
        sql = "INSERT INTO patient_info(patient_id, pateint_name, patient_age, patient_condition) VALUES(?, ?, ?, ?)"
        cur.execute(sql, (patient_id, patient_name, patient_age, patient_condition))
        con.commit()
        cur.close()

        return redirect(url_for("Veiwpatient"))

    except Exception as e:
        return "Error executing query: " + str(e)
    return redirect(url_for("Veiwpatient"), data = rows)
    
# patient table route 
@app.route("/veiwpatient")
def Veiwpatient():
    con = None
    try:
        con = sqlite3.connect("patient.db")
    except Error as e:
        return "Error connecting to database:" + str(e)
    
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM patient_info")
        rows = cur.fetchall()
        cur.close()
    except Error as e:
        return "Error executing query" + str(e)
    finally: 
        con.close()
    
    return render_template("veiwpatient.html", data = rows )
    

# funtionlity for the photo submission 
@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    img = Image.open(uploaded_file)
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    prediction = model.predict(np.expand_dims(img_array, axis=0))
    predicted_label = class_names[np.argmax(prediction)]
    return render_template('result.html', prediction=predicted_label)



if __name__ == '__main__':
    app.run(debug=True)