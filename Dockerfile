FROM python:3.9-slim

COPY manage.py gunicorn-cfg.py requirements_tipsyraw.txt ./
COPY app app
COPY authentication authentication
COPY core core
COPY raw_data_manager raw_data_manager
COPY utils utils
COPY logs logs

RUN apt update && apt install libpq-dev gcc curl -y
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements_tipsyraw.txt
# 한번만 다운 받으면 되기에 주석 처리
RUN curl -LOJ https://tipsy-pro.s3.ap-northeast-2.amazonaws.com/model/u2net.onnx
RUN mkdir -p root/.u2net/
RUN mv u2net.onnx ./root/.u2net/

#RUN python manage.py makemigrations
#RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
