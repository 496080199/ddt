from .trade import *
from django.shortcuts import render
from django.http import HttpResponse

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db import connection
from pytz import timezone



tz=timezone('Asia/Shanghai')

scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.start()
print("Scheduler started!")


#scheduler.add_job(sell, "cron", id='sell', day='*', hour='*', minute='*/15', second='59',replace_existing=True,
#  kwargs={})
#scheduler.add_job(sell, "cron", id='sell', day='*', hour='*', minute='*/10', second='59',replace_existing=True,
 #                     kwargs={})
scheduler.add_job(compensate, "cron", id='compensate', day='*', hour='*', minute='*/5', second='0', replace_existing=True,
                      kwargs={})
register_events(scheduler)

def matchtoken(token):
    validate=False
    if token == settings.TOKEN:
        validate=True
    return validate



def stat(request,token,cid):
    if matchtoken(token):
        try:
            cast = Cast.objects.get(pk=cid)
        except:
            message = '任务不存在'
            return HttpResponse(message)
        castinfo=',交易名称为'+str(cast.name)+',交易对为'+str(cast.symbol)+',交易额为'+str(cast.buyamount)+',增长百分比为'+str(cast.sellpercent)+'%'
        job = scheduler.get_job(job_id=str(cast.id))
        if job:
            message='任务ID:'+str(cid)+'已运行'+castinfo+',下次运行时间:'+str(job.next_run_time)
        else:
            message='任务ID:'+str(cid)+'未运行'+castinfo
    else:
        message = '非法请求'
    return HttpResponse(message)
def load(request,token,cid,hour):

    if matchtoken(token):
        try:
            cast = Cast.objects.get(pk=cid)
        except:
            message = '任务不存在'
            return HttpResponse(message)
        job = scheduler.get_job(job_id=str(cast.id))
        if job:
            job.remove()
            message='任务已重载'
        else:
            message='任务已加载'
        scheduler.add_job(buy, "cron", id=str(cast.id), day='*', hour='*/'+str(hour), minute='5', second='30',misfire_grace_time=3600, kwargs={'cid': cast.id})
        #scheduler.add_job(buy, "cron", id=str(cast.id), day='*', hour=str(hour), minute='5', second='30',
        #                  kwargs={'cid': cast.id})
        register_events(scheduler)

    else:
        message = '非法请求'
    return HttpResponse(message)
def pause(request,token,cid):
    if matchtoken(token):
        job=scheduler.get_job(job_id=str(cid))
        if job:
            job.remove()
            message='任务已暂停'
        else:
            message='无此任务'
    else:
        message='非法请求'

    return HttpResponse(message)

# Create your views here.

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse('404')
