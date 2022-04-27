from services.utils.ConnLog import create_log_file
from services.utils import ConnPostgreSQL as pcon
import services.utils.LFColors as lfc
from decimal import Decimal
from datetime import datetime as dt
import json
from services.EAM import reservice as res

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

alert_details = ''

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

def singleQuoteIssue(value):
    if not type(value) == type(None):
        return value.replace("'", "''").strip()
    else:
        return ""

def getNextDay(day):
    if day == "mon":
        return "tue"
    if day == "tue":
        return "wed"
    if day == "wed":
        return "thu"
    if day == "thu":
        return "fri"
    if day == "fri":
        return "sat"
    if day == "sat":
        return "sun"
    if day == "sun":
        return "mon"

# dayIndex = {'sun':}

def whichIsGreater(a, b, position):
    db = dt(1, 1, 1, int(a.split(':')[0]), int(a.split(':')[1]))
    new = dt(1, 1, 1, int(b.split(':')[0]), int(b.split(':')[1]))
    if position == "start":
        if db <= new:
            return True
        else:
            return False
    elif position == "end":
        if db >= new:
            return True
        else:
            return False

def getPattern(p):
    dbPatterns = []
    dbs = p.split('__')[0].split('_')[0]
    dbe = p.split('__')[1].split('_')[0]
    if dbs == dbe:
        dbPatterns.append(dbs)
    elif getNextDay(dbs) == dbe:
        dbPatterns.extend([dbs, dbe])
    else:
        dbPatterns.append(dbs)
        while (not getNextDay(dbs) == dbe):
            dbPatterns.append(getNextDay(dbs))
            dbs = getNextDay(dbs)
        dbPatterns.append(dbe)
    return ",".join(dbPatterns)

def s2d(s):
    try:
        return Decimal(s)
    except Exception as e:
        return s

def Validate(pDBCond, pDBvalue, pNewvalue, pColumn="", alert_payload=""):
    # Day & time
    if pColumn == "day_time":
        if pDBCond == 'between':
            db = getPattern(pDBvalue)
            new = getPattern(pNewvalue)
            if db == new:
                s = whichIsGreater(pDBvalue.split('__')[0].split('_')[1], pNewvalue.split('__')[0].split('_')[1], "start")
                e = whichIsGreater(pDBvalue.split('__')[1].split('_')[1], pNewvalue.split('__')[1].split('_')[1], "end")
                return True if s == True and e == True  else False
            elif db.__contains__(new):
                if db.startswith(new):
                    s = whichIsGreater(pDBvalue.split('__')[0].split('_')[1], pNewvalue.split('__')[0].split('_')[1], "start")
                    return True if s == True else False
                elif db.endswith(new):
                    e = whichIsGreater(pDBvalue.split('__')[1].split('_')[1], pNewvalue.split('__')[1].split('_')[1], "end")
                    return True if e == True else False
                else:
                    return True
            else:
                return False
    # Other
    else:
        print("{0}:{1}:{2}".format(pDBvalue, pDBCond, pNewvalue))
        out = None
        if pDBCond == 'equal to':
            out = True if s2d(pDBvalue) == s2d(pNewvalue) else False
        elif pDBCond == 'contains':
            out = True if pDBvalue.__contains__(pNewvalue) else False
        elif pDBCond == 'starts with':
            out = True if pDBvalue.startswith(pNewvalue) else False
        elif pDBCond == 'ends with':
            out = True if pDBvalue.endswith(pNewvalue) else False
        elif pDBCond == 'not equal to':
            out = True if s2d(pDBvalue) != s2d(pNewvalue) else False
        elif pDBCond == 'greater than':
            out = True if s2d(pDBvalue) > s2d(pNewvalue) else False
        elif pDBCond == 'greater than equal':
            out = True if s2d(pDBvalue)-1 >= s2d(pNewvalue) else False
        elif pDBCond == 'less than':
            out = True if s2d(pDBvalue) < s2d(pNewvalue) else False
        elif pDBCond == 'less than equal':
            out = True if s2d(pDBvalue)+1 <= s2d(pNewvalue) else False
        elif pDBCond == 'regex':
            try:
                db_reg = pDBvalue
                new_reg = pNewvalue
                value = alert_payload[pColumn]
                ret = res.validatePEAttribInternal({'pattern': db_reg, 'sample': value})
                if ret['result'] == 'success':
                    out = True
                else:
                    out = False
            except Exception as e:
                logERROR(str(e))
                out = False
        print(out)
        return out

