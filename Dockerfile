FROM python:3.5.6-stretch

WORKDIR /usr/src/app

COPY dist/cbpi-0.0.1.tar.gz ./
RUN pip install cbpi-0.0.1.tar.gz --no-cache-dir

COPY . .

EXPOSE 8080

CMD [ "cbpi" ]
