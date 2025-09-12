package main

import (
	"os"
	"strings"
)

// getEnvWithDefault returns the value of an environment variable or a default value
func getEnvWithDefault(key string, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Config holds application configuration
type Config struct {
	ServerHost string
	ServerPort string
	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string
}

// GetConfig returns the application configuration
func GetConfig() *Config {
	return &Config{
		ServerHost: getEnvWithDefault("SERVER_HOST", "0.0.0.0"),
		ServerPort: getEnvWithDefault("SERVER_PORT", "8145"),
		DBHost:     getEnvWithDefault("DB_HOST", "localhost"),
		DBPort:     getEnvWithDefault("DB_PORT", "5432"),
		DBUser:     getEnvWithDefault("DB_USER", "postgres"),
		DBPassword: getEnvWithDefault("DB_PASSWORD", "postgres"),
		DBName:     getEnvWithDefault("DB_NAME", "smart_split"),
	}
}

// GetServerAddress returns the full server address
func (c *Config) GetServerAddress() string {
	return c.ServerHost + ":" + c.ServerPort
}

// GetAllowedOrigins returns the CORS allowed origins
func (c *Config) GetAllowedOrigins() []string {
	defaultOrigins := []string{
		"http://localhost:5173",
		"http://localhost:5174",
		"http://localhost:3000",
		"http://127.0.0.1:5173",
		"http://127.0.0.1:5174",
		"http://10.39.5.170:5173", // Your computer's IP
		"http://10.39.5.170:3000", // Your computer's IP
	}

	// Add any additional origins from environment
	if envOrigins := os.Getenv("ALLOWED_CORS_ORIGINS"); envOrigins != "" {
		additionalOrigins := strings.Split(envOrigins, ",")
		defaultOrigins = append(defaultOrigins, additionalOrigins...)
	}

	return defaultOrigins
}
