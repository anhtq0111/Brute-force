import requests
import json

def login(headers, username, password):
    url = "http://localhost:5000/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username,
            "password": password}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # result = json.load(response.text)
    # return response.text
    print(response.text)


def predict_password(headers, username):
    url = "http://localhost:5000/gess_pass"
    data = {"username": username,
            "password": password}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.text)

if __name__ == "__main__":
    
    username, password = input("Enter your username: ").strip().split()
    headers = {"Content-Type": "application/json"}

    login(headers, username, password)
    predict_password(headers, username)