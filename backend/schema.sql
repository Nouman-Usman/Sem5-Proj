CREATE TABLE [User] (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('Admin', 'Customer', 'Lawyer')),
    phone_number VARCHAR(20),
    profile_picture_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended')),
    subscription_id INT,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Subscription (
    subscription_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    plan_type VARCHAR(20) NOT NULL CHECK (plan_type IN ('Free', 'Basic', 'Premium')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Active', 'Expired')),
    payment_info VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Pending', 'Completed', 'Failed')),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [User](user_id) ON DELETE CASCADE
);

CREATE TABLE CustomerHistory (
    history_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [User](user_id) ON DELETE CASCADE
);

CREATE TABLE ChatData (
    chat_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    messages NVARCHAR(MAX) NOT NULL,
    chat_title VARCHAR(255),
    last_message_time DATETIME DEFAULT GETDATE(),
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'Closed', 'Archived')),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [User](user_id) ON DELETE CASCADE
);

CREATE TABLE Summary (
    summary_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    chat_id INT NOT NULL,
    summary_text TEXT NOT NULL,
    generated_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [User](user_id) ON DELETE CASCADE,
    FOREIGN KEY (chat_id) REFERENCES ChatData(chat_id) ON DELETE NO ACTION
);

CREATE TABLE SentimentAnalysis (
    sentiment_id INT PRIMARY KEY IDENTITY(1,1),
    chat_id INT NOT NULL,
    sentiment_score DECIMAL(3, 2),
    sentiment_label VARCHAR(20) NOT NULL CHECK (sentiment_label IN ('Positive', 'Negative', 'Neutral')),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (chat_id) REFERENCES ChatData(chat_id) ON DELETE CASCADE
);

CREATE TABLE LawyerRecommendation (
    recommendation_id INT PRIMARY KEY IDENTITY(1,1),
    customer_id INT NOT NULL,
    lawyer_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3, 2),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Accepted', 'Rejected')),
    specialization VARCHAR(100) NOT NULL,
    recommended_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (customer_id) REFERENCES [User](user_id) ON DELETE CASCADE,
    FOREIGN KEY (lawyer_id) REFERENCES [User](user_id) ON DELETE NO ACTION
);

CREATE TABLE Logs (
    log_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    activity TEXT NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
    ip_address VARCHAR(45),
    severity VARCHAR(20) DEFAULT 'INFO' CHECK (severity IN ('INFO', 'WARNING', 'ERROR')),
    user_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES [User](user_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_email ON [User](email);
CREATE INDEX idx_user_type ON [User](user_type);
CREATE INDEX idx_user_status ON ChatData(user_id, status);
CREATE INDEX idx_last_message ON ChatData(last_message_time);
CREATE INDEX idx_customer_lawyer ON LawyerRecommendation(customer_id, lawyer_id);
CREATE INDEX idx_timestamp ON Logs(timestamp);
CREATE INDEX idx_user_timestamp ON Logs(user_id, timestamp);
