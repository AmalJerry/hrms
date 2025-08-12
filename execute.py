import scheduler_jobs
import workanniversary
import empwork_anniversary
import birthday_mail
import attendance_regularization
import leave_credited
import notification
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
scheduler = BackgroundScheduler()
# scheduler.configure(timezone=utc)


# scheduler.add_job(scheduler_jobs.update_attendance,
#                   trigger='cron', hour=20, minute=40)
scheduler.add_job(scheduler_jobs.update_attendance,trigger='cron', hour=23, minute=45)
# scheduler.add_job(scheduler_jobs.update_attendance, 'interval', seconds=20)

scheduler.add_job(workanniversary.work_anniversary,trigger='cron', hour=10, minute=00)

scheduler.add_job(empwork_anniversary.emp_work_anniversary,trigger='cron', hour=10, minute=00)

scheduler.add_job(birthday_mail.birthdaymail,trigger='cron', hour=10, minute=00)

scheduler.add_job(attendance_regularization.att_regularization,trigger='cron', hour=10, minute=00)
                  
scheduler.add_job(notification.notification_employee,trigger='cron', hour=10, minute=00)

scheduler.add_job(leave_credited.leavecredited,trigger='cron', hour=6, minute=30)

scheduler.add_job(scheduler_jobs.delete_duplicate_attendance,trigger='cron', hour=23, minute=30)

scheduler.start()
