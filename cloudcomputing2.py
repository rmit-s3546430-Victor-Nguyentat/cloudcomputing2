from flask import Flask, flash, redirect, render_template, request, url_for
app = Flask(__name__)
app.secret_key = 'xvasodiasiud'


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

@app.route('/upload_image')
def upload_image():
    return render_template('Upload_Image.html')

if __name__ == '__main__':
    app.run(debug = True)