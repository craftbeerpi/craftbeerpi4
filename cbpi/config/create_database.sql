CREATE TABLE IF NOT EXISTS dashboard
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80)

);

CREATE TABLE IF NOT EXISTS dashboard_content
(
    id INTEGER PRIMARY KEY NOT NULL,
    dbid INTEGER(80),
    element_id INTEGER,
    type VARCHAR(80),
    x INTEGER(5),
    y INTEGER(5),
    config VARCHAR(3000)
);

CREATE TABLE IF NOT EXISTS actor
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    type VARCHAR(80),
    config VARCHAR(3000)

);

CREATE TABLE IF NOT EXISTS sensor
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    type VARCHAR(80),
    config VARCHAR(3000)

);

CREATE TABLE IF NOT EXISTS kettle
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    sensor VARCHAR(80),
    heater VARCHAR(10),
    automatic VARCHAR(255),
    logic VARCHAR(50),
    config VARCHAR(1000),
    agitator VARCHAR(10),
    target_temp INTEGER,
    height INTEGER,
    diameter INTEGER
);

CREATE TABLE IF NOT EXISTS config
(
    name VARCHAR(50) PRIMARY KEY NOT NULL,
    value VARCHAR(255),
    type VARCHAR(50),
    description VARCHAR(255),
    options VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sensor
(
    id INTEGER PRIMARY KEY NOT NULL,
    type VARCHAR(100),
    name VARCHAR(80),
    config VARCHAR(3000)
);

CREATE TABLE IF NOT EXISTS step
(
    id INTEGER PRIMARY KEY NOT NULL,
    "order" INTEGER,
    name VARCHAR(80),
    type VARCHAR(100),
    stepstate VARCHAR(255),
    state VARCHAR(1),
    start INTEGER,
    end INTEGER,
    config VARCHAR(255),
    kettleid INTEGER
);

CREATE TABLE IF NOT EXISTS tank
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80),
    brewname VARCHAR(80),
    sensor VARCHAR(80),
    sensor2 VARCHAR(80),
    sensor3 VARCHAR(80),
    heater VARCHAR(10),
    logic VARCHAR(50),
    config VARCHAR(1000),
    cooler VARCHAR(10),
    target_temp INTEGER
);

CREATE TABLE IF NOT EXISTS translation
(
    language_code VARCHAR(3) NOT NULL,
    key VARCHAR(80) NOT NULL,
    text VARCHAR(100) NOT NULL,
    PRIMARY KEY (language_code, key)
);

CREATE TABLE IF NOT EXISTS dummy
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(80)

);


INSERT OR IGNORE INTO config (name, value, type, description, options) VALUES ('TEMP_UNIT', 'F', 'select', 'Temperature Unit', '[{"value": "C", "label": "C"}, {"value": "F", "label": "F"}]');
INSERT OR IGNORE INTO config (name, value, type, description, options) VALUES ('NAME', 'India Pale Ale1', 'string', 'Brew Name', 'null');
INSERT OR IGNORE INTO config (name, value, type, description, options) VALUES ('BREWERY_NAME', 'CraftBeerPI', 'string', 'Brewery Name', 'null');
