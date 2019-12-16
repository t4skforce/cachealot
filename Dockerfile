FROM alpine:latest

COPY ./app /app
WORKDIR /app
RUN apk add --no-cache python3 py3-lxml \
	&& pip3 install -r requirements.txt --no-cache-dir \
	&& python3 setup.py install \
	&& rm -rf /app

ENV CACHEALOT_INTERVAL=5
ENV CACHEALOT_THREADS=10
ENV CACHEALOT_ENTRYPOINT=https://pypy.org
ENV CACHEALOT_QUERY=a
ENV CACHEALOT_SAMEDOMAIN=True
ENV CACHEALOT_MAX_LEVELS=-1
ENV CACHEALOT_STATIC=False
ENV CACHEALOT_CONNECTION_TIMEOUT=120.0
ENV CACHEALOT_READ_TIMEOUT=120.0
ENV CACHEALOT_USER_AGENT="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

ENTRYPOINT ["cachealot"]
CMD []
