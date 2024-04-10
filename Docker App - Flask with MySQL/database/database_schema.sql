drop database if exists testing;
create database if not exists testing;
use testing;

create table if not exists passenger
(Passenger_id int NOT NULL PRIMARY KEY,
Passenger_name varchar(255),
Category               varchar(255),
Gender                 varchar(255),
Boarding_City      varchar(255),
Destination_City   varchar(255),
Distance                int,
Bus_Type             varchar(255)
);

create table if not exists price
(
id int NOT NULL PRIMARY KEY,
Bus_Type   varchar(255),
Distance    int,
Price      int
);

-- Table Insertion: Passenger
insert into passenger values(1, 'Sejal','AC','F','Bengaluru','Chennai',350,'Sleeper');
insert into passenger values(2, 'Anmol','Non-AC','M','Mumbai','Hyderabad',700,'Sitting');
insert into passenger values(3, 'Pallavi','AC','F','panaji','Bengaluru',600,'Sleeper');
insert into passenger values(4, 'Khusboo','AC','F','Chennai','Mumbai',1500,'Sleeper');
insert into passenger values(5, 'Udit','Non-AC','M','Trivandrum','panaji',1000,'Sleeper');
insert into passenger values(6, 'Ankur','AC','M','Nagpur','Hyderabad',500,'Sitting');
insert into passenger values(7, 'Hemant','Non-AC','M','panaji','Mumbai',700,'Sleeper');
insert into passenger values(8, 'Manish','Non-AC','M','Hyderabad','Bengaluru',500,'Sitting');
insert into passenger values(9, 'Piyush','AC','M','Pune','Nagpur',700,'Sitting');

-- Table Insertion: Price
insert into price values(1, 'Sleeper',350,770);
insert into price values(2, 'Sleeper',500,1100);
insert into price values(3, 'Sleeper',600,1320);
insert into price values(4, 'Sleeper',700,1540);
insert into price values(5, 'Sleeper',1000,2200);
insert into price values(6, 'Sleeper',1200,2640);
insert into price values(7, 'Sleeper',1500,2700);
insert into price values(8, 'Sitting',500,620);
insert into price values(9, 'Sitting',600,744);
insert into price values(10, 'Sitting',700,868);
insert into price values(11, 'Sitting',1000,1240);
insert into price values(12, 'Sitting',1200,1488);
insert into price values(13, 'Sitting',1500,1860);

SELECT  * FROM passenger limit 2;