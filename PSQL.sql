CREATE TABLE AboutUs (
  AboutId SERIAL PRIMARY KEY,
  AboutContent VARCHAR(500)
);

CREATE TABLE Concerts (
  ConcertId SERIAL PRIMARY KEY,
  ConcertTitle VARCHAR(20) NOT NULL,
  ConcertTime TIMESTAMP NOT NULL,
  ConcertLocation VARCHAR(50),
  ConcertDescription VARCHAR(200)
);

CREATE TABLE Tickets (
  TicketId SERIAL PRIMARY KEY,
  Seats INT,
  Price VARCHAR(150),
  ConcertId INT,
  FOREIGN KEY (ConcertId) REFERENCES Concerts(ConcertId)
);

CREATE TABLE Connections (
  ConnectionsId SERIAL PRIMARY KEY,
  FaceBook VARCHAR(100),
  Phone VARCHAR(10),
  Email VARCHAR(30),
  Instagram VARCHAR(50)
);

CREATE TABLE HomeElements (
  HomeElementId SERIAL PRIMARY KEY,
  HomeElementType VARCHAR(1),
  HomeElementFile VARCHAR(200),
);

CREATE TABLE Members (
  MemberId SERIAL PRIMARY KEY,
  MemberName VARCHAR(10),
  AboutMember VARCHAR(150),
  MemberImg VARCHAR(50)
);

CREATE TABLE Users (
  UserID SERIAL PRIMARY KEY,
  UserAccount VARCHAR(14) UNIQUE,
  UserPassword VARCHAR(50),
  UserName VARCHAR(10),
  UserRole VARCHAR(10),
  UserGender VARCHAR(1),
  MessageAble VARCHAR(1),
  Token VARCHAR(300),
  Tickets JSON[]
);

ALTER TABLE Users
ALTER Token TYPE VARCHAR(300);

INSERT INTO users (UserAccount,UserPassword,UserName,UserRole,UserGender,MessageAble)
VALUES ('root', 'aabb2100033f0352fe7458e412495148', '管理員', 'root', '', '1');

CREATE TABLE Messages (
  MessageId SERIAL PRIMARY KEY,
  UserID INT,
  Reply JSON[],
  FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
