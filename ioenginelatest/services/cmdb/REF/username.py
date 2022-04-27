username="anand@AUTOINTELLIDEV.COM"
if("@" in username):
  username, domain = username.split("@")
  username = username+"{0}".format("@")+domain.upper()
  print(username)
else:
  print("Noooo")
