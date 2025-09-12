package main

import (
	"crypto/rand"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"log"
	mathrand "math/rand"
	"net/http"
	"time"
)

var Version = "1.0.0"
var Debug = true

// User represents a user in the system
type User struct {
	ID        int       `json:"id"`
	Username  string    `json:"username"`
	Email     string    `json:"email"`
	FullName  string    `json:"full_name"`
	IBAN      string    `json:"iban"`
	BIC       string    `json:"bic"`
	CreatedAt time.Time `json:"created_at"`
}

// LoginRequest represents a login request
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// RegisterRequest represents a registration request
type RegisterRequest struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
	FullName string `json:"full_name"`
	IBAN     string `json:"iban"`
	BIC      string `json:"bic"`
}

// UpdateProfileRequest represents a profile update request
type UpdateProfileRequest struct {
	FullName string `json:"full_name"`
	IBAN     string `json:"iban"`
	BIC      string `json:"bic"`
}

// Group represents a group in the system
type Group struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	CreatedBy   int       `json:"created_by"`
	InviteCode  string    `json:"invite_code"`
	CreatedAt   time.Time `json:"created_at"`
	MemberCount int       `json:"member_count"`
}

// CreateGroupRequest represents a group creation request
type CreateGroupRequest struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// UpdateGroupRequest represents a group update request
type UpdateGroupRequest struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// GroupMember represents a group member
type GroupMember struct {
	ID       int       `json:"id"`
	GroupID  string    `json:"group_id"`
	UserID   int       `json:"user_id"`
	JoinedAt time.Time `json:"joined_at"`
	User     *User     `json:"user,omitempty"`
}

// JoinGroupRequest represents a request to join a group
type JoinGroupRequest struct {
	InviteCode string `json:"invite_code"`
}


var appConfig = GetConfig()
var AllowedCorsOrigins = appConfig.GetAllowedOrigins()

// Helper function to hash password
func hashPassword(password string) string {
	hash := sha256.Sum256([]byte(password))
	return hex.EncodeToString(hash[:])
}

// Helper function to generate random token
func generateToken() string {
	b := make([]byte, 32)
	rand.Read(b)
	return hex.EncodeToString(b)
}

// Helper function to get user by username
func getUserByUsername(username string) (*User, error) {
	var user User
	err := db.QueryRow(`
		SELECT id, username, email, full_name, iban, bic, created_at 
		FROM users 
		WHERE username = $1
	`, username).Scan(&user.ID, &user.Username, &user.Email, &user.FullName, &user.IBAN, &user.BIC, &user.CreatedAt)

	if err != nil {
		return nil, err
	}
	return &user, nil
}

// Helper function to get user by ID
func getUserByID(id int) (*User, error) {
	var user User
	err := db.QueryRow(`
		SELECT id, username, email, full_name, iban, bic, created_at 
		FROM users 
		WHERE id = $1
	`, id).Scan(&user.ID, &user.Username, &user.Email, &user.FullName, &user.IBAN, &user.BIC, &user.CreatedAt)

	if err != nil {
		return nil, err
	}
	return &user, nil
}

// Helper function to generate random group ID
func generateGroupID() string {
	const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	const length = 8
	
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[mathrand.Intn(len(charset))]
	}
	return string(b)
}

// Helper function to generate invite code
func generateInviteCode() string {
	b := make([]byte, 6)
	rand.Read(b)
	return hex.EncodeToString(b)[:6]
}

