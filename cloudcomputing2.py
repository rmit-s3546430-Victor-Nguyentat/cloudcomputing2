from flask import Flask, flash, redirect, render_template, request, url_for
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'xvasodiasiud'

UPLOAD_FOLDER = 'uploaded_images'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
SECRET_KEY = ""
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
   
    if request.method == 'POST':
      if request.form['username'] != 'admin' or \
         request.form['password'] != 'admin':
         error = 'Invalid username or password. Please try again!'
      else:
         flash('You were successfully logged in')
         return redirect(url_for('upload_image'))

    return render_template('Login.html', error = error)

@app.route('/upload_image', methods = ['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        print("IN POST METHOD")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("about to save")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_image', filename=filename))  
    return render_template('Upload_Image.html')

@app.route('/view_translations')
def view_translations():
    return render_template('View_Translations.html')

if __name__ == '__main__':
    app.run(debug = True)
    # host="0.0.0.0", port=80,