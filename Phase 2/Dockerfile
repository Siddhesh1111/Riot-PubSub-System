FROM python:3.10.0rc2-bullseye
COPY . /src
                  


RUN pip install  Flask-SocketIO==4.3.1
RUN pip install  python-engineio==3.13.2
RUN pip install  python-socketio==4.6.0
RUN pip install  Flask==2.0.2
RUN pip install  Flask-SocketIO==4.3.1
RUN pip install  google-api-core==2.1.1
RUN pip install  google-api-python-client==2.26.1
RUN pip install  google-auth==2.3.0
RUN pip install  google-auth-httplib2==0.1.0
RUN pip install  googleapis-common-protos==1.53.0
RUN pip install  httplib2==0.20.1
RUN pip install  oauthlib==3.1.1
RUN pip install  pip==21.2.4
RUN pip install  pymongo==3.12.0
RUN pip install  pyparsing==2.4.7

CMD ["python","/src/first_flask_app.py"]