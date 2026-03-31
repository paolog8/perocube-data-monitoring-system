-- SymmetricDS requires SUPERUSER to install trigger functions on tables it does not own.
-- GRANT TRIGGER alone is insufficient — PostgreSQL requires the trigger creator to be
-- either the table owner or a superuser.
ALTER ROLE sym_user SUPERUSER;
