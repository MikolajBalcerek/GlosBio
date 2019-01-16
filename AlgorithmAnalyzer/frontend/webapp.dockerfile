FROM node:11.6-alpine
LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

RUN apk update && \
	apk upgrade && \
    apk add --no-cache tini \
					   make \
					   python2 \
					   g++ \
					   gcc \
					   libgcc \
					   libstdc++ \
					   linux-headers \
					   python

WORKDIR /opt

COPY package.json package.json

RUN npm install && npm install -g serve

ENV PATH /data/node_modules/.bin:$PATH

WORKDIR /opt/app

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/sh", "entrypoint.sh"]