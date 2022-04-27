from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from services.utils.ConnLog import create_log_file
from services.utils import ConnPostgreSQL as pcon
import services.utils.LFColors as lfc
from flask import request
import json
from decimal import Decimal

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def lam_api_key_missing():
    return json.dumps({"result": "failure", "data": "api-key missing"})

def lam_api_key_invalid():
    return json.dumps({"result": "failure", "data": "invalid api-key"})

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return {"result": s, "data": x}

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

def addNewFilter(d, overall, action, filter_id):
    # Insert the filters as no rows returned
    print("New Filter:")
    new = {x['Key']: {'Operator': x['Operator'], 'Value': x['Value']} for x in d['Condition'][overall]}
    keys = list(new.keys())
    keys.sort()
    columns, values = [], []
    [columns.extend([k + "_cond", k + "_value"]) for k in keys]
    [values.extend([new[k]['Operator'], new[k]['Value']]) for k in keys]
    setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline'}.difference(set(keys))
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

        iQuery = "update filters set overall='{0}', {1}  where pk_filter_id={2} RETURNING pk_filter_id".format(
            overall,
            cond[:-2],
            filter_id
        )
    else:
        for i in range(0, len(columns)):
            if columns[i] == "value_value":
                c += columns[i] + ","
                v += str(values[i]) + ","
            else:
                c += columns[i] + ","
                v += "'" + values[i].replace("'", "''") + "',"

        iQuery = "insert into filters(overall, {0}, active_yn, total_event_filtered) values('{1}', {2}, '{3}', {4}) RETURNING pk_filter_id".format(
            c[:-1],
            overall,
            v[:-1],
            'Y',
            0
        )
    iRet = pcon.returnSelectQueryResultWithCommit(iQuery)
    if iRet['result'] == 'success':
        print("Filter added successfully with id:{0}".format(iRet['data'][0]['pk_filter_id']))
        return {'result': 'success', 'data': 'Filter accepted', 'info': iRet['data'][0]['pk_filter_id']}
    else:
        return {'result': 'failure', 'data': 'Error while adding filter. {0}'.format(iRet['data']), 'info': ''}

def createFilters(dPayload, action='insert', filter_id=0):
    try:

        d = dPayload['filters']

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
            queryUpdateCond = " pk_filter_id!={0} and ".format(filter_id)

        # Check if same type of filter exists
        sQuery = "select * from filters where {0} active_yn='Y' and ".format(queryUpdateCond)
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
            print("Filter already exists")
            print("exit here")
            return {'result': 'failure', 'data': 'Filter already exists with same conditions', 'info': sRet['data']}
        print("Exact match failed")


        # Check for vice vera conditions
        print("""Get similar data from DB: 
                ALL=>get all data that matches with same filter and having other field as '' or null
                ANY=>get all data that matches any field that included in incomig filter""")
        setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline'}
        sQuery = "select * from filters where {0} (".format(queryUpdateCond)
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
                        child['id'] = eachPE['pk_filter_id']
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
                    if eachPE['overall'] == 'ANY':
                        continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_filter_id']
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
                    return addNewFilter(d, overall, action, filter_id)
                    # return {'result': 'success', 'data': 'Filter accepted'}
                else:
                    return {'result': 'conflict', 'data': {'existing filter': dFinal['d2n'], 'overriding filter': dFinal['n2d']}}

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
                        child['id'] = eachPE['pk_filter_id']
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
                    if eachPE['overall'] == 'ALL':
                        continue
                    child1 = {}
                    for eachAttrib in new:
                        _cond = new[eachAttrib]['Operator']
                        _value = new[eachAttrib]['Value']
                        child1[eachAttrib] = Validate(_cond, _value, eachPE[eachAttrib + '_value'])
                        child1[eachAttrib + '_cond'] = eachPE[eachAttrib + '_cond']
                        child1[eachAttrib + '_value'] = eachPE[eachAttrib + '_value']
                        child1['id'] = eachPE['pk_filter_id']
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
                    return addNewFilter(d, overall, action, filter_id)
                    # return {'result': 'success', 'data': 'Filter accepted'}
                else:
                    return {'result': 'conflict', 'data': {'existing filter': dFinal['d2n'], 'overriding filter': dFinal['n2d']}}

        else:

            # Insert the filter as no rows returned
            return addNewFilter(d, overall, action, filter_id)

    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def getFilterList():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """select 
                            pk_filter_id, overall, 
                            COALESCE(machine_cond,'') machine_cond, COALESCE(machine_value,'') machine_value,
                            COALESCE(application_cond,'') application_cond, COALESCE(application_value,'') application_value,
                            COALESCE(description_cond,'') description_cond, COALESCE(description_value,'') description_value,
                            COALESCE(extra_description_cond,'') extra_description_cond, COALESCE(extra_description_value,'') extra_description_value,
                             COALESCE(value_cond,'') value_cond, COALESCE(cast(value_value as varchar),'') value_value,
                             COALESCE(cmdline_cond,'') cmdline_cond, COALESCE(cmdline_value,'') cmdline_value,
                             active_yn, total_event_filtered 
                            from filters order by pk_filter_id desc""" # where active_yn ='Y'
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    ind = dRet['data'][0].index('value_value')
                    for i in range(0, len(dRet['data'][1:])):
                        if isinstance(dRet['data'][i + 1][ind], Decimal):
                            dRet['data'][i + 1][ind] = float(dRet['data'][i + 1][ind])
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateFilter(filter_id, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                return createFilters(dPayload, action='update', filter_id=filter_id)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteFilter(filter_id, action):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                uQuery = "update filters set active_yn='{0}' where pk_filter_id={1}".format('Y' if action == 'on' else 'N', filter_id)
                dRet = pcon.returnInsertResult(uQuery)
                if dRet['result'] == 'success':
                    return json.dumps({'result': 'success', 'data': 'Filter {0}'.format('Activated' if action == 'on' else 'De-Activated')})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to remove the filter'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getArchieveData(filter_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select payload from filtered_records_24 where fk_filter_id={0} order by created_on desc".format(filter_id)
                dRet = pcon.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    l = []
                    for i in dRet['data']:
                        l.append(i['payload'])
                    return json.dumps({'result': 'success', 'data': l})
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing











