import subprocess

while 1:
  proc = subprocess.Popen(['curl -i -X POST http://localhost:8000/cmdb/insert -H \'Host: cmdb\' --data @input.json -H "Content-Type: application/json"'])
  out = proc.communicate()
  print(out)
