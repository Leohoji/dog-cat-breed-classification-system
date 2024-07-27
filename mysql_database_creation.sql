-- SHOW DATABASES;
-- CREATE DATABASE `cat_dog_system`;
USE `cat_dog_system`;
SET SQL_SAFE_UPDATES = 0;

-- create memeber table
CREATE TABLE `member_info` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    user_password VARCHAR(20) NOT NULL,
    register_data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SELECT * FROM `member_info`;
-- DROP TABLE `member_info`;

-- insert some default data
INSERT INTO `member_info` (user_name, user_password) VALUES ('12345qwer@gmail.com', 'sdlkjfg455');
INSERT INTO `member_info` (user_name, user_password) VALUES ('56789qwer@gmail.com', 'sdf485885');

-- create table user_history
CREATE TABLE user_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50),
    image BLOB,
    results VARCHAR(20),
    classification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_name) REFERENCES member_info(user_name)
);

SELECT * FROM `user_history`;

-- insert fake data into user_history table
INSERT INTO user_history (user_name, image, results) 
VALUES ('12345qwer@gmail.com', NULL, 'Success');

-- create table animal
CREATE TABLE animal (
    animal_id INT AUTO_INCREMENT PRIMARY KEY,
    animal_breed VARCHAR(20) UNIQUE,
    image_1 BLOB,
    image_2 BLOB,
    image_3 BLOB,
    animal_description VARCHAR(300)
);

SELECT * FROM `animal`;

-- insert some fake data into animal table
INSERT INTO animal (animal_breed, image_1, image_2, image_3, animal_description)
VALUES ('Labrador', NULL, NULL, NULL, 'Friendly and energetic dog breed.');
