# FROM python:3.7-alpine
# LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

# WORKDIR /opt/app

# RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

# RUN apk --update add --no-cache \
#     gcc \
#     freetype-dev \
# 	py-scipy

# RUN apk add --no-cache --virtual .build-deps \
#     musl-dev \
#     g++ 

# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# RUN pip --no-cache install pipenv pipenv_to_requirements

# COPY . .

# RUN pipenv run pipenv_to_requirements && sed -i '/scipy/d' requirements.txt

# RUN pip install --no-cache -r requirements.txt

# # RUN pipenv install -v --skip-lock

# RUN apk del .build-deps

# RUN apk add --no-cache tini

# ENTRYPOINT ["/sbin/tini", "--"]
# CMD ["python", "main.py"]

# =================

# FROM python:3.7

# LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

# WORKDIR /opt/app

# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# RUN pip --no-cache install pipenv pipenv_to_requirements

# COPY . .

# RUN pipenv run pipenv_to_requirements && sed -i '/scipy/d' requirements.txt

# RUN pip install --no-cache -r requirements.txt

# # RUN pipenv install -v --skip-lock

# RUN apk del .build-deps

# RUN apk add --no-cache tini

# ENTRYPOINT ["/sbin/tini", "--"]
# CMD ["python", "main.py"]

# ===============
FROM alpine:3.7
LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

RUN apk --update-cache \
    add musl \
    linux-headers \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    python3 \
    python3-dev \
	freetype-dev \
	tini \
	ffmpeg

RUN pip3 install --upgrade pip pipenv pipenv_to_requirements

WORKDIR /opt/app
COPY Pipfile Pipfile

RUN pipenv run pipenv_to_requirements
RUN pip3 install --no-cache -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python3", "main.py"]