FROM python:3.7-alpine

ARG SW_VERSION
ARG BUILD_DATE
ARG VCS_REF

# Image labeling
LABEL org.label-schema.name = "uptime-reporting" \
      org.label-schema.version = $SW_VERSION \
      org.label-schema.vendor = "Giacomo Lozito (https://github.com/giacomolozito)" \
      org.label-schema.vcs-url = "https://github.com/giacomolozito/uptime-reporting" \
      org.label-schema.vcs-ref = $VCS_REF \
      org.label-schema.build-date = $BUILD_DATE \
      org.label-schema.schema-version = "1.0"

COPY . /uptime-reporting
WORKDIR /uptime-reporting
RUN python setup.py install

ENTRYPOINT ["uptime-reporting"]
