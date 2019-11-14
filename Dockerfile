FROM alpine:latest

COPY ./app /app
RUN apk add --no-cache python3 python3-dev py3-lxml py3-pip \
	&& if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi \
	&& if [ ! -e /usr/bin/pip ]; then ln -sf pip3 /usr/bin/pip ; fi \
	&& cd /app/ \
	&& pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& python setup.py install \
	&& rm -rf ./src

ENTRYPOINT ["cachealot"]
