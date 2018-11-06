from celery import task

from .autocom import check

@task()
def check_autocom_daily():
    check(action="daily")

@task()
def check_darujme():
    darujme.check_for_new_payments()
