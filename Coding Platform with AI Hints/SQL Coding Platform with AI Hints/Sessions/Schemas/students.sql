create table students(
    id int primary key auto_increment,
    name varchar(10) not null unique,
    age int
);

insert into students(name, age) values("Vinay", 10), ("Vijay", 20);
