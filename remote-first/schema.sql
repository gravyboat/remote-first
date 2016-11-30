drop table if exists ads;
create table ads (
  id integer primary key autoincrement,
  jobTitle text not null,
  jobType text not null,
  jobDescription text not null,
  howToApply text not null,
  companyName text not null,
  companyURL text not null,
  publishDate text not null,
  expirationDate text not null,
  active integer
);
