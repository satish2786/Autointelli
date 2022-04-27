
def isPayloadValid(dPayload, lHeaders, lMandatory):
    if dPayload != {} and lHeaders != []:
        dPayload = {i.lower(): dPayload[i] for i in dPayload}
        lHeaders = [i.lower() for i in lHeaders]
        lMandatory = [i.lower() for i in lMandatory]
        lKey = [1 if eH in dPayload.keys() else 0 for eH in lHeaders]
        lVal = [0 if (dPayload[eM] == "" or dPayload[eM] is None) else 1 for eM in lMandatory]
        if 0 in lKey or 0 in lVal:
            return False
        else:
            return True
    else:
        return False 