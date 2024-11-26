--delete from connector where createdby = 'locust seed'
--delete from chargingstation where createdby = 'locust seed'
--delete from chargingstationlocation where createdby = 'locust seed'

declare @numSeededChargingStations int = 20000;
declare @evseId varchar(32);
declare @chargingStationLocationTableOutput TABLE (
	Id bigint not null
);
declare @chargingStationTableOutput TABLE (
	Id bigint not null
);
declare @i int = 0;

WHILE @i < @numSeededChargingStations
BEGIN
-- start
	set @evseId = (select 'DK*OKO*EZ' + replace(newid(), '-', ''));	

	INSERT dbo.ChargingStationLocation 
		OUTPUT INSERTED.Id INTO @chargingStationLocationTableOutput
	VALUES (
		getdate(), 
		'Locust seed', 
		getdate(), 
		null, 
		0, 
		newid(), 
		'locust test location ' + convert(varchar(10), @i),
		'Viby', 
		null, 
		0, 
		0, 
		null, 
		0, 
		123, 
		8000, 
		'Test road ' + convert(varchar(10), @i), 
		5100 + @i, 
		10, 
		null, 
		'', 
		'')

	INSERT dbo.ChargingStation 
		OUTPUT INSERTED.Id INTO @chargingStationTableOutput
	VALUES (getdate(), 'Locust seed', getdate(), null, 0, 
		'locust-cs-' + convert(varchar(10), @i), 
		900, 180, (select top 1 Id from @chargingStationLocationTableOutput), 'LOCUST', 0, 1727260502711000000, 1, 0, 13, 0, 0, null, 0)

	INSERT INTO dbo.Connector 
	VALUES (getdate(), 'Locust seed', getdate(), 'Locust seed', 0, 1, 
		(select top 1 Id from @chargingStationTableOutput),
		20, 11, 20, 70, 1727260502819000000,80, 1, null, @evseId, 0)

-- end
delete from @chargingStationLocationTableOutput
delete from @chargingStationTableOutput
set @i = @i + 1
END

select * from chargingstation
select * from ChargingStationLocation
select * from Connector