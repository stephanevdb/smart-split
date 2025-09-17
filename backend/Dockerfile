FROM golang:1.21
WORKDIR /app
COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o /smart-split-backend
EXPOSE 8145
CMD ["/smart-split-backend"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8145/api/health || exit 1