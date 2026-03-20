CREATE TABLE country (
    id           BIGSERIAL PRIMARY KEY,
    iso2         CHAR(2) NOT NULL UNIQUE,
    name         VARCHAR(120) NOT NULL
);

CREATE TABLE university (
    id               BIGSERIAL PRIMARY KEY,
    country_id       BIGINT NOT NULL,
    name             VARCHAR(300) NOT NULL,
    state_province   VARCHAR(120),

    CONSTRAINT uk_university UNIQUE (country_id, name, state_province),
    CONSTRAINT fk_university_country FOREIGN KEY (country_id) REFERENCES country(id)
);

CREATE INDEX ix_university_country ON university(country_id);
CREATE INDEX ix_university_name ON university(name);

CREATE TABLE university_domain (
   id            BIGSERIAL PRIMARY KEY,
   university_id BIGINT NOT NULL,
   domain        VARCHAR(253) NOT NULL,

   CONSTRAINT uk_university_domain UNIQUE (university_id, domain),
   CONSTRAINT fk_domain_university FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE INDEX ix_domain_domain ON university_domain(domain);

CREATE TABLE university_webpage (
    id            BIGSERIAL PRIMARY KEY,
    university_id BIGINT NOT NULL,
    url           VARCHAR(2048) NOT NULL,

    CONSTRAINT uk_university_webpage UNIQUE (university_id, url),
    CONSTRAINT fk_webpage_university FOREIGN KEY (university_id) REFERENCES university(id)
);

CREATE INDEX ix_webpage_url ON university_webpage(url);