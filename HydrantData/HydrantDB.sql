CREATE DATABASE IF NOT EXISTS Oven;
USE Oven;

CREATE TABLE IF NOT EXISTS ARTICLES (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TITLE VARCHAR(255) NOT NULL,
    URL VARCHAR(255) NOT NULL,
    ARTICLE_TEXT LONGTEXT NOT NULL,
    PUBLISH_DATE DATETIME NOT NULL,
    SUMMARY VARCHAR(300),
    WEIGHTING INT
    -- SUGGESTED_IMPACT (uncomment and define type if needed)
);

create table IF NOT EXISTS URL_BLACKLIST (URL VARCHAR(255) primary KEY);

select * from ARTICLES;