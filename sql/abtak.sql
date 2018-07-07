create table faculty(
    initials varchar(10) primary key,
    name varchar(30),
    designation varchar(30),
    phone varchar(15),
    email varchar(30)
);

/*create procedure for inserting faculty*/
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Faculty`(
    IN initials varchar(10),
    IN name varchar(30),
    IN designation varchar(30),
    IN phone varchar(15),
    email varchar(30)
)
BEGIN
    if (select exists (select 1 from faculty f where f.initials=initials) ) THEN
     
        select 'Faculty already exists.';
     
    ELSE
     
        insert into faculty
        values
        (
            initials, name, designation, phone, email
        );
     
    END IF;
END$$
DELIMITER ;


create table timeslot(
    day varchar(10),
    hour varchar(15),
    primary key(day, hour)
);

/*create procedure for inserting time slot */
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Timeslot`(
    in day varchar(10),
    in hour varchar(15)
)
BEGIN
    if (select exists(select 1 from timeslot t where t.day=day and t.hour=hour)) THEN
     
        select 'Time slot already exists.';
     
    ELSE
     
        insert into timeslot
        values
        (
            day,hour
        );
     
    END IF;
END$$
DELIMITER ;

/*subject and elective are disjoint*/

create table subject(
    code varchar(10) primary key,
    title varchar(60) not null,
    abbreviation varchar(10)
);

/* procedure for inserting subject*/

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Subject`(
    in code varchar(10),
    in title varchar(60),
    in abbreviation varchar(10)
)
BEGIN
    if (select exists(select 1 from subject s where s.code=code)) THEN
     
        select 'Subject already exists.';
     
    ELSE
     
        insert into subject
        values
        (
            code, title, abbreviation
        );
     
    END IF;
END$$
DELIMITER ;

create table elective(
    code varchar(10) primary key,
    title varchar(60) not null,
    pool varchar(2)
);

/*procedure to insert elective*/

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Elective`(
    in code varchar(10),
    in title varchar(60),
    in pool varchar(2)
)
BEGIN
    if (select exists(select 1 from elective e where e.code=code)) THEN
     
        select 'Elective already exists.';
     
    ELSE
     
        insert into elective
        values
        (
            code, title, pool
        );
     
    END IF;
END$$
DELIMITER ;

create table room(
    roomno varchar(20) primary key,
    type varchar(20)
);

/*create procedure for inserting room */
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Room`(
    in roomno varchar(10),
    in type varchar(15)
)
BEGIN
    if (select exists(select 1 from room r where r.roomno=roomno)) THEN
     
        select 'Room already exists.';
     
    ELSE
     
        insert into room
        values
        (
            roomno, type
        );
     
    END IF;
END$$
DELIMITER ;


create table class(
    semester char(1),
    section char(1),
    primary key(semester,section)
);

/*procedure to create class*/

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Class`(
    in semester char(1),
    in section char(1)
)
BEGIN
    if (select exists(select 1 from class c where c.semester=semester and c.section=section )) THEN
     
        select 'Class already exists.';
     
    ELSE
     
        insert into class
        values
        (
            semester, section
        );
     
    END IF;
END$$
DELIMITER ;

create table teachessection(
	semester char(1),
	section char(1),
	code varchar(10),
	initials varchar(10),
	foreign key(initials) references faculty(initials),
	foreign key(semester, section) references class(semester, section),
	foreign key(code) references subject(code),
	primary key(semester, section, code)
);

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_Teachessection`(
    in semester char(1),
    in section char(1),
	in code varchar(10),
	in initials varchar(10)
)
BEGIN
    if (select exists(select 1 from teachessection ts where ts.semester=semester and ts.section=section and ts.code=code)) THEN
     
        select 'Teacher already exists for this combination of class and code.';
     
    ELSE
     
        insert into teachessection
        values
        (
            semester, section, code, initials
        );
     
    END IF;
END$$
DELIMITER ;
	