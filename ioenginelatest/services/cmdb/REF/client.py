from CMDB import insertWindowsHost, osDetect
import time

r = osDetect.delay('192.168.1.115')
while r.ready() == False:
  time.sleep(2)
  print(r.get())
