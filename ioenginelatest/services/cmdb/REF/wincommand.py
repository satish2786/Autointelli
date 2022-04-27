import winrm

s = winrm.Session('192.168.1.104', auth=('anand@autointellidev.com', 'Ositboit@2020'), transport='ntlm')
r = s.run_cmd('hostname')
print(r.status_code)
print(r.std_out.decode('utf-8').strip())
