package config

import (
	"os"
)

type Config struct {
	DatabaseURL string
	Port        string
	Environment string
}

func LoadConfig() *Config {
	return &Config{
		DatabaseURL: getEnv("DATABASE_URL", "host=localhost port=5432 user=postgres password=postgres dbname=biblioteca sslmode=disable"),
		Port:        getEnv("PORT", "3000"),
		Environment: getEnv("ENVIRONMENT", "development"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
