-- MySQL Database Initialization Script
-- ----------------------------------
-- Purpose: Configure initial database permissions
-- Features:
-- - Admin user privileges
-- - Test database access
-- - Production database access
-- Author: Renzo Tincopa
-- Last Updated: 2024

-- Grant full admin privileges
-- Required for database management operations
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- Configure test database permissions
-- Enables Django test suite execution
GRANT ALL PRIVILEGES ON `test_trivia_db`.* TO 'admin'@'%';

-- Configure production database permissions
-- Required for application operation
GRANT ALL PRIVILEGES ON `trivia_db`.* TO 'admin'@'%';

-- Enable database creation permissions
-- Required for test database setup
GRANT CREATE ON *.* TO 'admin'@'%';

-- Apply permission changes
FLUSH PRIVILEGES;

-- Security Note: These permissions are for development
-- Modify for production environment with restricted access
