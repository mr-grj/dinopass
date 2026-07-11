FROM docker:27-cli

RUN apk add --no-cache \
      docker-cli-compose \
      cosign \
      postgresql16-client \
      bash \
      curl \
      jq

WORKDIR /work

COPY docker/updater/updater.sh /usr/local/bin/updater.sh
RUN chmod +x /usr/local/bin/updater.sh

ENTRYPOINT ["/usr/local/bin/updater.sh"]
