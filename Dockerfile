FROM python:3.6

LABEL "maintainer FRBELLO AT CISCO DOT COM"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD [ "python" , "app.py" ]
