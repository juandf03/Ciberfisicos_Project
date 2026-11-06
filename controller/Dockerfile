FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/farm
COPY controller/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home farm && mkdir /data && chown farm /data
COPY controller/app ./app
COPY simulator ./simulator
USER 10001:10001
CMD ["python", "-m", "app.main"]