def addNewPolicy(d, overall, action, policy_id, batch_flag, batch_js):
    # Insert the policy as no rows returned
    print("New Policy Engine:")
    new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']} for x in d['Condition'][overall]}
    keys = list(new.keys())
    keys.sort()
    columns, values = [], []
    [columns.extend([k + "_cond", k + "_value"]) for k in keys]
    [values.extend([new[k]['Operator'], new[k]['Value']]) for k in keys]
    # setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline', 'day_time'}.difference(set(keys))
    setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline', 'day_time',
               'priority', 'id', 'asset_number', 'region', 'asset_state', 'version', 'package',
               'pac_ver', 'pac_ver_no', 'status_update', 'status', 'additional_props', 'modified_by'}.difference(set(keys))
    c, v, iQuery, cond = "", "", "", ""

    if action == 'update':
        for i in range(0, len(columns)):
            if columns[i] == "value_value":
                cond += "{0}={1}, ".format(columns[i], str(values[i]))
            else:
                cond += "{0}='{1}', ".format(columns[i], values[i].replace("'", "''"))
        for i in setMain:
            if i == "value":
                cond += "value_cond=null, value_value=null, "
            else:
                cond += "{0}=null, {1}=null, ".format(i + "_cond", i + "_value")

        iQuery = "update policyengine set overall='{0}', vars_payload='{3}', {1}, batch_flag='{4}', batch_payload='{5}'  where pk_pk_id={2} RETURNING pk_pk_id".format(
            overall,
            cond[:-2],
            policy_id,
            json.dumps(d).replace("'", "''"),
            batch_flag,
            json.dumps(batch_flag).replace("'", "''")
        )
    else:
        for i in range(0, len(columns)):
            if columns[i] == "value_value":
                c += columns[i] + ","
                v += str(values[i]) + ","
            else:
                c += columns[i] + ","
                v += "'" + values[i].replace("'", "''") + "',"

        iQuery = "insert into policyengine(overall, {0}, active_yn, applied_to_alert_total, sample_payload, vars_payload, batch_flag, batch_payload) values('{1}', {2}, '{3}', {4}, '{5}', '{6}', '{7}', '{8}') RETURNING pk_pk_id".format(
            c[:-1],
            overall,
            v[:-1],
            'Y',
            0,
            json.dumps(alert_details).replace("'", "''"),
            json.dumps(d).replace("'", "''"),
            batch_flag,
            json.dumps(batch_js).replace("'", "''")
        )

    iRet = pcon.returnSelectQueryResultWithCommit(iQuery)
    if iRet['result'] == 'success':
        print("Policy Engine added successfully with id:{0}".format(iRet['data'][0]['pk_pk_id']))
        return {'result': 'success', 'data': 'Policy accepted', 'info': iRet['data'][0]['pk_pk_id']}
    else:
        return {'result': 'failure', 'data': 'Error while adding policy. {0}'.format(iRet['data']), 'info': ''}

