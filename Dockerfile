FROM python:3.10

ENV DASH_DEBUG_MODE False
COPY ./app /app
WORKDIR /app
RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--reload", "app:server"]