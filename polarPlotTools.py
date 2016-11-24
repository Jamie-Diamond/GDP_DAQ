from sensor_log_ToolBox import data_read
from windDataTools import getWindData

Mag, Gyro, GPS, Accel, Lin_Accel = data_read()
wind = getWindData(GPS)

print(gps)
print(wind)

