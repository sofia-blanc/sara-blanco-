import os

html_path = 'C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_interactive.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'window.addEventListener("message",hm);'

handler = (
    'if(ev.data.type==="AUTOOS_HARDWARE_FAULT"){'
    'var dev=ev.data.deviceCode;'
    's("falla");'
    'ae("fault_"+dev);'
    'if(dev==="DEV_GPS_01"){'
    'd(function(prev){return prev.map(function(item){return item.codigo==="DEV_GPS_RTK"||item.codigo==="DEV_GPS_01"?{...item,estado:"falla",salud_porcentaje:18}:item;});});'
    'l(function(prev){return{...prev,sensorHealthPct:82.4,sensorsOperational:14};});'
    '}else if(dev==="DEV_BATTERY_BMS"){'
    'd(function(prev){return prev.map(function(item){return item.codigo==="DEV_BMS_01"||item.codigo==="DEV_BATTERY_BMS"?{...item,estado:"falla",salud_porcentaje:22}:item;});});'
    'l(function(prev){return{...prev,batteryTemp:51.5,batterySoc:Math.min(prev.batterySoc,25),cpuUsage:78.5,sensorHealthPct:84,sensorsOperational:14};});'
    '}else if(dev==="DEV_LIDAR_01"){'
    'd(function(prev){return prev.map(function(item){return item.codigo==="DEV_LIDAR_01"?{...item,estado:"falla",salud_porcentaje:15}:item;});});'
    'l(function(prev){return{...prev,sensorHealthPct:79.5,sensorsOperational:13};});'
    '}else if(dev==="DEV_CAM_FRONT"){'
    'd(function(prev){return prev.map(function(item){return item.codigo==="DEV_CAM_FRONT"?{...item,estado:"falla",salud_porcentaje:20}:item;});});'
    'l(function(prev){return{...prev,sensorHealthPct:85,sensorsOperational:15};});'
    '}else if(dev==="DEV_ACT_BRAKE"||dev==="DEV_ACT_STEER"){'
    'd(function(prev){return prev.map(function(item){return item.codigo==="DEV_BRAKE_BOOSTER"||item.codigo==="DEV_STEER_BY_WIRE"?{...item,estado:"falla",salud_porcentaje:25}:item;});});'
    'l(function(prev){return{...prev,sensorHealthPct:88,sensorsOperational:15};});'
    '}else{'
    'd(function(prev){return prev.map(function(item){return item.codigo===dev?{...item,estado:"falla",salud_porcentaje:20}:item;});});'
    'l(function(prev){return{...prev,sensorHealthPct:85,sensorsOperational:14};});'
    '}'
    '}'
    'if(ev.data.type==="AUTOOS_RESET_DEVICE"||ev.data.type==="AUTOOS_RESET_ALL_FAULTS"){'
    's("operativo");'
    'ae(null);'
    'l(y);'
    'd(b);'
    'p(ee);'
    '}'
    'if(ev.data.type==="AUTOOS_UPDATE_BATTERY"){'
    'if(ev.data.batteryLevel!==undefined){'
    'var nSoc=Number(ev.data.batteryLevel);'
    'l(function(prev){return{...prev,batterySoc:nSoc,batteryRangeKm:Math.round(nSoc*5.0)};});'
    '}'
    '}'
)

replacement = handler + target

if target in content:
    new_content = content.replace(target, replacement, 1)
    copies = [
        'C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_interactive.html',
        'C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/autoos_interactive.html',
        'C:/Users/Usuario/Desktop/mio/universidad/autoos/modules/autoos_interactive.html',
        'C:/Users/Usuario/Desktop/mio/universidad/autoos/web/dist/autoos_interactive.html',
        'C:/Users/Usuario/Desktop/mio/universidad/autoos/web/public/autoos_interactive.html'
    ]
    for cpath in copies:
        with open(cpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Updated:', cpath)
else:
    print('Target not found!')
