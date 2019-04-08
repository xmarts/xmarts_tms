# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import mygeotab

username = 'javier.ramirez@sli.mx'
password = 'Javier0318*'
database = 'GSYEECA'

geo = mygeotab.API(
        username=username,
        password=password,
        database=database
    )

authenticate = geo.authenticate()





def calculate_litres_per_100km(from_date, to_date):

    odometer_records = geo.get('StatusData', 
                                  diagnosticSearch=dict(id='DiagnosticOdometerAdjustmentId'),
                                  deviceSearch=dict(engineVehicleIdentificationNumber='3HSDJAPT4HN513265'),
                                  toDate=to_date,
                                  fromDate=from_date)
    fuel_records = geo.get('StatusData',
                              diagnosticSearch=dict(id='DiagnosticDeviceTotalFuelId'),
                              deviceSearch=dict(engineVehicleIdentificationNumber='3HSDJAPT4HN513265'),
                              toDate=to_date,
                              fromDate=from_date)
    if len(odometer_records) == 0 or len(fuel_records) == 0:
        raise Exception('Device has not travelled in this time period or no fuel usage reported')
    odometer_change = odometer_records[-1]['data'] - odometer_records[0]['data']
    fuel_change = fuel_records[-1]['data'] - fuel_records[0]['data']
    return fuel_change / (odometer_change / 1000)

# end = datetime.utcnow()
# start = end - timedelta(days=365)
#xxx = geo.get('Device', engineVehicleIdentificationNumber='3HSDJAPT4HN513265')[0]
#print(xxx)
print(calculate_litres_per_100km(datetime.utcnow() - timedelta(days=10), datetime.utcnow()))



# data_list = []
# today = datetime.datetime.today()
# # yesterday = today - datetime.timedelta(days=1)

# if authenticate:
#     device = api.call('Get', typeName='Device')
    
#     for data in device:
#         vehicle_id = data.get('id')
#         vehicle_name = data.get('name')

#         params = {
#                 'deviceSearch': {'id': str(1160)},
#                 'diagnosticSearch': {'id': 'DiagnosticOdometerId'},
#                 'fromDate': today,
#                 }

#         diagnostic = api.get('StatusData', search=params)
#         if diagnostic:
#             odometer_mts = diagnostic[0]['data']
#             odometer_km = odometer_mts / 1000
#             print odometer_km, vehicle_name