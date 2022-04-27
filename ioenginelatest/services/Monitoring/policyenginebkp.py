from services.utils.ConnLog import create_log_file
from services.utils import ConnPostgreSQL as pcon
import services.utils.LFColors as lfc

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return {"result": s, "data": x}

l = {'equal to': " = '{0}'", 'contains': " like '%{0}%'", 'starts with': " like '{0}%'", 'ends with': " like '%{0}'",
     'not equal to': " != '{0}'",
     'greater than': " > {0} ", 'greater than equal': " >= {0} ", 'less than': " < {0} ", 'less than equal': " <= {0}",
     }

def Validate(pDBCond, pDBvalue, pNewvalue):
    print("{0}:{1}:{2}".format(pDBvalue, pDBCond, pNewvalue))
    out = None
    if pDBCond == 'equal to':
        out = True if pDBvalue == pNewvalue else False
    elif pDBCond == 'contains':
        out = True if pDBvalue.__contains__(pNewvalue) else False
    elif pDBCond == 'starts with':
        out = True if pDBvalue.startswith(pNewvalue) else False
    elif pDBCond == 'ends with':
        out = True if pDBvalue.endswith(pNewvalue) else False
    elif pDBCond == 'not equal to':
        out = True if pDBvalue != pNewvalue else False
    elif pDBCond == 'greater than':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'greater than equal':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'less than':
        out = True if pDBvalue <= pNewvalue else False
    elif pDBCond == 'less than equal':
        out = True if pDBvalue <= pNewvalue else False
    print(out)
    return out

def addNewPolicy(d, overall):
    # Insert the policy as no rows returned
    print("New Policy Engine:")
    new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']} for x in d['Condition'][overall]}
    keys = list(new.keys())
    keys.sort()
    columns, values = [], []
    [columns.extend([k + "_cond", k + "_value"]) for k in keys]
    [values.extend([new[k]['Operator'], new[k]['Value']]) for k in keys]
    c, v = "", ""
    for i in range(0, len(columns)):
        if columns[i] == "value_value":
            c += columns[i] + ","
            v += str(values[i]) + ","
        else:
            c += columns[i] + ","
            v += "'" + values[i].replace("'", "''") + "',"

    iQuery = "insert into policyengine(overall, {0}, active_yn, applied_to_alert_total) values('{1}', {2}, '{3}', {4}) RETURNING pk_pk_id".format(
        c[:-1],
        overall,
        v[:-1],
        'Y',
        0
    )
    iRet = pcon.returnSelectQueryResultWithCommit(iQuery)
    if iRet['result'] == 'success':
        print("Policy Engine added successfully with id:{0}".format(iRet['data'][0]['pk_pk_id']))
        return {'result': 'success', 'data': 'Policy accepted', 'info': iRet['data'][0]['pk_pk_id']}
    else:
        return {'result': 'failure', 'data': 'Error while adding policy. {0}'.format(iRet['data']), 'info': ''}

