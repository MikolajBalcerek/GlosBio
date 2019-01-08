FROM python:3.7-alpine
LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

RUN apk --update-cache \
    add musl \
    linux-headers \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    # python3 \
    # python3-dev \
	freetype-dev \
	tini \
	ffmpeg

WORKDIR /opt/app

COPY Pipfile Pipfile

# RUN pip3 install --upgrade pip pipenv pipenv_to_requirements gunicorn && \
RUN pip3 install --upgrade pipenv_to_requirements gunicorn && \
    pipenv run pipenv_to_requirements && \
	pip3 install --no-cache -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/sh", "entrypoint.sh"]