// Helper function to get groups by user ID
func getGroupsByUserID(userID int) ([]Group, error) {
	rows, err := db.Query(`
		SELECT g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at,
		       COUNT(gm.user_id) as member_count
		FROM groups g
		LEFT JOIN group_members gm ON g.id = gm.group_id
		WHERE g.id IN (
			SELECT group_id FROM group_members WHERE user_id = $1
		)
		GROUP BY g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at
		ORDER BY g.created_at DESC
	`, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []Group
	for rows.Next() {
		var group Group
		err := rows.Scan(&group.ID, &group.Name, &group.Description, &group.CreatedBy,
			&group.InviteCode, &group.CreatedAt, &group.MemberCount)
		if err != nil {
			return nil, err
		}
		groups = append(groups, group)
	}
	return groups, nil
}

// Helper function to get group by ID
func getGroupByID(id string) (*Group, error) {
	var group Group
	err := db.QueryRow(`
		SELECT g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at,
		       COUNT(gm.user_id) as member_count
		FROM groups g
		LEFT JOIN group_members gm ON g.id = gm.group_id
		WHERE g.id = $1
		GROUP BY g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at
	`, id).Scan(&group.ID, &group.Name, &group.Description, &group.CreatedBy,
		&group.InviteCode, &group.CreatedAt, &group.MemberCount)

	if err != nil {
		return nil, err
	}
	return &group, nil
}

// Helper function to get group by invite code
func getGroupByInviteCode(inviteCode string) (*Group, error) {
	var group Group
	err := db.QueryRow(`
		SELECT g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at,
		       COUNT(gm.user_id) as member_count
		FROM groups g
		LEFT JOIN group_members gm ON g.id = gm.group_id
		WHERE g.invite_code = $1
		GROUP BY g.id, g.name, g.description, g.created_by, g.invite_code, g.created_at
	`, inviteCode).Scan(&group.ID, &group.Name, &group.Description, &group.CreatedBy,
		&group.InviteCode, &group.CreatedAt, &group.MemberCount)

	if err != nil {
		return nil, err
	}
	return &group, nil
}

// Helper function to check if user is member of group
func isUserMemberOfGroup(userID int, groupID string) (bool, error) {
	var count int
	err := db.QueryRow(`
		SELECT COUNT(*) FROM group_members 
		WHERE user_id = $1 AND group_id = $2
	`, userID, groupID).Scan(&count)

	if err != nil {
		return false, err
	}
	return count > 0, nil
}

// Helper function to add user to group
func addUserToGroup(userID int, groupID string) error {
	_, err := db.Exec(`
		INSERT INTO group_members (group_id, user_id) 
		VALUES ($1, $2)
	`, groupID, userID)
	return err
}

// Helper function to remove user from group
func removeUserFromGroup(userID int, groupID string) error {
	_, err := db.Exec(`
		DELETE FROM group_members 
		WHERE user_id = $1 AND group_id = $2
	`, userID, groupID)
	return err
}

// Helper function to get group members
func getGroupMembers(groupID string) ([]GroupMember, error) {
	rows, err := db.Query(`
		SELECT gm.id, gm.group_id, gm.user_id, gm.joined_at,
		       u.username, u.email, u.full_name
		FROM group_members gm
		JOIN users u ON gm.user_id = u.id
		WHERE gm.group_id = $1
		ORDER BY gm.joined_at ASC
	`, groupID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var members []GroupMember
	for rows.Next() {
		var member GroupMember
		var user User
		err := rows.Scan(&member.ID, &member.GroupID, &member.UserID, &member.JoinedAt,
			&user.Username, &user.Email, &user.FullName)
		if err != nil {
			return nil, err
		}
		user.ID = member.UserID
		member.User = &user
		members = append(members, member)
	}
	return members, nil
}

func main() {
	// Initialize database
	if err := initDB(); err != nil {
		log.Printf("Failed to initialize database: %v", err)
		// Continue running the server even if DB fails
	}
	defer closeDB()

	r := gin.Default()

	config := cors.Config{
		AllowOrigins:     []string{"*"}, // Allow all origins for development
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"},
		AllowHeaders:     []string{"*"}, // Allow all headers
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: false, // Set to false when using wildcard origin
		MaxAge:           12 * 3600,
	}
	r.Use(cors.New(config))

	// Health check endpoint
	r.GET("/api/health", func(c *gin.Context) {
		dbStatus := "ok"
		if err := dbHealthCheck(); err != nil {
			dbStatus = "error"
			log.Printf("Database health check failed: %v", err)
		}

		c.JSON(http.StatusOK, gin.H{
			"status":   "ok",
			"database": dbStatus,
			"message":  "API is running",
			"version":  Version,
		})
		if Debug {
			log.Printf("Health check response: %+v", gin.H{
				"status":   "ok",
				"database": dbStatus,
				"message":  "API is running",
				"version":  Version,
			})
		}
	})

	// Authentication endpoints
	r.POST("/api/auth/register", func(c *gin.Context) {
		var req RegisterRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Check if username or email already exists
		var exists int
		err := db.QueryRow("SELECT 1 FROM users WHERE username = $1 OR email = $2", req.Username, req.Email).Scan(&exists)
		if err == nil {
			c.JSON(http.StatusConflict, gin.H{"error": "Username or email already exists"})
			return
		}

		// Hash password and create user
		passwordHash := hashPassword(req.Password)
		var userID int
		err = db.QueryRow(`
			INSERT INTO users (username, email, password_hash, full_name, iban, bic, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)
			RETURNING id
		`, req.Username, req.Email, passwordHash, req.FullName, req.IBAN, req.BIC).Scan(&userID)

		if err != nil {
			log.Printf("Error creating user: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
			return
		}

		user, err := getUserByID(userID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve user"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{
			"message": "User created successfully",
			"user":    user,
		})
	})

	r.POST("/api/auth/login", func(c *gin.Context) {
		var req LoginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Check credentials
		var passwordHash string
		var userID int
		err := db.QueryRow("SELECT id, password_hash FROM users WHERE username = $1", req.Username).Scan(&userID, &passwordHash)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
			return
		}

		if hashPassword(req.Password) != passwordHash {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
			return
		}

		user, err := getUserByID(userID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve user"})
			return
		}

		// Generate JWT token
		token, err := GenerateToken(user.ID, user.Username)
		if err != nil {
			log.Printf("Error generating token: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Login successful",
			"user":    user,
			"token":   token,
		})
	})

	// Google OAuth endpoint
	r.POST("/api/auth/google", func(c *gin.Context) {
		var req struct {
			AccessToken string `json:"access_token"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Verify Google access token
		// In a production app, you would verify the token with Google's API
		// For now, we'll create a mock user based on the token
		// You should implement proper Google token verification here

		// Mock user creation for demo purposes
		// In production, extract user info from Google's userinfo endpoint
		username := "google_user_" + generateToken()[:8]
		email := "user@example.com" // Extract from Google userinfo
		fullName := "Google User"   // Extract from Google userinfo

		// Check if user already exists (by email in a real implementation)
		var existingUser User
		err := db.QueryRow("SELECT id, username, email, full_name, iban, bic, created_at FROM users WHERE email = $1", email).Scan(
			&existingUser.ID, &existingUser.Username, &existingUser.Email, &existingUser.FullName,
			&existingUser.IBAN, &existingUser.BIC, &existingUser.CreatedAt)

		if err == nil {
			// User exists, return existing user
			token, err := GenerateToken(existingUser.ID, existingUser.Username)
			if err != nil {
				log.Printf("Error generating token: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
				return
			}
			c.JSON(http.StatusOK, gin.H{
				"message": "Google login successful",
				"user":    existingUser,
				"token":   token,
			})
			return
		}

		// Create new user
		var userID int
		err = db.QueryRow(`
			INSERT INTO users (username, email, full_name, password_hash, iban, bic, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
			RETURNING id
		`, username, email, fullName, "google_oauth_user", "", "", time.Now()).Scan(&userID)

		if err != nil {
			log.Printf("Error creating Google user: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
			return
		}

		user := User{
			ID:        userID,
			Username:  username,
			Email:     email,
			FullName:  fullName,
			IBAN:      "",
			BIC:       "",
			CreatedAt: time.Now(),
		}

		token, err := GenerateToken(user.ID, user.Username)
		if err != nil {
			log.Printf("Error generating token: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"message": "Google login successful",
			"user":    user,
			"token":   token,
		})
	})

	// Profile endpoints
	r.GET("/api/profile", AuthMiddleware(), func(c *gin.Context) {
		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		user, err := getUserByID(userID.(int))
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve user"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"user": user})
	})

	r.PUT("/api/profile", AuthMiddleware(), func(c *gin.Context) {
		var req UpdateProfileRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Update user profile
		_, err := db.Exec(`
			UPDATE users 
			SET full_name = $1, iban = $2, bic = $3
			WHERE id = $4
		`, req.FullName, req.IBAN, req.BIC, userID)

		if err != nil {
			log.Printf("Error updating user: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
			return
		}

		user, err := getUserByID(userID.(int))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated user"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Profile updated successfully",
			"user":    user,
		})
	})

	// Group endpoints
	r.GET("/api/groups", AuthMiddleware(), func(c *gin.Context) {
		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		groups, err := getGroupsByUserID(userID.(int))
		if err != nil {
			log.Printf("Error retrieving groups: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve groups"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"groups": groups})
	})

	r.POST("/api/groups", AuthMiddleware(), func(c *gin.Context) {
		var req CreateGroupRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Generate unique invite code
		inviteCode := generateInviteCode()

		// Generate random group ID
		groupID := generateGroupID()
		
		// Create group
		_, err := db.Exec(`
			INSERT INTO groups (id, name, description, created_by, invite_code, created_at)
			VALUES ($1, $2, $3, $4, $5, $6)
		`, groupID, req.Name, req.Description, userID, inviteCode, time.Now())

		if err != nil {
			log.Printf("Error creating group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create group"})
			return
		}

		// Add creator as first member
		err = addUserToGroup(userID.(int), groupID)
		if err != nil {
			log.Printf("Error adding creator to group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add creator to group"})
			return
		}

		// Get the created group
		group, err := getGroupByID(groupID)
		if err != nil {
			log.Printf("Error retrieving created group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve created group"})
			return
		}

		c.JSON(http.StatusCreated, gin.H{
			"message": "Group created successfully",
			"group":   group,
		})
	})

	r.GET("/api/groups/:id", AuthMiddleware(), func(c *gin.Context) {
		groupID := c.Param("id")
		if groupID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Group ID is required"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Group ID is already a string, no parsing needed
		gID := groupID

		// Check if user is member of group
		isMember, err := isUserMemberOfGroup(userID.(int), gID)
		if err != nil {
			log.Printf("Error checking group membership: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check group membership"})
			return
		}

		if !isMember {
			c.JSON(http.StatusForbidden, gin.H{"error": "You are not a member of this group"})
			return
		}

		group, err := getGroupByID(gID)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group"})
			return
		}

		// Get group members
		members, err := getGroupMembers(gID)
		if err != nil {
			log.Printf("Error retrieving group members: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group members"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"group":   group,
			"members": members,
		})
	})

	r.PUT("/api/groups/:id", AuthMiddleware(), func(c *gin.Context) {
		groupID := c.Param("id")
		if groupID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Group ID is required"})
			return
		}

		var req UpdateGroupRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Group ID is already a string, no parsing needed
		gID := groupID

		// Get group and check if user is the creator
		group, err := getGroupByID(gID)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group"})
			return
		}

		if group.CreatedBy != userID.(int) {
			c.JSON(http.StatusForbidden, gin.H{"error": "Only the group creator can update the group"})
			return
		}

		// Update group
		_, err = db.Exec(`
			UPDATE groups 
			SET name = $1, description = $2
			WHERE id = $3
		`, req.Name, req.Description, gID)

		if err != nil {
			log.Printf("Error updating group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update group"})
			return
		}

		// Get updated group
		updatedGroup, err := getGroupByID(gID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated group"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Group updated successfully",
			"group":   updatedGroup,
		})
	})

	r.DELETE("/api/groups/:id", AuthMiddleware(), func(c *gin.Context) {
		groupID := c.Param("id")
		if groupID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Group ID is required"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Group ID is already a string, no parsing needed
		gID := groupID

		// Get group and check if user is the creator
		group, err := getGroupByID(gID)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group"})
			return
		}

		if group.CreatedBy != userID.(int) {
			c.JSON(http.StatusForbidden, gin.H{"error": "Only the group creator can delete the group"})
			return
		}

		// Delete group (cascade will handle group_members)
		_, err = db.Exec(`DELETE FROM groups WHERE id = $1`, gID)
		if err != nil {
			log.Printf("Error deleting group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete group"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Group deleted successfully",
		})
	})

	r.POST("/api/groups/join", AuthMiddleware(), func(c *gin.Context) {
		var req JoinGroupRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Find group by invite code
		group, err := getGroupByInviteCode(req.InviteCode)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Invalid invite code"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to find group"})
			return
		}

		// Check if user is already a member
		isMember, err := isUserMemberOfGroup(userID.(int), group.ID)
		if err != nil {
			log.Printf("Error checking group membership: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check group membership"})
			return
		}

		if isMember {
			c.JSON(http.StatusConflict, gin.H{"error": "You are already a member of this group"})
			return
		}

		// Add user to group
		err = addUserToGroup(userID.(int), group.ID)
		if err != nil {
			log.Printf("Error adding user to group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to join group"})
			return
		}

		// Get updated group with new member count
		updatedGroup, err := getGroupByID(group.ID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated group"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Successfully joined group",
			"group":   updatedGroup,
		})
	})

	r.DELETE("/api/groups/:id/leave", AuthMiddleware(), func(c *gin.Context) {
		groupID := c.Param("id")
		if groupID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Group ID is required"})
			return
		}

		// Get user ID from JWT token
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
			return
		}

		// Group ID is already a string, no parsing needed
		gID := groupID

		// Check if user is member of group
		isMember, err := isUserMemberOfGroup(userID.(int), gID)
		if err != nil {
			log.Printf("Error checking group membership: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check group membership"})
			return
		}

		if !isMember {
			c.JSON(http.StatusForbidden, gin.H{"error": "You are not a member of this group"})
			return
		}

		// Get group to check if user is the creator
		group, err := getGroupByID(gID)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group"})
			return
		}

		if group.CreatedBy == userID.(int) {
			c.JSON(http.StatusForbidden, gin.H{"error": "Group creator cannot leave the group. Delete the group instead."})
			return
		}

		// Remove user from group
		err = removeUserFromGroup(userID.(int), gID)
		if err != nil {
			log.Printf("Error removing user from group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to leave group"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Successfully left group",
		})
	})

	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Smart Split Backend API",
			"endpoints": gin.H{
				"health":        "/api/health",
				"register":      "/api/auth/register",
				"login":         "/api/auth/login",
				"google_login":  "/api/auth/google",
				"profile":       "/api/profile",
				"groups":        "/api/groups",
				"group_details": "/api/groups/:id",
				"join_group":    "/api/groups/join",
				"leave_group":   "/api/groups/:id/leave",
			},
		})
	})

	serverAddr := appConfig.GetServerAddress()
	log.Printf("Starting server on %s", serverAddr)
	if err := r.Run(serverAddr); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
