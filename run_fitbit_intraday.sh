#!/bin/bash
source /home/pablo.morenomunoz/fitbit_project/venv/bin/activate
/home/pablo.morenomunoz/fitbit_project/venv/bin/python /home/pablo.morenomunoz/fitbit_project/fitbit_intraday.py >> /home/pablo.morenomunoz/fitbit_project/logs/fitbit_intrady.log 2>&1
