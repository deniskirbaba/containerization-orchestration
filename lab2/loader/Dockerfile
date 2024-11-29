FROM alpine:3.20.3

WORKDIR /loader

RUN apk add --no-cache git-lfs

VOLUME /loader/model

COPY load.sh .
RUN chmod +x load.sh

# Load model and tokenizer if needed
CMD ["./load.sh"]