FROM python:3.6-alpine
LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

RUN apk update && \
	apk upgrade && \
    apk add --no-cache musl \
                       linux-headers \
                       gcc \
                       g++ \
                       make \
                       gfortran \
                       openblas-dev \
	                   freetype-dev \
	                   tini \
	                   ffmpeg \
					   flac  && \
	apk add --no-cache hdf5-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing

WORKDIR /opt/app

COPY Pipfile Pipfile

RUN	pip3 install pipenv_to_requirements gunicorn && \
    pipenv run pipenv_to_requirements && \
    sed -i '/^tensorflow/d' requirements.txt && \
    pip3 install --no-cache -r requirements.txt && \
	pip3 install --no-cache https://github.com/better/alpine-tensorflow/releases/download/alpine3.7-tensorflow1.7.0/tensorflow-1.7.0-cp36-cp36m-linux_x86_64.whl

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/sh", "entrypoint.sh"]