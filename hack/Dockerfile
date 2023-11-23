ARG TARGET=archivematica-mcp-server

ARG UBUNTU_VERSION=22.04
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYTHON_VERSION=3.9
ARG NODE_VERSION=20
ARG PYENV_DIR=/pyenv
ARG SELENIUM_DIR=/selenium

# -----------------------------------------------------------------------------

FROM ubuntu:${UBUNTU_VERSION} AS pyenv-builder

ARG PYTHON_VERSION=3.9
ARG PYENV_DIR=/pyenv

ENV DEBIAN_FRONTEND=noninteractive
ENV PYENV_ROOT=${PYENV_DIR}/data
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN set -ex \
	&& apt-get --quiet --yes update \
	&& apt-get --quiet --yes --no-install-recommends install \
		build-essential \
		ca-certificates \
		curl \
		git \
		libbz2-dev \
		libffi-dev \
		libldap2-dev \
		liblzma-dev \
		libmysqlclient-dev \
		libncursesw5-dev \
		libreadline-dev \
		libsasl2-dev \
		libsqlite3-dev \
		libssl-dev \
		libxml2-dev \
		libxmlsec1-dev \
		libxslt1-dev \
		tk-dev \
		xz-utils \
		zlib1g-dev \
	&& rm --recursive --force /var/lib/apt/lists/* /var/cache/apt/*

RUN set -ex \
	&& curl --retry 3 --silent --location https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
	&& pyenv install ${PYTHON_VERSION} \
	&& pyenv global ${PYTHON_VERSION}

COPY requirements-dev.txt requirements-dev.txt

RUN set -ex \
	&& pyenv exec python${PYTHON_VERSION} -m pip install --upgrade pip setuptools \
	&& pyenv exec python${PYTHON_VERSION} -m pip install --requirement requirements-dev.txt \
	&& pyenv rehash

# -----------------------------------------------------------------------------

FROM ubuntu:${UBUNTU_VERSION} AS browsers-builder

ARG SELENIUM_DIR=/selenium

ENV DEBIAN_FRONTEND=noninteractive

RUN set -ex \
	&& apt-get --quiet --yes update \
	&& apt-get --quiet --yes --no-install-recommends install \
		ca-certificates \
		curl \
		jq \
	&& rm --recursive --force /var/lib/apt/lists/* /var/cache/apt/* \
	&& SELENIUM_CACHE=${SELENIUM_DIR}/cache \
	&& SELENIUM_BIN=${SELENIUM_DIR}/bin \
	&& mkdir --parents $SELENIUM_CACHE $SELENIUM_BIN \
	&& curl --retry 3 --silent --output $SELENIUM_BIN/selenium-manager --location https://github.com/SeleniumHQ/selenium/raw/trunk/common/manager/linux/selenium-manager \
	&& chmod +x $SELENIUM_BIN/selenium-manager \
	&& CHROME_OUTPUT=$($SELENIUM_BIN/selenium-manager --cache-path $SELENIUM_CACHE --browser chrome --output JSON) \
	&& FIREFOX_OUTPUT=$($SELENIUM_BIN/selenium-manager --cache-path $SELENIUM_CACHE --browser firefox --output JSON) \
	&& ln --symbolic $(echo $CHROME_OUTPUT | jq --raw-output '.result.browser_path') $SELENIUM_BIN/google-chrome \
	&& ln --symbolic $(echo $CHROME_OUTPUT | jq --raw-output '.result.driver_path') $SELENIUM_BIN/chromedriver \
	&& ln --symbolic $(echo $FIREFOX_OUTPUT | jq --raw-output '.result.browser_path') $SELENIUM_BIN/firefox \
	&& ln --symbolic $(echo $FIREFOX_OUTPUT | jq --raw-output '.result.driver_path') $SELENIUM_BIN/geckodriver

# -----------------------------------------------------------------------------

FROM node:${NODE_VERSION} AS archivematica-dashboard-frontend-builder

COPY src/dashboard/frontend /src/src/dashboard/frontend

WORKDIR /src/src/dashboard/frontend

RUN set ex \
	&& npm install --no-package-lock

# -----------------------------------------------------------------------------

FROM node:${NODE_VERSION} AS archivematica-dashboard-testing

ARG SELENIUM_DIR=/selenium
ENV PATH=${SELENIUM_DIR}/bin:$PATH

RUN set -ex \
	&& apt-get --quiet --yes update \
	&& apt-get --quiet --yes --no-install-recommends install \
		libasound2 \
		libdbus-glib-1-2 \
		libdrm2 \
		libgbm1 \
		libglib2.0-0 \
		libgtk-3-0 \
		libnss3 \
		libx11-xcb1 \
		libxcb1 \
		libxtst6 \
	&& rm --recursive --force /var/lib/apt/lists/* /var/cache/apt/*

COPY --chown=${USER_ID}:${GROUP_ID} --from=browsers-builder --link ${SELENIUM_DIR} ${SELENIUM_DIR}
COPY --chown=${USER_ID}:${GROUP_ID} --from=archivematica-dashboard-frontend-builder --link /src/src/dashboard/frontend/node_modules /src/src/dashboard/frontend/node_modules
COPY src/dashboard/frontend /src/src/dashboard/frontend

WORKDIR /src/src/dashboard/frontend

ENTRYPOINT ["npm", "run", "test-single-run"]

# -----------------------------------------------------------------------------

FROM ubuntu:${UBUNTU_VERSION} AS base

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYENV_DIR=/pyenv

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV PYENV_ROOT=${PYENV_DIR}/data
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN set -ex \
	&& apt-get --quiet --yes update \
	&& apt-get --quiet --yes --no-install-recommends install \
		apt-transport-https \
		build-essential \
		curl \
		gettext \
		git \
		gpg-agent \
		libbz2-dev \
		libffi-dev \
		liblzma-dev \
		libncursesw5-dev \
		libreadline-dev \
		libsqlite3-dev \
		libssl-dev \
		libxml2-dev \
		libxmlsec1-dev \
		locales \
		software-properties-common \
		tk-dev \
		xz-utils \
		zlib1g-dev \
	&& rm --recursive --force /var/lib/apt/lists/*

# Set the locale
RUN locale-gen en_US.UTF-8

# OS dependencies
COPY hack/osdeps.py /src/hack/osdeps.py
COPY src/dashboard/osdeps /src/src/dashboard/osdeps
COPY src/MCPServer/osdeps /src/src/MCPServer/osdeps
COPY src/MCPClient/osdeps /src/src/MCPClient/osdeps
RUN set -ex \
	&& curl --retry 3 --silent https://packages.archivematica.org/GPG-KEY-archivematica | apt-key add - \
	&& add-apt-repository --no-update --yes "deb [arch=amd64] http://packages.archivematica.org/1.15.x/ubuntu-externals jammy main" \
	&& add-apt-repository --no-update --yes "deb http://archive.ubuntu.com/ubuntu/ jammy multiverse" \
	&& add-apt-repository --no-update --yes "deb http://archive.ubuntu.com/ubuntu/ jammy-security universe" \
	&& add-apt-repository --no-update --yes "deb http://archive.ubuntu.com/ubuntu/ jammy-updates multiverse" \
	&& curl --retry 3 --silent --output /tmp/repo-mediaarea.deb --location https://mediaarea.net/repo/deb/repo-mediaarea_1.0-24_all.deb \
	&& dpkg --install /tmp/repo-mediaarea.deb \
	&& rm /tmp/repo-mediaarea.deb \
	&& apt-get --quiet --yes update \
	&& apt-get --quiet --yes --no-install-recommends install \
		libyaml-dev clamav \
	&& /src/hack/osdeps.py Ubuntu-22 1 | grep --invert-match --extended-regexp "nginx|postfix|python3.9-dev" | xargs apt-get --yes --no-install-recommends install \
	&& rm --recursive --force /var/lib/apt/lists/*

# Download ClamAV virus signatures
RUN freshclam --quiet

COPY --chown=${USER_ID}:${GROUP_ID} --from=pyenv-builder --link ${PYENV_DIR} ${PYENV_DIR}
COPY --chown=${USER_ID}:${GROUP_ID} . /src

RUN set -ex \
	&& groupadd --gid ${GROUP_ID} --system archivematica \
	&& useradd --uid ${USER_ID} --gid ${GROUP_ID} --home-dir /var/archivematica --system archivematica \
	&& mkdir --parents /var/archivematica/sharedDirectory \
	&& chown --recursive archivematica:archivematica /var/archivematica

USER archivematica

# -----------------------------------------------------------------------------

FROM base AS archivematica-mcp-client

ARG PYTHON_VERSION=3.9

ENV DJANGO_SETTINGS_MODULE settings.common
ENV PYTHONPATH /src/src/MCPClient/lib/:/src/src/MCPClient/lib/clientScripts:/src/src/archivematicaCommon/lib/:/src/src/dashboard/src/
ENV ARCHIVEMATICA_MCPCLIENT_ARCHIVEMATICACLIENTMODULES /src/src/MCPClient/lib/archivematicaClientModules
ENV ARCHIVEMATICA_MCPCLIENT_CLIENTASSETSDIRECTORY /src/src/MCPClient/lib/assets/
ENV ARCHIVEMATICA_MCPCLIENT_CLIENTSCRIPTSDIRECTORY /src/src/MCPClient/lib/clientScripts/

# Some scripts in archivematica-fpr-admin executed by MCPClient rely on certain
# files being available in this image (e.g. see https://git.io/vA1wF).
COPY src/archivematicaCommon/lib/externals/fido/ /usr/lib/archivematica/archivematicaCommon/externals/fido/
COPY src/archivematicaCommon/lib/externals/fiwalk_plugins/ /usr/lib/archivematica/archivematicaCommon/externals/fiwalk_plugins/

ENTRYPOINT pyenv exec python${PYTHON_VERSION} -m /src/src/MCPClient/lib/archivematicaClient.py

# -----------------------------------------------------------------------------

FROM base AS archivematica-mcp-server

ARG PYTHON_VERSION=3.9

ENV DJANGO_SETTINGS_MODULE settings.common
ENV PYTHONPATH /src/src/MCPServer/lib/:/src/src/archivematicaCommon/lib/:/src/src/dashboard/src/

ENTRYPOINT pyenv exec python${PYTHON_VERSION} -m /src/src/MCPServer/lib/archivematicaMCP.py

# -----------------------------------------------------------------------------

FROM base AS archivematica-dashboard

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYTHON_VERSION=3.9

USER root

RUN set -ex \
	&& internalDirs=' \
		/src/src/dashboard/frontend \
		/src/src/dashboard/src/static \
		/src/src/dashboard/src/media \
	' \
	&& mkdir --parents $internalDirs \
	&& chown --recursive archivematica $internalDirs

USER archivematica

COPY --chown=${USER_ID}:${GROUP_ID} --from=archivematica-dashboard-frontend-builder --link /src/src/dashboard/src/media/js/ /src/src/dashboard/src/media/js

WORKDIR /src/src/dashboard/src

ENV DJANGO_SETTINGS_MODULE settings.local
ENV PYTHONPATH /src/src/dashboard/src/:/src/src/archivematicaCommon/lib/
ENV AM_GUNICORN_BIND 0.0.0.0:8000
ENV AM_GUNICORN_CHDIR /src/src/dashboard/src
ENV FORWARDED_ALLOW_IPS *

RUN set -ex \
	&& ./manage.py collectstatic --noinput --clear \
	&& ./manage.py compilemessages

ENV DJANGO_SETTINGS_MODULE settings.production

EXPOSE 8000

ENTRYPOINT pyenv exec python${PYTHON_VERSION} -m gunicorn --config=/src/src/dashboard/install/dashboard.gunicorn-config.py wsgi:application

# -----------------------------------------------------------------------------

FROM base AS archivematica-tests

# -----------------------------------------------------------------------------

FROM ${TARGET}
