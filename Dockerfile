FROM python:3.6.8

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x entry-point.sh

CMD [ "./entry-point.sh" ]
