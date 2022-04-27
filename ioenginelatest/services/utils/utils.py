import services.utils.ED_AES256 as aes

def int2Alert(id):
    return 'AL' + str(id).rjust(13,'0')

def alert2Int(id):
    return int(id.strip('AL').strip('0'))

def int2Event(id):
    return 'EV' + str(id).rjust(13,'0')

def event2Int(id):
    return int(id.strip('EV').strip('0'))

def decodeAuto(password):
    k = '@ut0!ntell!'.encode()
    passwd = password.encode()
    return (aes.decrypt(passwd, k).decode('utf-8'))

def monitoringNameConvert(lVars=[], action = "to"):
    try:
        out = []
        if action == "to":
            for i in lVars:
                out.append(i.replace(' ','__space__').replace('(','__openbracket__').replace(')', '__closebracket__').replace('-','__iphen__'))
        elif action == "from":
            for i in lVars:
                out.append(i.replace('__space__',' ').replace('__openbracket__', '(').replace('__closebracket__', ')').replace('__iphen__', '-'))
        return out
    except Exception as e:
        return []

