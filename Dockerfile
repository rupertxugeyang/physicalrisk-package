FROM python:3

COPY . /app

WORKDIR /app

RUN apt-get install -y libgeos-dev 

#specific version
RUN pip install pandas numpy psycopg2 h2o scipy typing datetime boto3 gdal

CMD python var.py

