.PHONY: run build clean test

# Run the server in development mode
run:
	go run .

# Build the binary
build:
	go build -o smart-split-api .

# Clean build artifacts
clean:
	rm -f smart-split-api

# Install dependencies
deps:
	go mod tidy

# Run tests (when you add them)
test:
	go test ./...

# Start server in background
start:
	go run . &

# Stop server
stop:
	pkill -f "go run ." || true

# Restart server
restart: stop start
