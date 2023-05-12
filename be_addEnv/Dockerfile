FROM --platform=${TARGETPLATFORM:-linux/amd64} ghcr.io/openfaas/classic-watchdog:0.2.1 as watchdog
FROM debian:bullseye-slim
#FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3-alpine

ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Allows you to add additional packages via build-arg
ARG ADDITIONAL_PACKAGE

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog
RUN apt update -y
RUN apt install -y python3 python3-pip wget less procps
# RUN apk --no-cache add ca-certificates ${ADDITIONAL_PACKAGE}
# RUN apk add git


# Add non root user
RUN groupadd -r app && useradd app -r -g app

WORKDIR /home/app/

COPY index.py           .
COPY requirements.txt   .

RUN chown -R app /home/app && \
  mkdir -p /home/app/python && chown -R app /home/app
USER app
ENV PATH=$PATH:/home/app/.local/bin:/home/app/python/bin/
ENV PYTHONPATH=$PYTHONPATH:/home/app/python

RUN pip install -r requirements.txt --target=/home/app/python

RUN mkdir -p function
RUN touch ./function/__init__.py

WORKDIR /home/app/function/
COPY function/requirements.txt	.

RUN pip install -r requirements.txt --target=/home/app/python

WORKDIR /home/app/

USER root

COPY function           function

RUN adduser --system --gecos "steampipe user" --shell /bin/false --uid 9193 steampipe

RUN echo \
 && cd /tmp \
 && wget -nv https://github.com/turbot/steampipe/releases/download/v0.17.4/steampipe_linux_amd64.tar.gz \
 && tar xzf steampipe_linux_amd64.tar.gz \
 && mv steampipe /usr/local/bin/ \
 && rm -rf /tmp/steampipe_linux_amd64.tar.gz 

## Steampipe requirements
# RUN apk add gcompat libstdc++ libgcc musl libpq 
# Allow any user-id for OpenShift users.
USER app
ENV STEAMPIPE_UPDATE_CHECK=false

# disable telemetry
ENV STEAMPIPE_TELEMETRY=none
# ENV STEAMPIPE_LOG=trace

RUN steampipe plugin install aws
# RUN steampipe service start 
# RUN steampipe service stop

RUN mkdir /home/app/.aws
RUN echo "[default]" > /home/app/.aws/credentials

ENV write_debug="true"
ENV fprocess="python3 index.py"
EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
