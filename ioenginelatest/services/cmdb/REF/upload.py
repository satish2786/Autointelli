from flask import Flask, render_template, request
from werkzeug import secure_filename
import os

UPLOAD_FOLDER = '/tmp/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload')
def upload_file1():
   return  '''
<html>
   <body>
        <form action = "http://192.168.56.101:8000/cmdb/insertBulk" method = "POST"
                 enctype = "multipart/form-data">
         <input type = "file" name = "file" />
         <input type = "submit"/>
      </form>

   </body>
</html>
'''
	
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3890, debug=True)
