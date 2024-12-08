ALTER TABLE Users
ADD PasswordHash NVARCHAR(255) NULL;

-- Update existing users with a temporary password hash if needed
UPDATE Users 
SET PasswordHash = 'pbkdf2:sha256:temporary_hash'
WHERE PasswordHash IS NULL;

-- Then make the column NOT NULL after updating existing records
ALTER TABLE Users
ALTER COLUMN PasswordHash NVARCHAR(255) NOT NULL;
