FROM python:3.8-slim
LABEL authors="kouroshsimpkins"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

ENV NAME World

CMD ["python", "app.py"]
