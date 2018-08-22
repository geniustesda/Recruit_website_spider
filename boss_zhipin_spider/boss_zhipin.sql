drop table if exists job_crawl;
create table job_crawl(
    id int(20) not null auto_increment primary key,
    job varchar(20) null,
    job_des_url varchar(300) null,
    company_des_url varchar(300) null,
    salary varchar(20) null,
    position varchar(20) null,
    worktime varchar(10) null,
    education varchar(10) null,
    company varchar(15) null,
    industry varchar(10) null,
    finance varchar(10) null,
    size varchar(10) null,
    hr_name varchar(10) null,
    hr_img varchar(300) null,
    hr_job varchar(10) null,
    release_date varchar(20) null,
    time timestamp
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8;