def createPolicyEngine(d):
    try:

        # Sample Payload
        # d = {"Condition": {"ALL": [{"Key": "application", "operator": "starts with", "value": "IOSPLUSTE"},
        #                            {"Key": "description", "operator": "contains", "value": "contains"},
        #                            {"Key": "value", "operator": "greater than", "value": "10.1"}]
        #                    }
        #      }

        operatorFormatting = {'equal to': " = '{0}'", 'contains': " like '%{0}%'", 'starts with': " like '{0}%'", 'ends with': " like '%{0}'",
                              'not equal to': " != '{0}'",
                              'greater than': " > {0} ", 'greater than equal': " >= {0} ", 'less than': " < {0} ", 'less than equal': " <= {0}",
                              }

        # Check if same type of policy exists
        sQuery = "select * from policyengine where active_yn='Y' and "
        conds = []

        print("Looking for exact match")
        overall = list(d['Condition'].keys())[0]
        for eachField in d['Condition'][overall]:
            field = eachField['Key']
            operation = eachField['Operator']
            fvalue = eachField['Value']
            conds.append(" ({0}_value={1} and {2}_cond={3}) ".format(field, fvalue, field, operation))
        sQuery += " and ".join(conds)
        sRet = pcon.returnSelectQueryResult(sQuery)
        if sRet['result'] == 'success':
            print("Policy already exists")
            print("exit here")
            return {'result': 'failure', 'data': 'Policy already exists with same conditions', 'info': sRet['data']}
        print("Exact match failed")


        # Check for vice vera conditions
        print("""Get similar data from DB: 
                ALL=>get all data that matches with same filter and having other field as '' or null
                ANY=>get all data that matches any field that included in incomig filter""")
        setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline'}
        sQuery = "select * from policyengine where ("
        cond1, newL = [], []
        if overall == 'ALL':
            for eachField in d['Condition'][overall]:
                cond1.append(" ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                newL.append(eachField['Key'])
            for i in setMain.difference(set(newL)):
                cond1.append(" ({0}_cond = '' or {1}_cond is null) ".format(i, i))
            sQuery += " and ".join(cond1)
        elif overall == 'ANY':
            for eachField in d['Condition'][overall]:
                cond1.append(" ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                newL.append(eachField['Key'])
            sQuery += " or ".join(cond1)
        sQuery += ") and active_yn='Y'"
        print("{0}:{1}".format(overall, sQuery))
        dRet = pcon.returnSelectQueryResult(sQuery)
        print("Got similar data from DB:{0}".format(dRet['data']))
        if dRet['result'] == 'success':
            dFinal = {}

            # AND Condition
            if overall == 'ALL':
                print("Loop Over And Condition:")
                # db to new
                print("DB values compared with new value:")
                new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']}  for x in d['Condition'][overall]}
                print("new:{0}".format(new))
                parent = []
                for eachPE in dRet['data']:
                    if eachPE['overall'] == 'ANY':
                        continue
                    child = {}
                    for eachAttrib in new: # setMain:
                        _cond = eachPE[eachAttrib + '_cond']
                        _value = eachPE[eachAttrib + '_value']
                        child[eachAttrib] = Validate(_cond, _value, new[eachAttrib]['Value'])
                        child[eachAttrib + '_cond'] = _cond
                        child[eachAttrib + '_value'] = _value
                        child['id'] = eachPE['pk_pk_id']
                    parent.append(child)
                retCh = []
                for ch in parent:
                    if not 0 in [1 if ch[k] == True else 0 for k in new]:
                        print("Matching:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['d2n'] = retCh
                else:
                    dFinal['d2n'] = []

                # new to db
                print("New values compared with db value:")
                parent1 = []
                for eachPE in dRet['data']:
                    if eachPE['overall'] == 'ANY':
                        continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_pk_id']
                    parent1.append(child1)
                retCh = []
                for ch in parent1:
                    if not 0 in [1 if ch[k] == True else 0 for k in new]:
                        print("Matching & Waste of Keeping them:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['n2d'] = retCh
                else:
                    dFinal['n2d'] = []

                if len(dFinal['d2n']) == 0 and len(dFinal['n2d']) == 0:
                    return addNewPolicy(d, overall)
                    # return {'result': 'success', 'data': 'Policy accepted'}
                else:
                    return {'result': 'conflict', 'data': {'existing policy': dFinal['d2n'], 'overriding policy': dFinal['n2d']}}

            # OR Condition
            elif overall == 'ANY':
                print("Loop Over Or Condition:")
                # db to new
                print("DB values compared with new value:")
                new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']} for x in d['Condition'][overall]}
                print("new:{0}".format(new))
                parent = []
                for eachPE in dRet['data']:
                    if eachPE['overall'] == 'ALL':
                        continue
                    child = {}
                    for eachAttrib in new: # setMain:
                        _cond = eachPE[eachAttrib + '_cond']
                        _value = eachPE[eachAttrib + '_value']
                        child[eachAttrib] = Validate(_cond, _value, new[eachAttrib]['Value'])
                        child[eachAttrib + '_cond'] = _cond
                        child[eachAttrib + '_value'] = _value
                        child['id'] = eachPE['pk_pk_id']
                    parent.append(child)
                retCh = []
                for ch in parent:
                    if 1 in [1 if ch[k] == True else 0 for k in new]:
                        print("Matching:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['d2n'] = retCh
                else:
                    dFinal['d2n'] = []

                # new to db
                print("New values compared with db value:")
                parent1 = []
                for eachPE in dRet['data']:
                    if eachPE['overall'] == 'ALL':
                        continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_pk_id']
                    parent1.append(child1)
                retCh = []
                for ch in parent1:
                    if 1 in [1 if ch[k] == True else 0 for k in new]:
                        print("Matching & Waste of Keeping them:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['n2d'] = retCh
                else:
                    dFinal['n2d'] = []

                if len(dFinal['d2n']) == 0 and len(dFinal['n2d']) == 0:
                    return addNewPolicy(d, overall)
                    # return {'result': 'success', 'data': 'Policy accepted'}
                else:
                    return {'result': 'conflict', 'data': {'existing policy': dFinal['d2n'], 'overriding policy': dFinal['n2d']}}

        else:

            # Insert the policy as no rows returned
            return addNewPolicy(d, overall)
            # print("New Policy Engine:")
            # new = {x['Key']: {'operator': x['operator'], 'value': x['value']} for x in d['Condition'][overall]}
            # keys = list(new.keys())
            # keys.sort()
            # columns, values = [], []
            # [columns.extend([k + "_cond", k + "_value"]) for k in keys]
            # [values.extend([new[k]['operator'], new[k]['value']]) for k in keys]
            # c, v = "", ""
            # for i in range(0,len(columns)):
            #     if columns[i] == "value_value":
            #         c += columns[i] + ","
            #         v += values[i] + ","
            #     else:
            #         c += columns[i] + ","
            #         v += "'" + values[i] + "',"
            #
            # iQuery = "insert into policyengine(overall, {0}, active_yn) values('{1}', {2}, '{3}') RETURNING pk_pk_id".format(
            #     c[:-1],
            #     overall,
            #     v[:-1],
            #     'N'
            # )
            # iRet = pcon.returnSelectQueryResultWithCommit(iQuery)
            # if iRet['result'] == 'success':
            #     print("Policy Engine added successfully with id:{0}".format(iRet['data'][0]['pk_pk_id']))
            #     return {'result': 'success', 'data': 'Policy accepted', 'info': iRet['data'][0]['pk_pk_id']}
            # else:
            #     return {'result': 'failure', 'data': 'Error while adding policy. {0}'.format(iRet['data']), 'info': ''}

    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))
















