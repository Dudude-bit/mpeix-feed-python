create table feed_data(
    id bigserial primary key unique not null,
    created_at timestamp ,
    updated_at timestamp,
    source varchar(63),
    source_id bigint unique ,
    source_link text unique ,
    text text,
    post_created timestamp,
    recourse_id text

)