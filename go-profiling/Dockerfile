# Dockerfile
FROM golang:1.22-alpine

WORKDIR /app

COPY go.mod .
COPY go.sum .

COPY . .

RUN go build -o profiling .

EXPOSE 8091

CMD ["./profiling"]
