CREATE TABLE employees (
    empid INT PRIMARY KEY AUTO_INCREMENT,
    empname VARCHAR(255) UNIQUE NOT NULL,
    age INT,
    salary FLOAT,
    department VARCHAR(255),
    elligibility_criteria ENUM("Y", "N"),
    is_online TINYINT,
    relational INT,
    CHECK (age >= 18 AND age <= 75)
);

INSERT INTO employees(empname, age, salary, department, elligibility_criteria, is_online, relational) VALUES
    ("Aarav Kumar", 29, 18.75, "IT", "Y", 1, 2),
    ("Isha Patel", 35, 21.30, "Marketing", "N", 0, 3),
    ("Rohan Mehra", 42, 25.00, "HR", "Y", 1, 4),
    ("Sofia Ali", 27, 19.50, "Finance", "Y", 0, 5),
    ("Liam Chen", 31, 22.10, "Development", "N", 1, 6),
    ("Emma Wilson", 38, 24.00, "Sales", "Y", 0, 7),
    ("Olivia Smith", 26, 17.85, "Research", "N", 1, 8),
    ("Noah Lee", 45, 26.30, "IT", "Y", 0, 9),
    ("Ava Taylor", 33, 20.55, "Marketing", "N", 1, 10),
    ("Isabella Brown", 40, 27.80, "HR", "Y", 1, 11),
    ("Mia Johnson", 23, 18.20, "Finance", "Y", 0, 12),
    ("Lucas Davis", 36, 23.45, "Development", "N", 1, 13),
    ("Amelia Martin", 29, 19.90, "Sales", "Y", 0, 14),
    ("Ethan Anderson", 48, 28.60, "Research", "N", 1, 15),
    ("Charlotte Wilson", 32, 21.75, "IT", "Y", 1, 16),
    ("James Thomas", 37, 22.80, "Marketing", "N", 0, 17),
    ("Sophia Jackson", 41, 26.90, "HR", "Y", 1, 18),
    ("Alexander Martinez", 34, 20.00, "Finance", "N", 0, 19),
    ("Harper Gonzalez", 28, 23.30, "Development", "Y", 1, 20),
    ("Elijah Hernandez", 39, 25.70, "Sales", "N", 0, 21);

