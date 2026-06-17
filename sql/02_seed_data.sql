-- Dane testowe - siatka bezpieczenstwa na wypadek gdy sala nie wypelni ankiety.
-- Uruchom po 01_setup.sql.

USE DATABASE DEMO;
USE SCHEMA PUBLIC;
USE WAREHOUSE DEMO_WH;

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Data Engineer', 7, 'AWS', 'Python', 3, TRUE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Data Scientist', 4, 'GCP', 'Python', 2, TRUE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Analyst', 2, 'Azure', 'SQL', 1, FALSE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Dev', 10, 'AWS', 'Java', 4, FALSE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Manager', 8, 'Azure', 'SQL', 2, TRUE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Data Engineer', 5, 'Snowflake', 'Python', 3, TRUE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Data Scientist', 6, 'GCP', 'Rust', 1, TRUE);

INSERT INTO AUDIENCE_SURVEY (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
VALUES ('Dev', 3, 'AWS', 'JavaScript', 5, FALSE);
