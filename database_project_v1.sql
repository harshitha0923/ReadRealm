USE readrealm;
-- --------------------------------------------------------
-- DROP TABLE 
-- --------------------------------------------------------
DROP TABLE UserBooksRead;
DROP TABLE GenresBooks;
DROP TABLE UserBooksToRead;
DROP TABLE UserCurrentlyReading;
DROP TABLE Followers;
DROP TABLE Reviews;
DROP TABLE Ratings;
DROP TABLE Users;
DROP TABLE Publishers;
DROP TABLE Books;
DROP TABLE Genres;
DROP TABLE Authors;

DROP VIEW UserProfileView;
DROP VIEW UserFollowersView;
DROP VIEW AverageBookRating;
DROP VIEW BookDetailsPageView;
DROP VIEW BookDetailsWithLatestRating;
DROP PROCEDURE AddFollower;

-- --------------------------------------------------------
-- CREATE TABLES, INDEX, VIEWS, TRANSACTION STORED PROCEDURE
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    FollowerCount INT DEFAULT 0,
    FollowingCount INT DEFAULT 0,
    Bio TEXT
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Authors (
    AuthorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Bio TEXT
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Genres (
    GenreID INT AUTO_INCREMENT PRIMARY KEY, 
    GenreName VARCHAR(255) UNIQUE NOT NULL
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Publishers (
    PublisherId INT AUTO_INCREMENT PRIMARY KEY,
    PublisherName VARCHAR(255) UNIQUE NOT NULL
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Books (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    AuthorID INT,
    GenreID INT, -- Consider removing if you will use GenresBooks for many-to-many relation
    PublicationDate DATE,
    ISBN VARCHAR(13) UNIQUE,
    Description TEXT,
    ImageURL TEXT
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID) ON DELETE CASCADE ON UPDATE CASCADE
    -- If books have a single publisher, add the foreign key constraint here
    -- FOREIGN KEY (PublisherID) REFERENCES Publishers(publisher_id)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS GenresBooks (
    GenreBookID INT AUTO_INCREMENT PRIMARY KEY,
    GenreID INT,
    BookID INT,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS UserBooksRead (
    EntryID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    BookID INT,
    DateAdded DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS UserBooksToRead (
    EntryID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    BookID INT,
    DateAdded DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS UserCurrentlyReading (
    ReadingID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    BookID INT,
    StartDate DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Followers (
    RelationshipID INT AUTO_INCREMENT PRIMARY KEY,
    FollowerID INT,
    FollowingID INT,
    DateFollowed DATE,
    FOREIGN KEY (FollowerID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (FollowingID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Reviews (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    BookID INT,
    ReviewContent TEXT,
    ReviewDate DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS Ratings (
    RatingID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    BookID INT,
    Rating INT CHECK (Rating BETWEEN 0 AND 5), -- Changed to include 0
    RatingDate DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_userBooksToRead_userID ON UserBooksToRead(UserID);
CREATE INDEX idx_userBooksRead_userID ON UserBooksRead(UserID);
CREATE INDEX idx_followers_followerID ON Followers(FollowerID);
CREATE INDEX idx_followers_followingID ON Followers(FollowingID);


#UserProfileView: Combines user details with their reading lists and follower counts.
CREATE VIEW UserProfileView AS
SELECT u.UserID, u.Username, u.Bio,
       (SELECT COUNT(*) FROM UserBooksToRead ubtr WHERE ubtr.UserID = u.UserID) AS ToReadCount,
       (SELECT COUNT(*) FROM UserBooksRead ubr WHERE ubr.UserID = u.UserID) AS ReadCount,
       (SELECT COUNT(*) FROM UserCurrentlyReading ucr WHERE ucr.UserID = u.UserID) AS CurrentlyReadingCount,
       (SELECT COUNT(*) FROM Followers f WHERE f.FollowingID = u.UserID) AS FollowerCount,
       (SELECT COUNT(*) FROM Followers f WHERE f.FollowerID = u.UserID) AS FollowingCount
FROM Users u;

#UserFollowersView: Details about a user's followers, useful for displaying lists of followers or people a user is following.
CREATE VIEW UserFollowersView AS
SELECT u.UserID, u.Username, f.FollowingID, f.FollowerID
FROM Users u
JOIN Followers f ON u.UserID = f.FollowingID OR u.UserID = f.FollowerID;


SELECT B.BookID as BookID, B.Title AS BookTitle,
    (1*SUM(CASE WHEN R.Rating = 1 THEN 1 ELSE 0 END) + 
    2*SUM(CASE WHEN R.Rating = 2 THEN 1 ELSE 0 END) + 
    3*SUM(CASE WHEN R.Rating = 3 THEN 1 ELSE 0 END) + 
    4*SUM(CASE WHEN R.Rating = 4 THEN 1 ELSE 0 END) + 
    5*SUM(CASE WHEN R.Rating = 5 THEN 1 ELSE 0 END)) / COUNT(*) AS 'AverageRating'
FROM Books B LEFT JOIN Ratings R ON B.BookID = R.BookID 
GROUP BY B.BookID, B.Title;


CREATE VIEW BookDetailsPageView AS
SELECT 
    B.BookID AS BookID,
    B.Title AS BookTitle,
    A.Name AS AuthorName,
    P.PublisherName,
    B.PublicationDate,
    B.Description,
    ABR.AverageRating,
    G.GenreName, 
    B.ImageURL
FROM 
    Books B
    LEFT JOIN Authors A ON B.AuthorID = A.AuthorID
    LEFT JOIN Publishers P ON B.PublisherID = P.PublisherID
    LEFT JOIN Genres G ON B.GenreID = G.GenreID
    LEFT JOIN AverageBookRating ABR ON ABR.BookID = B.BookID
GROUP BY 
    B.BookID, B.Title, A.Name, P.PublisherName, B.PublicationDate, B.Description, G.GenreName;


CREATE VIEW BookDetailsWithLatestRating AS
SELECT 
    BD.BookID, R.UserID, BD.BookTitle, BD.AuthorName, BD.PublisherName, BD.PublicationDate, BD.Description, BD.AverageRating, 
    R.Rating AS UserRating, BD.GenreName, BD.ImageURL, R.RatingDate AS LatestRatingDate
FROM  BookDetailsPageView BD
LEFT JOIN (SELECT RatingID, UserID, BookID, Rating, RatingDate FROM Ratings R1 WHERE R1.RatingDate = (
        SELECT MAX(R2.RatingDate) FROM Ratings R2 WHERE R2.UserID = R1.UserID ) 
        ) R ON BD.BookID = R.BookID;


CREATE VIEW AverageBookRating AS
SELECT B.BookID, B.Title AS BookTitle,
    (1*SUM(CASE WHEN R.Rating = 1 THEN 1 ELSE 0 END) + 
    2*SUM(CASE WHEN R.Rating = 2 THEN 1 ELSE 0 END) + 
    3*SUM(CASE WHEN R.Rating = 3 THEN 1 ELSE 0 END) + 
    4*SUM(CASE WHEN R.Rating = 4 THEN 1 ELSE 0 END) + 
    5*SUM(CASE WHEN R.Rating = 5 THEN 1 ELSE 0 END)) / COUNT(*) AS 'Average_Rating'
FROM Books B LEFT JOIN Ratings R ON B.BookID = R.BookID
GROUP BY B.BookID, B.Title;



DELIMITER $$

CREATE PROCEDURE AddFollower(IN p_FollowerID INT, IN p_FollowingID INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        -- If an error occurs, rollback the transaction
        ROLLBACK;
    END;

    -- Start the transaction
    START TRANSACTION;
    
    -- Insert the follower relationship into the Followers table
    INSERT INTO Followers (FollowerID, FollowingID, DateFollowed) 
    VALUES (p_FollowerID, p_FollowingID, NOW());
    
    -- To add following count - Update the following count for the follower
    UPDATE Users 
    SET FollowingCount = FollowingCount + 1 
    WHERE UserID = p_FollowerID;
    
    -- To add follower count - Update the follower count for the user being followed
    UPDATE Users 
    SET FollowerCount = FollowerCount + 1 
    WHERE UserID = p_FollowingID;
    
    -- To remove following count - Update the following count for the follower
    UPDATE Users 
    SET FollowingCount = FollowingCount - 1 
    WHERE UserID = p_FollowerID;
    
    -- To remove follower count - Update the follower count for the user being followed
    UPDATE Users 
    SET FollowerCount = FollowerCount - 1 
    WHERE UserID = p_FollowingID;    
    
    -- If all operations are successful, commit the transaction
    COMMIT;
END$$

DELIMITER ;

-- --------------------------------------------------------
-- INSERT DATA 
-- --------------------------------------------------------
INSERT INTO Users (Username, Email, Password, Bio)
VALUES ('alice_smith', 'alice.smith@example.com', 'as$123', 'Book lover and tea enthusiast.'),
       ('bob_jones', 'bob.jones@example.com', 'bj$123', 'Always looking for a good mystery.'),
       ('emily_davis', 'emily.davis@example.com', 'ed$123', 'Science fiction fanatic.'),
       ('michael_wilson', 'michael.wilson@example.com', 'mw$123', 'History buff and avid reader.'),
       ('sarah_miller', 'sarah.miller@example.com', 'sm$123', 'Enjoys fantasy and young adult novels.');

INSERT INTO Authors (Name, Bio)
VALUES ('Agatha Christie', 'Queen of mystery novels.'),
       ('J.R.R. Tolkien', 'Author of The Lord of the Rings.'),
       ('Stephen King', 'Master of horror and suspense.'),
       ('Margaret Atwood', 'Author of The Handmaid''s Tale.'),
       ('Haruki Murakami', 'Renowned Japanese author.');

INSERT INTO Genres (GenreName)
VALUES ('Romance'),
       ('Historical Fiction'),
       ('Thriller'),
       ('Young Adult'),
       ('Biography');

INSERT INTO Publishers (PublisherName)
VALUES ('Random House'),
       ('Simon & Schuster'),
       ('Macmillan'),
       ('Hachette'),
       ('Wiley');

INSERT INTO Books (Title, AuthorID, GenreID, PublicationDate, ISBN, Description)
VALUES ('Murder on the Orient Express', 1, 3, '1934-01-01', '9780062693662', 'A classic mystery novel by Agatha Christie.'),
       ('The Hobbit', 2, 4, '1937-09-21', '9780547928227', 'Fantasy adventure novel by J.R.R. Tolkien.'),
       ('The Shining', 3, 1, '1977-01-28', '9780385121675', 'Horror novel by Stephen King.'),
       ('The Handmaid''s Tale', 4, 2, '1985-09-17', '9780385490818', 'Dystopian novel by Margaret Atwood.'),
       ('Norwegian Wood', 5, 5, '1987-08-28', '9780375704024', 'A novel by Haruki Murakami.');

INSERT INTO GenresBooks (GenreID, BookID)
VALUES (3, 1),
       (4, 2),
       (1, 3),
       (2, 4),
       (5, 5);

INSERT INTO UserCurrentlyReading (UserID, BookID, StartDate)
VALUES (1, 2, '2023-01-05'),
       (2, 3, '2023-02-15'),
       (3, 4, '2023-03-10'),
       (4, 5, '2023-04-05'),
       (5, 1, '2023-04-20');
       
INSERT INTO UserBooksRead (UserID, BookID, DateAdded)
VALUES (1, 2, '2023-01-20'),  -- alice_smith read The Hobbit
       (2, 3, '2023-02-25'),  -- bob_jones read The Shining
       (3, 4, '2023-03-30'),  -- emily_davis read The Handmaid's Tale
       (4, 5, '2023-04-20'),  -- michael_wilson read Norwegian Wood
       (5, 1, '2023-05-05');  -- sarah_miller read Murder on the Orient Express
       
INSERT INTO UserBooksToRead (UserID, BookID, DateAdded)
VALUES (1, 1, '2023-01-10'),  -- alice_smith plans to read Murder on the Orient Express
       (2, 4, '2023-02-20'),  -- bob_jones plans to read The Handmaid's Tale
       (3, 5, '2023-03-15'),  -- emily_davis plans to read Norwegian Wood
       (4, 2, '2023-04-10'),  -- michael_wilson plans to read The Hobbit
       (5, 3, '2023-05-01');  -- sarah_miller plans to read The Shining
       
INSERT INTO Followers (FollowerID, FollowingID, DateFollowed)
VALUES (1, 2, '2023-01-10'),
       (2, 3, '2023-02-20'),
       (3, 4, '2023-03-15'),
       (4, 5, '2023-04-10'),
       (5, 1, '2023-05-01');

INSERT INTO Reviews (UserID, BookID, ReviewContent, ReviewDate)
VALUES (1, 2, 'A delightful read!', '2023-01-20'),
       (2, 3, 'Incredible story.', '2023-02-25'),
       (3, 4, 'A must-read!', '2023-03-30'),
       (4, 5, 'Fascinating narrative.', '2023-04-20'),
       (5, 1, 'Loved it!', '2023-05-05');

INSERT INTO Ratings (UserID, BookID, Rating, RatingDate)
VALUES (1, 2, 5, '2023-01-20'),
       (2, 3, 4, '2023-02-25'),
       (3, 4, 5, '2023-03-30'),
       (4, 5, 4, '2023-04-20'),
       (5, 1, 5, '2023-05-05');

