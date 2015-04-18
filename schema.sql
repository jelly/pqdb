drop table if exists quotes;
create table quotes (
    id integer primary key autoincrement,
    'text' text not null,
    author text not null,
    ts datetime default current_timestamp
);
