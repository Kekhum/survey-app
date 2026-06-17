-- Uruchom jako ACCOUNTADMIN (lub uzytkownik z uprawnieniami CREATE DATABASE/WAREHOUSE/USER).
-- Zastap haslo 'ZmienMnie123!' silnym haslem przed uzyciem.

USE ROLE ACCOUNTADMIN;

-- Baza danych i schemat
CREATE DATABASE IF NOT EXISTS DEMO;
CREATE SCHEMA  IF NOT EXISTS DEMO.PUBLIC;

-- Tabela odpowiedzi ankiety
CREATE TABLE IF NOT EXISTS DEMO.PUBLIC.AUDIENCE_SURVEY (
    response_id      STRING        DEFAULT UUID_STRING(),
    submitted_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    role             STRING,
    experience_years INT,
    fav_cloud        STRING,
    fav_language     STRING,
    coffees_per_day  INT,
    uses_ai_daily    BOOLEAN
);

-- Warehouse do zapisu i odczytu (maly, autosuspend po 60s)
CREATE WAREHOUSE IF NOT EXISTS DEMO_WH
    WAREHOUSE_SIZE      = XSMALL
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Rola z minimalnymi uprawnieniami (zasada least privilege)
CREATE ROLE IF NOT EXISTS DEMO_SURVEY_ROLE;

GRANT USAGE ON WAREHOUSE DEMO_WH                       TO ROLE DEMO_SURVEY_ROLE;
GRANT USAGE ON DATABASE  DEMO                          TO ROLE DEMO_SURVEY_ROLE;
GRANT USAGE ON SCHEMA    DEMO.PUBLIC                   TO ROLE DEMO_SURVEY_ROLE;
GRANT INSERT, SELECT ON TABLE DEMO.PUBLIC.AUDIENCE_SURVEY TO ROLE DEMO_SURVEY_ROLE;

-- Dedykowany uzytkownik dla aplikacji ankiety
CREATE USER IF NOT EXISTS DEMO_SURVEY_USER
    PASSWORD          = 'ZmienMnie123!'
    DEFAULT_ROLE      = DEMO_SURVEY_ROLE
    DEFAULT_WAREHOUSE = DEMO_WH
    MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE DEMO_SURVEY_ROLE TO USER DEMO_SURVEY_USER;
