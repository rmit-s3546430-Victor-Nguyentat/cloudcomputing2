from flask_bootstrap import Bootstrap
from flask import Flask, flash, redirect, render_template, request, url_for, session
import os, json, requests
from werkzeug.utils import secure_filename
import boto3


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'xvasodiasiud'

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
SECRET_KEY = ""
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# method to upload images to s3
def upload(photo, key:str, bucket = "cc-a2-image-bucket"):
    s3 = boto3.client('s3')
    s3.upload_file(photo, bucket, key)
    s3.put_object_acl(ACL='public-read', Bucket=bucket, Key=key)

# method gets user images from s3 bucket
# returns an array of URLs
def get_user_images(username: str):
    if username != "":
        bucket = "cc-a2-image-bucket"
        prefix = username + "/"
            
        imageURLs = []
        baseURL = "https://cc-a2-image-bucket.s3.amazonaws.com/"

        s3 = boto3.client('s3')
        response = s3.list_objects(Bucket=bucket, Prefix=prefix)
        # print(response)
        for item in response['Contents']:
            imageURLs.append(baseURL + item['Key'])
        print(imageURLs)
        return imageURLs
    else:
        print("Invalid Username")
        return []

# get image text
def get_image_text(username, imagename):
    
    request_url = "https://2tjcoizmkl.execute-api.us-east-1.amazonaws.com/dev/get-text?user=" + username + "&image=" + imagename 
    response = requests.get(request_url)
    return response.json()

# get image date
def get_image_date(username, imagename):
    bucket = "cc-a2-image-bucket"
    prefix = username + "/" + imagename

    s3 = boto3.client('s3')

    response = s3.list_objects(Bucket=bucket, Prefix=prefix)

    if 'Contents' not in response:
        return "No Data"
    else:
        return response['Contents'][0]['LastModified']

# translate text method
def translate_text(sourceText, sourceLanguageCode="en", targetLanguageCode="de"):
    translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)

    translation_result = translate.translate_text(Text=sourceText, SourceLanguageCode=sourceLanguageCode, TargetLanguageCode=targetLanguageCode)

    if 'TranslatedText' not in translation_result:
        return "Text could not be translated"
    else:
        return translation_result.get('TranslatedText')




@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
   
    if request.method == 'POST':
      if request.form['username'] != 'admin' or \
         request.form['password'] != 'admin':
         error = 'Invalid username or password. Please try again!'
      else:
         session['username'] = request.form['username']
         flash('You were successfully logged in')
         return redirect(url_for('upload_image'))

    return render_template('Login.html', error = error)

@app.route('/upload_image', methods = ['GET', 'POST'])
def upload_image():

    #Transition from view translations screen
    baseURL = "https://cc-a2-image-bucket.s3.amazonaws.com/admin/"
    imageURL = request.args.get('filename', None)
    if imageURL:
        image_name = imageURL.replace(baseURL, "")
        detectedText = get_image_text(session['username'], image_name)
        return render_template('Upload_Image.html', imageURL=imageURL, detectedText = detectedText, image_name = image_name)

    #If user initially sends the form
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

            # upload to s3
            upload(app.config['UPLOAD_FOLDER'] + "/" + filename, session['username'] + "/" + filename)

            #Detects writing from photo
            detectedText = get_image_text(session['username'], filename)
            return render_template('Upload_Image.html', filename=filename, detectedText = detectedText)  
    return render_template('Upload_Image.html')

@app.route('/view_translations')
def view_translations():

    #List of image URLs to display
    imageURLs = get_user_images(session['username'])

    #Removes base URL to get each individual image name
    imagenames = []
    baseURL = "https://cc-a2-image-bucket.s3.amazonaws.com/admin/"
    for imageURL in imageURLs:
        imagenames.append(imageURL.replace(baseURL, ""))

    #List of image dates
    image_dates = []
    for imagename in imagenames:
        image_dates.append(get_image_date(session['username'], imagename).strftime('%m/%d/%Y, %H:%M:%S')
)
    

    return render_template('View_Translations.html', imageURLs = imageURLs, image_dates = image_dates)

@app.route('/display_translation', methods = ['GET', 'POST'])
def display_translation():
    if request.method == 'POST':

        baseURL = "https://cc-a2-image-bucket.s3.amazonaws.com/admin/"
        select = request.form.get('lang_select')
        text = request.form.get('text')
        imageURL = request.form.get('imageURL')
        if imageURL == None:
            imageURL = baseURL + request.form.get('filename')

        print(select, text, imageURL)

        translated_text = translate_text(str(text), sourceLanguageCode="en",targetLanguageCode=str(select))

        return render_template('Upload_Image.html', imageURL=imageURL, detectedText = text, translated_text = translate_text(str(text), sourceLanguageCode="en",targetLanguageCode=str(select)))







@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)