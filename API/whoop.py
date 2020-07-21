import requests



whoop_url = "https://api-7.whoop.com/users/27265/cycles"

whoop_login = "https://app.whoop.com/login"
PARAMS = {"username":"","password":"#","grant_type":"password","issueRefresh":False}

r = requests.get(url = whoop_login, params = PARAMS) 

# stat = r.status()
data = r.json()
print(data)
if __name__ == '__main__':
    print("hello")