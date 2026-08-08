-- Run this against your database once, before applying the migration
-- that creates the bookings/maintenance_blocks ExcludeConstraints.
-- Without it, the CREATE TABLE / ALTER TABLE will fail with something
-- like: "operator class "gist_uuid_ops" does not exist for access method gist"
CREATE EXTENSION IF NOT EXISTS btree_gist;
