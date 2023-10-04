CREATE TABLE IF NOT EXISTS public.user (
    id uuid DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY,
    username VARCHAR(200),
    email VARCHAR(200),
    password VARCHAR(200),
    is_admin BOOLEAN,
    disabled BOOLEAN
);