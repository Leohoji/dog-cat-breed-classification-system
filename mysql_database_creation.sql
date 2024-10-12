-- SHOW DATABASES;
-- CREATE DATABASE `cat_dog_system`;
USE `cat_dog_system`;
SET SQL_SAFE_UPDATES = 0;
SHOW TABLES;

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
INSERT INTO `member_info` (user_name, user_password) VALUES ('LoHoLeo2', 'ssssssss');

-- alter the member information
UPDATE `member_info`
SET user_password = 'Frankfurt'
WHERE user_name = '12345qwer@gmail.com';

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
-- DELETE FROM user_history WHERE history_id = 9;

-- insert fake data into user_history table
INSERT INTO user_history (user_name, image, results) 
VALUES ('12345qwer@gmail.com', NULL, 'Success');

DELETE FROM user_history WHERE user_name = 'LoHoLeo5';
DELETE FROM user_history WHERE user_name = '12345qwer@gmail.com' AND results = 'yes';

-- create table animal
CREATE TABLE animal (
    animal_id INT AUTO_INCREMENT PRIMARY KEY,
    animal_breed VARCHAR(50) UNIQUE,
    image_1 BLOB,
    image_2 BLOB,
    animal_description VARCHAR(300),
    animal_link VARCHAR(500)
);

-- DROP TABLE `animal`;  

SELECT * FROM `animal`;

-- insert some fake data into animal table
INSERT INTO animal (animal_breed, image_1, image_2, animal_description, animal_link)
VALUES ('Labrador', NULL, NULL, 'Friendly and energetic dog breed.', 'https://en.wikipedia.org/wiki/St._Bernard_(dog_breed)');

-- delete fake data from animal table
DELETE FROM animal WHERE animal_breed = 'Labrador';
