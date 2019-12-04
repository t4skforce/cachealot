FROM alpine:latest

COPY ./app /app
RUN apk add --no-cache python3 python3-dev py3-lxml py3-pip \
	&& if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi \
	&& if [ ! -e /usr/bin/pip ]; then ln -sf pip3 /usr/bin/pip ; fi \
	&& cd /app/ \
	&& pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& python setup.py install \
	&& rm -rf /app \
	&& apk del py3-pip

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
