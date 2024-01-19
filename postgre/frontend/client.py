import requests
import json
import time
import streamlit as st

st.title('Brute-force')
option = st.selectbox("Choose option:", ('Login', 'Guess pass'))

if option == 'Login':
    username = st.text_input('Enter user name')
    password = st.text_input('Enter password')
    if st.button('Login'):
        data = {"username": username,
            "password": password}
        url = "http://localhost:2410/login"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            if response.json()['result'] == 'success':
                st.success(f"User ID: {response.json()['user_id']}")
            else: 
                st.error('Wrong username or password')
        else:
            st.error('Can not request')

else:
    username = st.text_input('Enter user name')

    if st.button('Guess'):
        data = {"username": username,}
        url = "http://localhost:2410/gess_pass"
        headers = {"Content-Type": "application/json"}
        start = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        end = time.time()
        if response.status_code == 200:
            if response.json()['result'] == 'success':
                st.success(f"Password: {response.json()['password']}. Total time: {end - start}")
            else: 
                st.error('No User')
        else:
            st.error('Can not request')

