FROM python:3.6-alpine

ENV INSTALL_PATH /persona_api
RUN mkdir -p ${INSTALL_PATH}
WORKDIR ${INSTALL_PATH}

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:8000 app:app