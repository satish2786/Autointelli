import os
os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/.vaultpassdb"

os.system("echo -e \"ansible_user\": anand@AUTOINTELLIDEV.COM\n\"ansible_pass\": Ositboit@2020 >> test.yml")
os.system("ansible-vault encrypt test.yml")
