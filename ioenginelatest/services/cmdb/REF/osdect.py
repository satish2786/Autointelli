import nmap
nma = nmap.PortScannerAsync()


def callback_result(host, scan_result):
  print("-----------------------------")
  #print(host, scan_result)
  print(host, scan_result['scan'][host]['osmatch'][0]['osclass'][0]['osfamily'])

nma.scan(hosts='192.168.1.100-110', arguments='-O -p 22-443', callback=callback_result)
while nma.still_scanning():
  print("waiting >>>")
  nma.wait(5)

