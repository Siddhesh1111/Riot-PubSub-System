FROM python:3.10.0rc2-bullseye
COPY . /src
RUN pip install Flask
RUN pip install pymongo
CMD ["python","/src/first_flask_app.py"]