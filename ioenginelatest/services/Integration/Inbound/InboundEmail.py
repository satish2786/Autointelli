import imaplib
import configparser
import os
import email
import email.parser
import requests
import json
import re
import pysnow

def open_connection(verbose=False):
    # Connect to the server
    hostname = "mail.autointelli.com"
    if verbose:
        print('Connecting to', hostname)
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = 'aidev@autointelli.com'
    password = 'LSBA3dCDxBZy'
    if verbose:
        print('Logging in as', username)
    connection.login(username, password)
    return connection

def validatePEAttribInternal(pattern, sample):
    try:
        subs = []
        try:
            ret = re.search(pattern, sample, re.M | re.I)
            if ret is None:
                return {'result': 'failure', 'data': "Pattern doesn't match with sample"}
            elif (ret is not None) and (ret.lastindex is None):
                return {'result': 'success', 'data': {'groups': subs}}
            else:
                for i in range(0, ret.lastindex):
                    subs.append(ret.group(i + 1))
                return {'result': 'success', 'data': {'groups': subs}}
        except Exception as e:
            return {'result': 'failure', 'data': str(e)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def createSNOW(CALLER, SDESC, DDESC):
    try:
        c = pysnow.Client(instance='dev69860', user='admin', password='bz7EfIzNOf5R')
        incident = c.resource(api_path='/table/incident')
        new_record = {
            'caller_id': CALLER,
            'short_description': SDESC,
            'description': DDESC
        }
        result = incident.create(payload=new_record)
        print("SNOW Result: {0}".format(result))
        INC = result.one()['number']
        return {'result': 'success', 'data': INC}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

if __name__ == '__main__':
    c = open_connection(verbose=False)
    # c.select('INBOX', readonly=True)
    c.select('INBOX')
    typ, data = c.search(None, '(UNSEEN)')
    print(data)
    print('Number of Emails: {0}'.format(data))
    for num in data[0].split():
        print("Inside: {0}".format(num))
        typ, msg_data = c.fetch(num, '(RFC822)')
        print("After fetch: typ: {0}, msg: {1}".format(typ, msg_data))
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                email_parser = email.parser.BytesFeedParser()
                email_parser.feed(response_part[1])
                msg = email_parser.close()
                if msg['Subject'].lower().__contains__('password reset'): # or msg['Subject'].lower().__contains__('account unlock'):
                    # idd = validatePEAttribInternal('.*<(.*)>', msg['From'])
                    idd = validatePEAttribInternal('"(.*) .*".*', msg['From'])
                    print("Extracted caller:{0}".format(idd))
                    if idd['result'] == 'success' and len(idd['data']['groups']) > 0:
                        # idd['data']['groups'][0] = 'Alissa Mountjoy'
                        caller = idd['data']['groups'][0].lower()
                        sdesc = "Reset the password for {0} on Active Directory".format(idd['data']['groups'][0].lower())
                        desc = sdesc
                        print(caller, sdesc, desc)
                        retSNOW = createSNOW(caller, sdesc, desc)
                        # retSNOW = {'result': 'success', 'data': 1234}
                        if retSNOW['result'] == 'success':
                            print("Incident created caller:{0}, desc:{1} => inc: {2}".format(caller, sdesc, retSNOW['data']))
                        else:
                            print("Incident creation failed caller:{0}, desc:{1} => reason: {2}".format(caller, sdesc, retSNOW['data']))
                        # This is for event receiver push
                        # eventJSON = {'priority': '1',
                        #        'Msg_updated_time': msg['Date'],
                        #        'Machine': '172.16.1.5',
                        #        'Application': 'Active Directory',
                        #        'Value': msg['From'],
                        #        'Cmdline': 'PASSWORD RESET',
                        #        'Description': "Reset the password for {0} on Active Directory".format(idd['data']['groups'][1]),
                        #        'Extra_Description': msg['Subject'],
                        #        'severity': 'CRITICAL',
                        #        'source': 'EMAIL',
                        #        'event_created_time': 0,
                        #        'customer_id': 'Anonymous'}
                        # print(eventJSON)
                    else:
                        print("Reply to the sender asking to send the right details which is missing.")
                elif msg['Subject'].lower().__contains__('account unlock'):
                    idd = validatePEAttribInternal('"(.*) .*".*', msg['From'])
                    print("Extracted caller:{0}".format(idd))
                    if idd['result'] == 'success' and len(idd['data']['groups']) > 0:
                        # idd['data']['groups'][0] = 'Alissa Mountjoy'
                        caller = idd['data']['groups'][0].lower()
                        sdesc = "Account Unlock for {0} on Active Directory".format(idd['data']['groups'][0].lower())
                        desc = sdesc
                        print(caller, sdesc, desc)
                        retSNOW = createSNOW(caller, sdesc, desc)
                        # retSNOW = {'result': 'success', 'data': 1234}
                        if retSNOW['result'] == 'success':
                            print("Incident created caller:{0}, desc:{1} => inc: {2}".format(caller, sdesc,
                                                                                             retSNOW['data']))
                        else:
                            print("Incident creation failed caller:{0}, desc:{1} => reason: {2}".format(caller, sdesc,
                                                                                                        retSNOW[
                                                                                                            'data']))
                    else:
                        print("Reply to the sender asking to send the right details which is missing.")

        print("mark as read: {0}".format(num))
        result, data = c.uid('STORE', num, '+FLAGS', '\\Seen')
        print(result, data)
    # result, data = c.uid('STORE', num, '+FLAGS', 'r(\\Seen)')
    # result, data = c.uid('STORE', num, '+FLAGS', '\\Seen') # latest
    # payload = {'title': msg['subject'], 'description': ''.join(msg['subject'].split('\r\n'))}
    # headers = {'Content-Type': 'Application/json'}
    # print(payload)
    # print("http://127.0.0.1:5011/Interaction/email_classify_ticket")
    # output = requests.post("http://127.0.0.1:5011/Interaction/email_classify_ticket", data=json.dumps(payload),
    #                        headers=headers)
    # print(output.text)