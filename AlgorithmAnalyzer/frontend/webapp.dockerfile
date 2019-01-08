FROM node:11.6-alpine
LABEL maintainer="Stanisław Gołębiewski <stagol@st.amu.edu.pl>"

WORKDIR /opt/app

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

ADD package.json package.json

RUN npm install && npm install -g serve

ENTRYPOINT ["/sbin/tini", "--"]
# CMD ["serve", "-l", "tcp://0.0.0.0:3000", "-s", "build"]  npm run build
CMD ["/bin/sh", "entrypoint.sh"]