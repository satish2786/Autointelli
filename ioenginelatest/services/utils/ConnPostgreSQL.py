import psycopg2
import json
from services.utils import decoder
from services.utils.ConnLog import create_log_file

import services.utils.LFColors as lfc
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

# Read configuration details from the config file
#cfgData = json.load(open('/usr/local/autointelli/ioengine/services/config/config.json', "r"))
cfgData = json.load(open('/etc/autointelli/autointelli.conf', "r"))

tDBUIConn = (cfgData['ui']['dbip'],
               cfgData['ui']['dbname'],
               cfgData['ui']['username'],
               decoder.decode("auto!ntell!", cfgData['ui']['password']),
               cfgData['ui']['dbport'])

tDBJBPMConn = (cfgData['jbpm']['dbip'],
               cfgData['jbpm']['dbname'],
               cfgData['jbpm']['username'],
               decoder.decode("auto!ntell!", cfgData['jbpm']['password']),
               cfgData['jbpm']['dbport'])

tDBJBPMCentralConn = (cfgData['jcentral']['dbip'],
               cfgData['jcentral']['dbname'],
               cfgData['jcentral']['username'],
               decoder.decode("auto!ntell!", cfgData['jcentral']['password']),
               cfgData['jcentral']['dbport'])

def returnDBParam(dbname="ui"):
    if dbname == "ui":
        return tDBUIConn
    elif dbname == "jbpm":
        return tDBJBPMConn
    elif dbname == "jcentral":
        return tDBJBPMCentralConn

def chkForNone(val):
    return ('' if val is None else val)

def returnInsertResult(sQuery, sDB="ui"):
    try:
        ll, result = [], {}
        iCount = 0
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        conn.commit()
        iCount = cur.rowcount
        conn.close()
        return {"result": "success", "data": iCount}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResult(sQuery, sDB="ui"):
    try:
        ll, result = [], {}
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        conn.close()
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            return {"result": "success", "data": ll}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResultGroupBy(sQuery, lGroupBy=[], sDB="ui"):
    try:
        ll, result, actualresult = [], {}, []
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        conn.close()
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            if len(lGroupBy) > 0:
                dTmp = {}
                for eachDict in ll:
                    sKey = "__".join([chkForNone(eachDict[eachKey]) for eachKey in lGroupBy])
                    if sKey in dTmp.keys():
                        lTmp = dTmp[sKey]
                        lTmp.append(eachDict)
                        dTmp[sKey] = lTmp
                    else:
                        dTmp[sKey] = [eachDict]
                actualresult = [eachValues for eachValues in dTmp.values()]
            return {"result": "success", "data": actualresult}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResultWithCommit(sQuery, sDB="ui"):
    try:
        ll, result = [], {}
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            return {"result": "success", "data": ll}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResultAsList(sQuery, sDB="ui"):
    try:
        ll, result = [], {}
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        conn.close()
        if len(rows) > 0:
            d = {cols[0]: [i[0] for i in rows]}
            return {"result": "success", "data": d}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResultAs2DList(sQuery, sDB="ui"):
    try:
        ll, result = [], {}
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        lFinal = [list(i) for i in rows]
        conn.close()
        if len(lFinal) > 0:
            lFinal.insert(0, cols)
            return {"result": "success", "data": lFinal}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}

def returnSelectQueryResultConvert2Col2Dict(sQuery, SortByVal=False, sDB="ui"):
    try:
        ll, result = [], {}
        tParam = returnDBParam(sDB)
        conn = psycopg2.connect(host=tParam[0], dbname=tParam[1], user=tParam[2], password=tParam[3], port=tParam[4])
        cur = conn.cursor()
        cur.execute(sQuery)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        lFinal = [list(i) for i in rows]
        conn.close()
        if len(lFinal) > 0:
            #lFinal.insert(0, cols)
            lKeys = [i[0] for i in lFinal]
            lValues = [i[1] for i in lFinal]
            retDict = dict(zip(lKeys, lValues))
            if SortByVal == True:
                retDict = [(k, retDict[k]) for k in sorted(retDict, key=retDict.get, reverse=True)]
            return {"result": "success", "data": retDict}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {"result": "failure", "data": str(e)}
