from __future__ import division, print_function
from app import app
from flask import render_template
from datetime import datetime

# coding=utf-8
import sys
import os
import glob
import re
import numpy as np

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import Flask, session, redirect, url_for, render_template, request, escape
from werkzeug.utils import secure_filename

#++++++++++++++++++++++++   CNN   +++++++++++++++++++++++++++++++++
# Model saved with Keras model.save()
MODEL_PATH = 'models/RPL.h5'

#Load your trained model
model = load_model(MODEL_PATH)
print('Model loaded. Start serving...')

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(32, 32)) #target_size must agree with what the trained model expects!!

    # Preprocessing the image
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)

   
    preds = model.predict_classes(img)
    return preds

#
@app.route('/prediksi', methods=['GET'])
def prediksi():
    # Main page
    return render_template('prediksi.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        #os.remove(file_path)#removes file from the server after prediction has been returned

        # Arrange the correct return according to the model. 
		# In this model 1 is Pneumonia and 0 is Normal.
        str1 = 'maaf yang anda masukan "MOBIL ALPARD" bukan kendaraan bermotor'
        str2 = 'Motor Honda Beat'
        str3 = 'maaf yang anda masukan "Kereta Api" bukan kendaraan bermotor'
        str4 = 'maaf yang anda masukan "Pesawat" bukan kendaraan bermotor'
        str5 = 'Motor Satria Fu'
        str6 = 'Motor Honda Scoopy'
        str7 = 'maaf yang anda masukan "MOBIL Sport" bukan kendaraan bermotor'
        str8 = 'maaf yang anda masukan "MOBIL Truck" bukan kendaraan bermotor'
        if preds == [0]:
            return str1
        elif preds == [1]:
            return str2
        elif preds == [2]:
            return str3
        elif preds == [3]:
            return str4
        elif preds == [4]:
            return str5
        elif preds == [5]:
            return str6
        elif preds == [6]:
            return str7
        else:
            return str8
    return None

#++++++++++++++++++++MFCC+++++++++++++++++++++++++++++++++++

#++++++++++++++++++++++++CHECKBOX
app.secret_key = 'isinya password buat session'
app.static_folder = 'static'

daftarGejala = ['Suara gemeretak','Tidak responsif','Keluar asap putih','Boros bensin','Tenaga yang dihasilkan lemah','Mesin tersendat-sendat']
daftarKerusakan = ['Kerusakan Pada Piston','Kerusakan Pada Klep','Kerusakan Aus Sabuk']
solusiPenyakit = ['Ganti Piston','Ganti Klep','Ganti Sabuk']
gejala = 0

def checkGejala():
    if request.form.get('pilihan') == 'ya':
        return True
    if request.form.get('pilihan') == 'tidak':
        return False
    else:
        return checkGejala()

@app.route('/')
def box():
   session.pop('namaPengguna', None)
   session.pop('gejalaKerusakan', None)
   session.pop('logs', None)
   session.pop('logs2', None)
   session['gejalaKerusakan'] = 0
   session['logs'] = 0
   session['logs2'] = 0
   return render_template('box.html', link = url_for('box'))

@app.route('/welcome',methods = ['POST', 'GET'])
def welcome():
   if request.method == 'POST':
      name = request.form.get('Name')
      session['namaPengguna'] = name
      gejalanya = session['gejalaKerusakan']
      pertanyaan = daftarGejala[gejalanya]
      return render_template("welcome.html", name = name,  pertanyaan = pertanyaan, link = url_for('box'))

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      #=============================================================Logs 0
      if session['logs'] == 0 and checkGejala():
         if session['gejalaKerusakan'] == 0: # Penyakit 1
            session['gejalaKerusakan'] = 1
            session['logs'] = 1
            return redirect(url_for('diagnosa'))

      #=============================================================Logs 1
      elif session['logs'] == 1  and checkGejala():
         if session['gejalaKerusakan'] == 1: # Penyakit 1
            session['gejalaKerusakan'] = 2
            session['logs'] = 2
            return redirect(url_for('diagnosa'))
         elif session['gejalaKerusakan'] == 3 and session['logs2'] == 0: # Penyakit 2
            session['gejala kerusakan'] = 4
            session['logs'] = 2
            return redirect(url_for('diagnosa'))
         elif session['gejalaKerusakan'] == 4 and session['logs2'] == 0: # Penyakit 2
            session['gejala kerusakan'] = 5
            session['logs'] = 2
            return redirect(url_for('diagnosa'))
         

      #=============================================================Logs 2
      elif session['logs'] == 2 and checkGejala():
         if session['gejalaKerusakan'] == 2: # Penyakit 1
            terjangkitPenyakit = daftarKerusakan[0]
            solusiPenyakitnya = "Solusi: " + solusiPenyakit[0]
            return render_template("result.html", terjangkitPenyakit = terjangkitPenyakit, solusiPenyakitnya = solusiPenyakitnya, awal = url_for('box'))
         elif session['gejalaKerusakan'] == 4 and session['logs2'] == 0: # Penyakit 2
            terjangkitPenyakit = daftarKerusakan[1]
            solusiPenyakitnya = "Solusi: " + solusiPenyakit[1]
            return render_template("result.html", terjangkitPenyakit = terjangkitPenyakit, solusiPenyakitnya = solusiPenyakitnya, awal = url_for('box'))
         elif session['gejalaKerusakan'] == 5 and session['logs2'] == 1: # Penyakit 3
            terjangkitPenyakit = daftarKerusakan[2]
            solusiPenyakitnya = "Solusi: " + solusiPenyakit[2]
            return render_template("result.html", terjangkitPenyakit = terjangkitPenyakit, solusiPenyakitnya = solusiPenyakitnya, awal = url_for('box'))
 
      #=============================================================Logs 1      
      else:
         if session['gejalaKerusakan'] == 0: # Penyakit 2
            session['gejalaKerusakan'] = 3
            session['logs'] = 1
            session['logs2'] = 0
            return redirect(url_for('diagnosa'))
         elif session['gejalaKerusakan'] == 1: # Penyakit 3
            session['gejalaKerusakan'] = 4 
            session['logs'] = 1
            session['logs2'] = 1
            return redirect(url_for('diagnosa'))               
         else:
            terjangkitPenyakit = "Motor Anda ga rusak koq." # Tidak ada gejala
            return render_template("result.html", terjangkitPenyakit = terjangkitPenyakit, awal = url_for('box'))
         

@app.route('/diagnosa',methods = ['POST', 'GET'])
def diagnosa():
   name = session['namaPengguna']
   pertanyaan = daftarGejala[session['gejalaKerusakan']]
   return render_template("diagnosa.html", pertanyaan = pertanyaan, name = name, link = url_for('box'))
   

#+++++++++++++++++++++UMUM++++++++++++++++++++++++++++++++++++++
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def home():
	return render_template('index.html')
	
@app.route('/about')
def about():
	return render_template('about.html')
	
@app.route('/anggota')
def anggota():
	return render_template('anggota.html')


		
if __name__ == "__main__":
    app.run()