def createPolicyEngine(d, action='insert', policy_id=0, alert_info='', batch_flag='N', batch_json={}):
    global alert_details
    alert_details = alert_info

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

        # Only update works
        queryUpdateCond = ""
        if action == 'update':
            queryUpdateCond = " pk_pk_id!={0} and ".format(policy_id)

        # Check if same type of policy exists
        sQuery = "select * from policyengine where {0} active_yn='Y' and ".format(queryUpdateCond)
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
        setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline', 'day_time',
                   'priority', 'id', 'asset_number', 'region', 'asset_state', 'version', 'package',
                   'pac_ver', 'pac_ver_no', 'status_update', 'status', 'additional_props', 'modified_by'}

        # AND & AND, OR & OR
        sQuery = "select * from policyengine where {0} (".format(queryUpdateCond)
        cond1, newL = [], []
        if overall == 'ALL':
            for eachField in d['Condition'][overall]:
                cond1.append(" ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                newL.append(eachField['Key'])
            for i in setMain.difference(set(newL)):
                cond1.append(" ({0}_cond = '' or {1}_cond is null) ".format(i, i))
            sQuery += " and ".join(cond1)
            sQuery += ") and lower(overall)='all'"
        elif overall == 'ANY':
            for eachField in d['Condition'][overall]:
                cond1.append(" ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                newL.append(eachField['Key'])
            sQuery += " or ".join(cond1)
            sQuery += ") and lower(overall)='any'"
        sQuery += " and active_yn='Y'"

        # AND & OR, OR & AND
        s2Query = ""
        if (overall == 'ALL' and len(d['Condition'][overall]) == 1) or (overall == 'ANY'):
            s2Query += "select * from policyengine where {0} (".format(queryUpdateCond)
            cond1, newL = [], []
            if overall == 'ALL':
                if len(d['Condition'][overall]) == 1:
                    for eachField in d['Condition'][overall]:
                        cond1.append(
                            " ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                        newL.append(eachField['Key'])
                    s2Query += " and ".join(cond1)
                    s2Query += ") and lower(overall)='any'"
            elif overall == 'ANY':
                if len(d['Condition'][overall]) == 1:
                    for eachField in d['Condition'][overall]:
                        cond1.append(
                            " ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'], eachField['Key']))
                        newL.append(eachField['Key'])
                    for i in setMain.difference(set(newL)):
                        cond1.append(" ({0}_cond = '' or {1}_cond is null) ".format(i, i))
                    s2Query += " and ".join(cond1)
                    s2Query += ") and lower(overall)='all'"
                elif len(d['Condition'][overall]) > 1:
                    for MOR in d['Condition'][overall]:
                        cond1, newL = [], []
                        s2Query += "("
                        for eachField in [MOR]:
                            cond1.append(" ({0}_cond != '' and {1}_cond is not null) ".format(eachField['Key'],
                                                                                              eachField['Key']))
                            newL.append(eachField['Key'])
                        for i in setMain.difference(set(newL)):
                            cond1.append(" ({0}_cond = '' or {1}_cond is null) ".format(i, i))
                        s2Query += " and ".join(cond1)
                        s2Query += ") or "
                    s2Query = s2Query[:-3]
                    s2Query += ") and lower(overall)='all'"
            s2Query += " and active_yn='Y'"

        
        fQuery = "select * from ({0}  {1}) A".format(sQuery, ('union all {0}'.format(s2Query) if s2Query != '' else ''))
        print("{0}:{1}".format(overall, fQuery))
        dRet = pcon.returnSelectQueryResult(fQuery)
        print("Got similar data from DB:{0}".format(dRet['data']))
        if dRet['result'] == 'success':
            dFinal = {}

            # AND Condition
            if overall == 'ALL':
                print("Loop Over And Condition:")
                # db to new
                print("DB values compared with new value:")
                new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']} for x in d['Condition'][overall]}
                print("new:{0}".format(new))
                parent = []
                for eachPE in dRet['data']:
                    # if eachPE['overall'] == 'ANY':
                    #     continue
                    child = {}
                    for eachAttrib in new: # setMain:
                        _cond = eachPE[eachAttrib + '_cond']
                        _value = eachPE[eachAttrib + '_value']
                        if eachAttrib.lower().strip() == 'value':
                            child[eachAttrib] = Validate(_cond, new[eachAttrib]['Value'], _value, eachAttrib, alert_details)
                        else:
                            child[eachAttrib] = Validate(_cond, _value, new[eachAttrib]['Value'], eachAttrib, alert_details)
                        child[eachAttrib + '_cond'] = _cond
                        child[eachAttrib + '_value'] = _value
                        child['id'] = eachPE['pk_pk_id']
                    parent.append(child)
                retCh = []
                for ch in parent:
                    if not 0 in [1 if ch[k] == True else 0 for k in new]:
                        if 'value_value' in ch.keys():
                            ch['value_value'] = float(ch['value_value']) if isinstance(ch['value_value'], Decimal) else ch['value_value']
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
                    # if eachPE['overall'] == 'ANY':
                    #     continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        if eachAttrib.lower().strip() == 'value':
                            child1[eachAttrib] = Validate(_cond, new[eachAttrib]['Value'], _value, eachAttrib, alert_details)
                        else:
                            child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'], eachAttrib, eachPE['sample_payload'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_pk_id']
                    parent1.append(child1)
                retCh = []
                for ch in parent1:
                    if not 0 in [1 if ch[k] == True else 0 for k in new]:
                        if 'value_value' in ch.keys():
                            ch['value_value'] = float(ch['value_value']) if isinstance(ch['value_value'], Decimal) else ch['value_value']
                        print("Matching & Waste of Keeping them:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['n2d'] = retCh
                else:
                    dFinal['n2d'] = []

                if len(dFinal['d2n']) == 0 and len(dFinal['n2d']) == 0:
                    return addNewPolicy(d, overall, action, policy_id, batch_flag, batch_json)
                    # return addNewPolicy(d, overall)
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
                    # if eachPE['overall'] == 'ALL':
                    #     continue
                    child = {}
                    for eachAttrib in new: # setMain:
                        _cond = eachPE[eachAttrib + '_cond']
                        _value = eachPE[eachAttrib + '_value']
                        if eachAttrib.lower().strip() == 'value':
                            child[eachAttrib] = Validate(_cond, new[eachAttrib]['Value'], _value, eachAttrib, alert_details)
                        else:
                            child[eachAttrib] = Validate(_cond, _value, new[eachAttrib]['Value'], eachAttrib, alert_details)
                        child[eachAttrib + '_cond'] = _cond
                        child[eachAttrib + '_value'] = _value
                        child['id'] = eachPE['pk_pk_id']
                    parent.append(child)
                retCh = []
                for ch in parent:
                    if 1 in [1 if ch[k] == True else 0 for k in new]:
                        if 'value_value' in ch.keys():
                            ch['value_value'] = float(ch['value_value']) if isinstance(ch['value_value'], Decimal) else ch['value_value']
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
                    # if eachPE['overall'] == 'ALL':
                    #     continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        if eachAttrib.lower().strip() == 'value':
                            child1[eachAttrib] = Validate(_cond, new[eachAttrib]['Value'], _value, eachAttrib, alert_details)
                        else:
                            child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'], eachAttrib, eachPE['sample_payload'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_pk_id']
                    parent1.append(child1)
                retCh = []
                for ch in parent1:
                    if 1 in [1 if ch[k] == True else 0 for k in new]:
                        if 'value_value' in ch.keys():
                            ch['value_value'] = float(ch['value_value']) if isinstance(ch['value_value'], Decimal) else ch['value_value']
                        print("Matching & Waste of Keeping them:{0}".format(ch))
                        retCh.append(ch)
                if len(retCh) > 0:
                    dFinal['n2d'] = retCh
                else:
                    dFinal['n2d'] = []

                if len(dFinal['d2n']) == 0 and len(dFinal['n2d']) == 0:
                    return addNewPolicy(d, overall, action, policy_id, batch_flag, batch_json)
                    # return addNewPolicy(d, overall)
                    # return {'result': 'success', 'data': 'Policy accepted'}
                else:
                    return {'result': 'conflict', 'data': {'existing policy': dFinal['d2n'], 'overriding policy': dFinal['n2d']}}

        else:

            # Insert the policy as no rows returned
            return addNewPolicy(d, overall, action, policy_id, batch_flag, batch_json)

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
















