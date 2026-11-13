-- One-off migration for vocabulary-api#5.
-- Renames the user/category link table from the misspelled "user_cotegories"
-- to "user_categories", together with its primary key, foreign key
-- and NOT NULL constraints, so the names match what create_all would generate.
--
-- Run it with the API scaled to 0, after a pg_dump backup, against the
-- "vocabulary" database. The whole script runs in one transaction and stops
-- on the first error, so a failure leaves the database unchanged.
--
--   psql -v ON_ERROR_STOP=1 -d vocabulary -f 0001_rename_user_categories.sql

BEGIN;

ALTER TABLE user_cotegories RENAME TO user_categories;
ALTER TABLE user_categories
    RENAME CONSTRAINT user_cotegories_pkey TO user_categories_pkey;
ALTER TABLE user_categories
    RENAME CONSTRAINT user_cotegories_category_id_fkey TO user_categories_category_id_fkey;
-- PostgreSQL 18 also names NOT NULL constraints after the table.
ALTER TABLE user_categories
    RENAME CONSTRAINT user_cotegories_user_id_not_null TO user_categories_user_id_not_null;
ALTER TABLE user_categories
    RENAME CONSTRAINT user_cotegories_category_id_not_null TO user_categories_category_id_not_null;

COMMIT;
