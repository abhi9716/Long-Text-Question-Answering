FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# for docker paths always define absolute paths
# copy the local requirements.txt file to the /app/requirements.txt in the container
COPY ./requirements.txt /myapp/requirements.txt

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# install the packages from the requirements.txt file in the container
RUN pip install -r /myapp/requirements.txt
RUN pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# RUN apt-get update && apt-get install -y \
# curl
# expose the port that uvicorn will run the app 
# EXPOSE 8000

# copy the local api/ folder to the /app folder in the container
COPY . /myapp

# inside a container default workdir is root(.) but for fastapi, it also look for main.py in /app
# if you are not saving main.py in root, /app or saving it in new folder inside root then uncomment below
WORKDIR /myapp/app