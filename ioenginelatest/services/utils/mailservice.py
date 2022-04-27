import requests as req
import sys
from string import Template
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from services.utils import ConnPostgreSQL as conpost
from services.utils import ED_AES256 as aes

# class emailservice:

SMTP_IP, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_COMM_TYPE = "", "", "", "", ""
SMTP_FROM = "alerts@nxtgen.com"
template_html = """
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
<html xmlns='http://www.w3.org/1999/xhtml'>
   <head>
      <meta http-equiv='Content-Type' content='text/html; charset=utf-8' />
      <title>[SUBJECT]</title>
      <link href="https://fonts.googleapis.com/css?family=Montserrat:400,400i,500,500i,600,600i,700,700i,800,800i,900,900i&display=swap" rel="stylesheet">
      <style type='text/css'>
         body {
            font-family: 'Montserrat', sans-serif;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin:0 !important;
            text-align: justify;
            width: 100% !important;
            -webkit-text-size-adjust: 100% !important;
            -ms-text-size-adjust: 100% !important;
            -webkit-font-smoothing: antialiased !important;
         }
         .tableContent img {
            border: 0 !important;
            display: block !important;
            outline: none !important;
         }
         a{
            color:#382F2E;
         }
         p, h1{
            color:#382F2E;
            margin:0;
         }
         p{
            color:#4a4a4a;
            font-size:16px;
            font-weight:normal;
            line-height:27px;
            text-align: justify;
         }
         a.link1{
            color:#382F2E;
         }
         a.link2{
            font-size:16px;
            text-decoration:none;
            color:#ffffff;
         }
         h2{
            text-align:left;
            color:#222222;
            font-size:16px;
            font-weight:normal;
         }
         div,p,ul,h1{
         margin:0;
         }
         .bgBody{
               background: #ffffff;
         }
         .bgItem{
            background: #ffffff;
         }
         @media only screen and (max-width:480px){
            table[class="MainContainer"], td[class="cell"]{
               width: 100% !important;
               height:auto !important;
            }
            td[class="specbundle"]{
               width:100% !important;
               float:left !important;
               font-size:16px !important;
               /* line-height:17px !important; */
               display:block !important;
               padding-bottom:15px !important;
            }
            td[class="spechide"]{
               display:none !important;
            }
            img[class="banner"]{
               width: 100% !important;
               height: auto !important;
            }
            td[class="left_pad"] {
               padding-left:15px !important;
               padding-right:15px !important;
            }
         }
         @media only screen and (max-width:540px)
         {
            table[class='MainContainer'], td[class='cell']
            {
               width: 100% !important;
               height:auto !important;
            }
            td[class='specbundle']
            {
               width:100% !important;
               float:left !important;
               font-size:16px !important;
               line-height:27px !important;
               display:block !important;
               padding-bottom:15px !important;
            }
            td[class='spechide']
            {
               display:none !important;
            }
            img[class='banner']
            {
               width: 75% !important;
               height: auto !important;
            }
         }
         .content-footer p{
            font-size: 15px;
         }
      </style>
   </head>
   <body paddingwidth="0" paddingheight="0"   style="padding-top: 0; padding-bottom: 0; padding-top: 0; padding-bottom: 0; background-repeat: repeat; width: 100% !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; -webkit-font-smoothing: antialiased;" offset="0" toppadding="0" leftpadding="0">
      <table bgcolor="#ffffff" width="100%" border="0" cellspacing="0" cellpadding="0" class="tableContent" align="left" >
         <tbody>
            <tr>
               <td>
                  <table width="850" border="0" cellspacing="0" cellpadding="0" align="left" bgcolor="#ffffff" class="MainContainer">
                     <tbody>
                        <tr>
                           <td>
                              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                 <tbody>
                                    <tr>
                                       <td valign="top" width="40"></td>
                                       <td>
                                          <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                             <tbody>
                                                <!-- =============================== Header ====================================== -->
                                                <tr>
                                                   <td height='25' class="spechide"></td>
                                                   <!-- =============================== Body ====================================== -->
                                                </tr>
                                                <tr>
                                                   <td class='movableContentContainer ' valign='top'>
                                                      <div class="movableContent" style="border: 0px; padding-top: 0px; position: relative;">
                                                         <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                            <tbody>
                                                               <tr>
                                                                  <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                                      <tbody>
                                                                         <tr>
                                                                             <td  valign="top" width="100%" class="specbundle">
                                                                                 <div class="contentEditableContainer contentTextEditable">
                                                                                    <div class="contentEditable">
                                                                                       <p style='margin:0; text-align:center; color: #ffffff; background-color: #3F51B5;'><span class="specbundle2"><span class="font1"><b> Service Notification Manager - Autointelli</b></span></span></p>
                                                                                    </div>
                                                                                 </div>
                                                                              </td>
                                                                         </tr>
                                                                      </tbody>
                                                                  </table>
                                                               </tr>
                                                            </tbody>
                                                         </table>
                                                      </div>

                                                      <div class="movableContent" style="border: 0px; padding-top: 0px; position: relative;">
                                                         <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center">
                                                            <tr>
                                                               <td height='20'></td>
                                                            </tr>
                                                            <tr>
                                                               <td align='left'>
                                                                  <div class='contentEditableContainer contentTextEditable'>
                                                                     <div class='contentEditable'>
                                                                        <p >
                                                                              <b>$HTMLHeader</b>
                                                                              
                                                                           <br> <br> <br>

                                                                        </p>
                                                                     </div>
                                                                  </div>
                                                               </td>
                                                            </tr>
                                                            <tr>
                                                               <td>
                                                                     <p>$HTMLOutput</p>
                                                               </td>
                                                            </tr>
                                                            <tr>
                                                               <td height='55'></td>
                                                            </tr>
                                                         </table>
                                                      </div>
                                                      <div class="movableContent" style="border: 0px; padding-top: 0px; position: relative;">
                                                         <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                            <tbody>
                                                               <tr>
                                                                  <td>
                                                                     <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                                        <tbody>
                                                                           <tr>
                                                                              <td valign="top" class="specbundle">
                                                                                 <div class="contentEditableContainer contentTextEditable content-footer">
                                                                                    <div class="contentEditable" align='center'>
                                                                                       <p  style='text-align:left;color:#09090c;font-weight:normal;line-height:25px;'>
                                                                                          <span style='font-weight:bold; color:#09090c;'>Regards,</span><br><br>
                                                                                          <span style='font-weight:bold;'>NxtGen</span><br><br>
                                                                                          <br>
                                                                                      </p>
                                                                                    </div>
                                                                                 </div>
                                                                              </td>

                                                                           </tr>
                                                                        </tbody>
                                                                     </table>
                                                                  </td>
                                                               </tr>
                                                            </tbody>
                                                         </table>
                                                      </div>
                                                      <!-- =============================== footer ====================================== -->
                                                   </td>
                                                </tr>
                                             </tbody>
                                          </table>
                                       </td>
                                       <td valign="top" width="40">&nbsp;</td>
                                    </tr>
                                 </tbody>
                              </table>
                           </td>
                        </tr>
                     </tbody>
                  </table>
               </td>
            </tr>
         </tbody>
      </table>
   </body>
</html>     """

