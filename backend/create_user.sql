-- Script generado automaticamente
-- Ejecuta con: psql -U postgres -f create_user.sql

CREATE USER "Aurora" WITH PASSWORD 'p-integracion123';
ALTER USER "Aurora" CREATEDB;
