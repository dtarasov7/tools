FROM golang:1.22-alpine AS builder

ENV GO111MODULE=on
RUN apk --no-cache add git && \
    go install -v github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@v0.5.1 && \
    go install -v github.com/google/go-jsonnet/cmd/jsonnet@7903819 && \
    go install -v github.com/brancz/gojsontoyaml@latest

FROM alpine:latest
RUN apk --no-cache add git gettext bash make jq gawk ca-certificates curl wget

COPY --from=builder /go/bin/* /usr/local/bin/
COPY ./entrypoint.sh /
RUN chmod a+x /usr/local/bin/jb /usr/local/bin/jsonnet /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--help" ]