def getSMTPMETA():
    sQuery = "select configip ip, configport port, username, password, communicationtype commtype from configuration where configname='SMTP'"
    dRet = conpost.returnSelectQueryResult(sQuery)
    return dRet

def sendmail(sSubject, lTo, lCC, sBody):

    t = Template(template_html)
    #t = tBody
    userdata = {"To": ",".join(lTo),
                "From": SMTP_FROM,
                "Subject": sSubject,
                "HTML": t.substitute(HTMLHeader=sSubject,
                                         HTMLOutput=sBody),
                "Cc": ",".join(lCC)}

    to_add, sub, ccc, html_in = userdata['To'], userdata['Subject'], userdata['Cc'], userdata['HTML']
    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = to_add
    msg['Subject'] = sub
    msg['cc'] = ccc
    msg.attach(MIMEText(html_in, 'html'))
    s = smtplib.SMTP(SMTP_IP, SMTP_PORT)
    #s.set_debuglevel(1)
    s.ehlo()
    if s.has_extn('STARTTLS'):
        s.starttls()
        s.ehlo()
    try:
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
    except Exception as e:
        print(str(e))

    text = msg.as_string()
    # sending the mail
    try:
        s.sendmail(SMTP_FROM, (to_add,ccc), text)
    except Exception as e:
        print(str(e))

dRet = getSMTPMETA()
print(dRet)
if dRet["result"] == "success":
    SMTP_IP = dRet["data"][0]["ip"]
    SMTP_PORT = dRet["data"][0]["port"]
    SMTP_USERNAME = dRet["data"][0]["username"]
    k = '@ut0!ntell!'.encode()
    fromClient = dRet["data"][0]["password"].encode()
    pass_de = aes.decrypt(fromClient, k).decode('utf-8')
    SMTP_PASSWORD = pass_de
    SMTP_COMM_TYPE = dRet["data"][0]["commtype"]
    #print(SMTP_PASSWORD)
    #notes = "<table><tr> <td>Sample<td> <tr></table>"
    #notes = "Thanks for registering to https://r2d2.nxtgen.com/nxtgen <BR/>User this password <B>NxtGen@123</B> to do first login</BR>" + notes
    #sendmail("New User Registration", ["dinesh@autointelli.com"], ["dinesh@autointelli.com"], notes)
    #sendmail("New User Registration", ["dinesh@autointelli.com"], ["dinesh@autointelli.com"], "Thanks for registering to https://r2d2.nxtgen.com/nxtgen <BR/>User this password <B>NxtGen@123</B> to do first login")

