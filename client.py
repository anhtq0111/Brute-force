import requests
import json
import time
def login(headers, username, password):
    url = "http://localhost:2410/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username,
            "password": password}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # result = json.load(response.text)
    # return response.text
    print(response.text)


def predict_password(headers, username):
    url = "http://localhost:2410/gess_pass"
    data = {"username": username,
            "password": password}
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()
    print("Total find time:", end_time - start_time, "seconds")
    print(response.text)

if __name__ == "__main__":
    
    username, password = input("Enter your username: ").strip().split()
    headers = {"Content-Type": "application/json"}

    login(headers, username, password)
    predict_password(headers, username)