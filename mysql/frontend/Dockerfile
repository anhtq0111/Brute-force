# start by pulling the python image
FROM python:3.9

# copy the requirements file into the image
COPY requirements.txt /usr/src/app/requirements.txt

# switch working directory
WORKDIR /usr/src/app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
# COPY . /app

EXPOSE 8501

ENV NAME World

# configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]

CMD ["streamlit", "run", "client.py", "--server.port=8501", "--server.address=0.0.0.0"]