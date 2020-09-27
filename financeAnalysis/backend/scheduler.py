# Look into Airflow instead https://www.saturncloud.io/s/job-scheduling-with-python/

from crontab import CronTab

cron = CronTab(user='root')
job = cron.new(command='source /app/venv/bin/activate && python get_stocks.py')
job.minute.on(0)
job.hour.on(21) #UTC Time when stock market closes
cron.write()