FROM python:3.8-slim

WORKDIR /code/app
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install -r /code/requirements.txt
RUN pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# expose the port that uvicorn will run the app
EXPOSE 8000

# 
COPY ./app/ /code/app

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["python", "main.py"]


