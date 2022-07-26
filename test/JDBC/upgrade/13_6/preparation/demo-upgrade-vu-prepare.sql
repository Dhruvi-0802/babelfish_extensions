--view to view
CREATE VIEW demo_upgrade_view AS SELECT * FROM sys.objects
GO

--computed column to function
CREATE TABLE demo_upgrade_t1 (a fixeddecimal, b fixeddecimal, c AS square(a))
GO

--computed column to operator
CREATE VIEW demo_upgrade_view2 AS SELECT a+b FROM demo_upgrade_t1
GO

--table to collation
CREATE TABLE demo_collation(col varchar(20) COLLATE Greek_CS_AS)
GO

--udtype to type
CREATE TYPE demo_type FROM varchar(11) NOT NULL
GO
