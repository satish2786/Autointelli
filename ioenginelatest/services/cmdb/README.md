CMDB API DETAILS
----------------

* METHOD  : POST
* URL     : http://localhost:8000/cmdb/insert
* HEADERS : -H 'Host: cmdb' and  -H "Content-Type: application/json"
* BODY
{
        "ipaddress": "1.1.1.1",
        "hostname": "SRVNAGCMD001",
        "username": "automationuser",
        "password": "xxxxxxxxxxxxx"
}

Bash Method to TEST :  `curl -i -X POST http://localhost:8000/cmdb/insert -H 'Host: cmdb' --data @input.json -H "Content-Type: application/json"`
Where input.json is the file containing the above body
