from .trade import *
from django.shortcuts import render
from django.http import HttpResponse


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django_apscheduler.models import DjangoJob
from pytz import timezone

tz=timezone('Asia/Shanghai')

scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.start()

job = scheduler.get_job(job_id='sell')
if job:
    job.remove()
scheduler.add_job(sell, "cron", id='sell', day='*', hour='*', minute='*/15', second='0',
                      kwargs={})

def matchtoken(token):
    validate=False
    if token == settings.TOKEN:
        validate=True
    return validate



def stat(request,token,cid):
    if matchtoken(token):
        cast = Cast.objects.get(pk=cid)
        castinfo=',交易名称为'+str(cast.name)+',交易对为'+str(cast.symbol)+',交易额为'+str(cast.buyamount)+',增长百分比为'+str(cast.sellpercent)+'%'
        jobs = DjangoJob.objects.filter(name=str(cid))
        if jobs.exists():
            message=str(cid)+'已运行'+castinfo
        else:
            message=str(cid)+'未运行'+castinfo
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
        scheduler.add_job(buy, "cron", id=str(cast.id), day='*', hour='*', minute='*/'+str(hour), second='30',kwargs={'cid': cast.id})
        register_events(scheduler)

    else:
        message = '非法请求'
    return HttpResponse(message)
def pause(request,token,cid):
    if matchtoken(token):
        jobs = DjangoJob.objects.filter(name=str(cid))
        if jobs.exists():
            jobs.delete()
            message='任务已暂停'
        else:
            message='无此任务'
    else:
        message='非法请求'

    return HttpResponse(message)

# Create your views here.

def index(request):
    return HttpResponse('404')