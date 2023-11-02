#!/usr/bin/env python3
import time
import logging
from time import strftime, localtime
from gpiozero import OutputDevice


ON_THRESHOLD = 70  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 50  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 17  # Which GPIO pin you're using to control the fan.
EPOCH_INTERVAL = 1800 # (seconds) after last power off, to switch on the fan minuts.
TIME_FAN_INTERVAL = 120 # (seconds) after last power off, to switch on the fan 1/2 minuts.
PATH_TO_LOG_FILE = 'PUT_HERE_YOUR_PATH_TO_SAVE_THE_LOGS/Logs/logPi_Fan_Controller.log' # Here you can put your path to save the logfile

def get_temp():
    """Get the core temperature.
    Read file from /sys to get CPU temp in temp in C *1000
    Returns:
        int: The core temperature in thousanths of degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp_str = f.read()

    try:
        return int(temp_str) / 1000
    except (IndexError, ValueError,) as e:
        raise RuntimeError('Could not parse temperature output.') from e

def add_logg(CODE:int, DATA:str):
    '''IN PROGRESS'''
    print(CODE, DATA)
    return

def power_on_fan_task(LAST_POWER_OFF:int, EPOCH_INTERVAL:int, TIME_FAN_INTERVAL:int , FAN:OutputDevice, TEMP:float):
    """Power on the fan during 1/2 minuts to prolonge the rpi life."""

    # VARIABLES
    epoch_now = int(time.time())

    if epoch_now >= (LAST_POWER_OFF+EPOCH_INTERVAL):
        temp = get_temp()
        FAN.on()
        hora = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        logging.info(hora + '   003 POWER_ON    TMP:' + str(int(temp)) + 'º     The fan has turned on due to the function.')
        
        time.sleep(TIME_FAN_INTERVAL)
        FAN.off()
        temp = get_temp()
        last_power = int(time.time())
        hora = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        logging.info(hora + '   001 POWER_OFF   TMP:' + str(int(temp)) + 'º     The fan has been turned off due to the function.')
    else:
        return LAST_POWER_OFF

    return last_power

if __name__ == '__main__':
    # Creating the log file to save the logs.
    logging.basicConfig(format='%(levelname)s:%(message)s', filename = PATH_TO_LOG_FILE, encoding='utf-8', level=logging.DEBUG)
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        hora = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        logging.warning(hora + '   005  WRONG_TEMP  INVALID     The temperature selected to ON_THRESHOLD is lowe than OFF_THRESHOLD.')
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')
    

    fan = OutputDevice(GPIO_PIN)
    # Here we are creating th first epoch time for the half hour count.
    last_power = int(time.time())
    

    while True:

        temp = get_temp()
        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        if temp > ON_THRESHOLD and not fan.value:
            fan.on()
            hora = strftime("%a, %d %b %Y %H:%M:%S", localtime())
            logging.info(hora + '   001 POWER_ON    TMP:' + str(int(temp)) + 'º     The fan has turned on due to the temperature.' )

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < OFF_THRESHOLD:
            fan.off()
            last_power = int(time.time())
            hora = strftime("%a, %d %b %Y %H:%M:%S", localtime())
            logging.info(hora + '   002 POWER_OFF   TMP:' + str(int(temp)) + 'º     The fan has been turned off due to the temperature.' )

        time.sleep(SLEEP_INTERVAL)
        last_power = power_on_fan_task(last_power , EPOCH_INTERVAL, TIME_FAN_INTERVAL, fan, temp)