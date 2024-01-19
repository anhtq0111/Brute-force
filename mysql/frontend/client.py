import requests
import json
import time
import streamlit as st

st.title('Brute-force')
if st.button('Init database'):
    url = "http://172.23.0.1:2410/init"
    headers = {"Content-Type": "application/json"}
    start = time.time()
    response = requests.get(url, headers=headers)
    end = time.time()
    if response.status_code == 200:
        if response.json()['result'] == 'success':
            st.success(f"Init database in {end - start} seconds")
        else: 
            st.error('Already init')
    else:
        st.error('Can not request')

option = st.selectbox("Choose option:", ('Login', 'Guess pass'))

if option == 'Login':
    username = st.text_input('Enter user name')
    password = st.text_input('Enter password')
    if st.button('Login'):
        data = {"username": username,
            "password": password}
        url = "http://172.23.0.1:2410/login"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            if response.json()['result'] == 'success':
                st.success(f"User ID: {response.json()['user_id']}")
            else: 
                st.error('Wrong username or password')
        else:
            st.error('Can not request')

elif option == 'Guess pass':
    username = st.text_input('Enter user name')

    if st.button('Guess'):
        data = {"username": username,}
        url = "http://172.23.0.1:2410/gess_pass"
        headers = {"Content-Type": "application/json"}
        start = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        end = time.time()
        if response.status_code == 200:
            if response.json()['result'] == 'success':
                st.success(f"Password: {response.json()['password']}. Total time: {end - start} seconds")
            else: 
                st.error('No User')
        else:
            st.error('Can not request')
    
