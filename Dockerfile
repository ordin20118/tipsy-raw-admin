#FROM python:3.8-alpine
FROM python:3.8

COPY manage.py gunicorn-cfg.py requirements.txt requirements_tipsyraw.txt ./
COPY app app
COPY authentication authentication
COPY core core
COPY raw_data_manager raw_data_manager
COPY utils utils
COPY logs logs

#RUN pip install --upgrade pip
RUN pip install -r requirements_tipsyraw.txt

#RUN python manage.py makemigrations
#RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
