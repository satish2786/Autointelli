from flask import Flask, jsonify
from nltk import word_tokenize
from nltk.corpus import stopwords
import re, string
from fuzzywuzzy import process


# test = input('description:')
stop_lst = ['warning', 'critical', 'ok']
stop_words = stopwords.words('english')
stp = stop_words.extend(stop_lst)
# print(stop_words)

def validateSuppression(alert_desc, comparison_list):
    """Method : This method is used to validate whether a given event can be supression with the open events"""

    #alert_desc="WARNING - load average per CPU: 0.13, 0.10, 0.10"
    alert_desc = "Service RemoteRegistry (Remote Registry) is not running (startup type automatic)"
    comparison_list = [
        "WARNING - load average per CPU: 0.09, 0.17, 0.40",
        "CRITICAL - load average per CPU: 0.84, 0.42, 0.22",
        "OK - load average per CPU",
        "WARNING - load average per CPU: 0.54, 0.21, 0.14",
        "WARNING - load average per CPU: 0.29, 0.14, 0.11",
        "OK - load average per CPU: 0.10, 0.07, 0.10"
    ]

    des = re.sub(r'\d+', '', str(alert_desc))
    stop = stop_words + list(string.punctuation)
    in_put = []
    test_input = [i for i in word_tokenize(des.lower()) if i not in stop]
    in_put.append(' '.join(test_input))
    print('out', in_put)

    desc = []
    for i in comparison_list:
        k = re.sub(r'\d+', '', str(i))
        desc.append(k)

    key_sent = []
    for w in range(0, len(desc)):
        output = [i for i in word_tokenize((desc[w]).lower()) if i not in stop]
        extracted_text = (' '.join(output))
        key_sent.append(extracted_text)
    # print('key_sentence',key_sent)

    f = process.extract(str(in_put), key_sent)
    for i in range(0, len(f)):
        print("f", f[i][1])
        if f[i][1] >= 100:
            print("no log suppress")
            return jsonify("no log suppress")
        elif f[i][1] <= 70:
            print("add to present table")
            return jsonify("add to present table")
