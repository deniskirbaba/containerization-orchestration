FROM alpine:3.20.3

WORKDIR /loader

RUN apk add --no-cache git-lfs

VOLUME /loader/model

COPY load-model.sh .
RUN chmod +x load-model.sh

# Load model and tokenizer if needed
CMD ["./load-model.sh"]