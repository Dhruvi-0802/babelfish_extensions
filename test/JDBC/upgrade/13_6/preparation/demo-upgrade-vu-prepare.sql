create view demo_upgrade_view as select * from sys.objects
go

create table demo_upgrade_t1 (a fixeddecimal, b fixeddecimal, c as square(a))
go

create view demo_upgrade_view2 as select a+b from demo_upgrade_t1
go