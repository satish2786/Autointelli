from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.perfrpt import perfreport as perf
import json
from datetime import datetime as dt
from jinja2 import Template
import base64
from io import BytesIO
import matplotlib.pyplot as plt, mpld3
import pdfkit
from flask import request

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

location = ''
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['onapploc']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

dIPFQDN = {'blr-': [{'host': '10.227.45.119', 'port': 9200}, {'host': '10.227.45.120', 'port': 9200}, {'host': '10.227.45.121', 'port': 9200}],
           'amd-': [{'host': '10.210.45.119', 'port': 9200}, {'host': '10.210.45.120', 'port': 9200}, {'host': '10.210.45.121', 'port': 9200}],
           'fbd-': [{'host': '10.195.45.119', 'port': 9200}, {'host': '10.195.45.120', 'port': 9200}, {'host': '10.195.45.121', 'port': 9200}],
           'mum-': [{'host': '10.239.45.218', 'port': 9200}, {'host': '10.239.45.219', 'port': 9200}, {'host': '10.239.45.220', 'port': 9200}, {'host': '10.239.45.221', 'port': 9200}, {'host': '10.239.45.222', 'port': 9200}, {'host': '10.239.45.223', 'port': 9200}]}

dIPFQDNDownload = {'blr-': {'fqdn': 'r2d2.nxtgen.com'},
           'amd-': {'fqdn': '61.0.172.106'},
           'fbd-': {'fqdn': '117.255.216.170'},
           'mum-': {'fqdn': '103.230.37.88'}}

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def generatePDF(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                # report_date = []
                # reportTraffic_Total_speed = []
                # reportTraffic_In_speed = []
                # reportTraffic_Out_speed = []
                # holdAllDate = []
                # allSuperDate = []
                AverageData, SumsData, LowHighData, plotters, bandPlotName, groupLowHigh, rowData = [], [], [], [], [], [], []

                out = json.loads(perf.perfDataLatest1(dPayload))
                if out['result'] == 'success':
                    reportData = out
                    rowData = out
                    SumsData = reportData['data']['Sums']
                    LowHighData = reportData['data']['LowHigh']

                    # GRAPH START
                    fig, ax = plt.subplots()
                    fig.set_size_inches(12, 7)
                    fig.autofmt_xdate()

                    indexzero = reportData['data']['plots'][0]
                    del reportData['data']['plots'][0]
                    RemovedTitle = reportData['data']['plots']

                    print(rowData["plotters"])
                    print(indexzero)
                    for item in rowData["plotters"]:
                        pos = indexzero.index(item)
                        tmpDate, tmpValue = [], []
                        for j in RemovedTitle:
                            tmpDate.append(j[0])
                            tmpValue.append(j[pos])
                        ax.plot(tmpDate, tmpValue, label=item)

                    ax.set_ylabel('Mbit/s')
                    ax.set_title('AutoIntelli Report')
                    ax.legend()

                    ax = plt.gca()
                    plt.xticks(rotation=70)
                    for label in ax.get_xaxis().get_ticklabels()[::2]:
                        label.set_visible(False)
                    for label in ax.get_xaxis().get_ticklabels()[::2]:
                        label.set_visible(False)
                    for label in ax.get_xaxis().get_ticklabels()[::2]:
                        label.set_visible(False)
                    for label in ax.get_xaxis().get_ticklabels()[::2]:
                        label.set_visible(False)
                    for label in ax.get_xaxis().get_ticklabels()[::2]:
                        label.set_visible(False)
                    #     plt.savefig('datagraph.jpg',dpi=100)

                    figfile = BytesIO()
                    plt.savefig(figfile, format='png')
                    figfile.seek(0)
                    figdata_png = base64.b64encode(figfile.getvalue())
                    # tmpfile = BytesIO()
                    # plt.savefig(tmpfile, format='png')
                    # encoded = base64.b64encode(tmpfile.getvalue())
                    # plt.show()

                    htmltemple = """
                                        <!doctype html>
                                        <html lang="en">

                                        <head>
                                          <meta charset="utf-8">
                                          <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                                          <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css"
                                            integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
                                          <title>Autointelli Report</title>
                                        </head>

                                        <body>


                                        <div class="graph">
                                                <img src="data:image/png;base64,{{fig}}">
                                        </div>

                                          <div class="SumsTable">
                                            <h2>Sums</h2>
                                            <table class="table">
                                              <tbody>
                                                {% for SumsTitle,SumsVal in reportData["data"]["Sums"].items() %}
                                                <tr>
                                                  <td> {{SumsTitle}} </td>
                                                  <td> {{SumsVal}}</td>
                                                </tr>
                                                {% endfor %}
                                              </tbody>
                                            </table>
                                          </div>

                                          <div class="AverageTable">
                                            <h2>Average</h2>
                                            <table class="table">
                                              <tbody>
                                                {% for AverageTitle,AverageVal in reportData["data"]["Average"].items() %}
                                                <tr>
                                                  <td>{{AverageTitle}}</td>
                                                  <td>{{AverageVal}}</td>
                                                </tr>
                                                {% endfor %}
                                              </tbody>
                                            </table>
                                          </div>

                                          <div class="LowHighTable">
                                            <h2>Low High</h2>
                                            <table class="table">
                                              <tbody>
                                                {% for LowHighTitle,LowHighVal in reportData["data"]["LowHigh"].items() %}
                                                <tr>
                                                  <td>{{LowHighTitle}} </td>
                                                  <td>Low: {{LowHighVal["low"]}}</td>
                                                  <td>High: {{LowHighVal["high"]}}</td>
                                                </tr>
                                                {% endfor %}
                                              </tbody>
                                            </table>
                                          </div>

                                          <div class="rowData">
                                            <h2>Row Data</h2>
                                            <table class="table">
                                              <tbody>
                                                {% for key in reportData["data"]["plots"] %}
                                                <tr>
                                                  {% for keys in key %}
                                                  <td>{{keys}}</td>
                                                  {% endfor %}
                                                </tr>
                                                {% endfor %}
                                              </tbody>
                                            </table>
                                            <div>
                                        </body>
                                        </html>
                                            """

                    template = Template(htmltemple)

                    template_render = template.render(
                        fig=figdata_png.decode('utf8'),
                        plotters=plotters,
                        bandPlotName=bandPlotName,
                        AverageData=AverageData,
                        SumsData=SumsData,
                        LowHighData=groupLowHigh,
                        payload=json.loads(dPayload),
                        reportData=rowData
                    )

                    options = {
                        "enable-local-file-access": None,
                        'margin-top': '0.50in',
                        'margin-bottom': '0.50in',
                        'margin-right': '0.10in',
                        'margin-left': '0.10in',
                        'encoding': "UTF-8",
                        'no-outline': None
                    }

                    pdfName = "PerformanceReport_" + str(int(dt.now().timestamp() * 1000000)) + ".pdf"
                    pdfPath = "/usr/share/nginx/html/downloads/" + pdfName
                    pdfkit.from_string(template_render, pdfPath, options=options)

                    return json.dumps({"result": "success",
                            "data": "https://{0}/downloads/".format(dIPFQDNDownload[location]['fqdn']) + pdfName})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to generate PDF, Try after sometimes.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing
