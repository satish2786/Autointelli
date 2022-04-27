import psycopg2
import smtplib
from services.utils.decoder import decode, encode
from flask import request,jsonify, Blueprint
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_api = Blueprint('smtp_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
conn.autocommit = True
cur = conn.cursor()
cur.execute('select configip,configport,username,password,communicationtype from configuration where configname=\'SMTP\'')

smtpdata = cur.fetchall()
smtpdata = smtpdata[0]
smtpip = smtpdata[0]
smtpport = smtpdata[1]
smtpuser = smtpdata[2]
smtppass = smtpdata[3]
comm_type = smtpdata[4]

smtppass = decode('auto!ntell!',smtppass)



@smtp_api.route("/admin/api/v2/sendmail/", methods = ['post'])
def send_email():
    userdata = request.get_json()
    if ((len(userdata["To"])) or (len(userdata["Subject"])) or (len(userdata["Cc"])) or (len(userdata["HTML"])) ) == 0:
       return jsonify({"MSG" : "Required fields are empty","Errorcode" : "1"})
    else:
        to_add,sub,ccc,html_in = userdata['To'], userdata['Subject'], userdata['Cc'],userdata['HTML']
        msg = MIMEMultipart()
        msg['From'] = "EmailAdmin@autointelli.com"
        msg['To'] = to_add
        msg['Subject'] = sub
        msg['cc'] = ccc
        msg.attach(MIMEText(html_in, 'html'))
        if (comm_type == "smtp"):
            s = smtplib.SMTP(smtpip, smtpport)
        else:
            s  = smtplib.SMTP(smtpip, smtpport)
            s.starttls()
        try:
           s.login(smtpuser, smtppass)
        except Exception as e:
            return jsonify({"MSG":"Error in login","Return" : "Errorcode 421"})
        text = msg.as_string()
        # sending the mail
        try:
           s.sendmail(smtpuser, (to_add,ccc), text, html_in)
        except Exception as e:
            return jsonify({"MSG":"Unable to send message","Return" : "Error"+str(e)})
        #Terminating the session 
        finally:
               s.quit()
        return jsonify({"MSG":"Mail successfully send"})

