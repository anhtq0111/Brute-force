# start by pulling the python image
FROM python:3.10.2-bullseye

# copy the requirements file into the image
COPY requirements.txt /usr/src/app/requirements.txt

# switch working directory
WORKDIR /usr/src/app

# install the dependencies and packages in the requirements file
RUN  pip3 install -r requirements.txt

# # copy every content from the local file to the image
COPY . .

ENV NAME World


CMD ["python", "server.py" ]