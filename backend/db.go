package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

var db *sql.DB

func dbHealthCheck() error {
	err := db.Ping()
	if err != nil {
		return fmt.Errorf("error pinging database: %v", err)
	}
	return nil
}

func initDB() error {
	host := getEnvWithDefault("DB_HOST", "localhost")
	port := getEnvWithDefault("DB_PORT", "5432")
	user := getEnvWithDefault("DB_USER", "postgres")
	password := getEnvWithDefault("DB_PASSWORD", "postgres")
	dbname := getEnvWithDefault("DB_NAME", "smart_split")

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("error opening database: %v", err)
	}

	// Test the connection
	err = db.Ping()
	if err != nil {
		return fmt.Errorf("error connecting to the database: %v", err)
	}

	// Create tables
	if err := createTables(); err != nil {
		return fmt.Errorf("error creating tables: %v", err)
	}

	log.Println("Successfully connected to database")
	return nil
}

func createTables() error {
	// Users table
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username TEXT UNIQUE NOT NULL,
			email TEXT UNIQUE NOT NULL,
			password_hash TEXT NOT NULL,
			created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			full_name TEXT,
			iban TEXT,
			bic TEXT
		)
	`)
	if err != nil {
		return fmt.Errorf("error creating users table: %v", err)
	}

	// Groups table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS groups (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			description TEXT,
			created_by INTEGER NOT NULL,
			invite_code TEXT UNIQUE,
			created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (created_by) REFERENCES users (id)
		)
	`)
	if err != nil {
		return fmt.Errorf("error creating groups table: %v", err)
	}

	// Group memberships table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS group_members (
			id SERIAL PRIMARY KEY,
			group_id TEXT NOT NULL,
			user_id INTEGER NOT NULL,
			joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
			FOREIGN KEY (user_id) REFERENCES users (id),
			UNIQUE(group_id, user_id)
		)
	`)
	if err != nil {
		return fmt.Errorf("error creating group_members table: %v", err)
	}

	log.Println("Database tables created successfully")
	return nil
}

func closeDB() {
	if db != nil {
		db.Close()
	}
}
