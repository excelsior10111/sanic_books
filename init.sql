CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    author VARCHAR(100) NOT NULL,
    book_descr VARCHAR(510) NOT NULL,
    book_name VARCHAR(255) NOT NULL,
    published INTEGER NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    roles VARCHAR(10) DEFAULT 'user'
);
CREATE INDEX index_email
ON users (email);

CREATE TABLE sessions (
    ssi UUID PRIMARY KEY,
    userid INTEGER NOT NULL,
    expiry TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX sessions_expiry_idx ON sessions(expiry);