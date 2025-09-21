-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;

-- Insert sample data (optional)
-- This will be executed after the tables are created by SQLAlchemy

-- Sample users
INSERT INTO users (username, email, full_name, created_at, is_active) VALUES
('john_doe', 'john@example.com', 'John Doe', NOW(), true),
('jane_smith', 'jane@example.com', 'Jane Smith', NOW(), true),
('mike_wilson', 'mike@example.com', 'Mike Wilson', NOW(), true)
ON DUPLICATE KEY UPDATE username=username;

-- Sample tasks
INSERT INTO tasks (title, description, status, priority, created_at, updated_at, owner_id) VALUES
('Setup Development Environment', 'Configure local development environment with Docker and MySQL', 'completed', 'high', NOW(), NOW(), 1),
('Create API Documentation', 'Write comprehensive API documentation for all endpoints', 'in_progress', 'medium', NOW(), NOW(), 1),
('Implement User Authentication', 'Add JWT-based authentication system', 'pending', 'high', NOW(), NOW(), 2),
('Database Optimization', 'Optimize database queries and add indexes', 'pending', 'low', NOW(), NOW(), 2),
('Write Unit Tests', 'Create unit tests for all API endpoints', 'pending', 'medium', NOW(), NOW(), 3),
('Deploy to Production', 'Set up production environment and deploy application', 'pending', 'high', NOW(), NOW(), 3)
ON DUPLICATE KEY UPDATE title=title;