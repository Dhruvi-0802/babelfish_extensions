CREATE TABLE test_sp_helpsrvrolemember_tbl (ServerRole sys.SYSNAME,
											MemberName sys.SYSNAME,
											MemberSID sys.VARBINARY(85));

CREATE LOGIN test_sp_helpsrvrolemember_login WITH PASSWORD='123'
GO
