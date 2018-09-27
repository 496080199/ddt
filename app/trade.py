from .models import *
from .log import log
from .mail import mail
from django.conf import settings
from decimal import Decimal
from django.db.models import Q
import ccxt,datetime,traceback,time

from pytz import timezone

tz=timezone('Asia/Shanghai')

def getdt():
    dt=str(datetime.datetime.now(tz).isoformat())+'----'
    return dt

def login(excode,apikey,secretkey):
    exchange = eval("ccxt." + excode + "()")
    exchange.apiKey = apikey
    exchange.secret = secretkey
    exchange.options['createMarketBuyOrderRequiresPrice'] = False
    exchange.options['marketBuyPrice'] = False
    if settings.USE_PROXY:
        exchange.proxies = {'http':'http://'+settings.PROXY_ADDR,'https':'http://'+settings.PROXY_ADDR}
    return exchange

def comcuravg(cast,exchange):
    orderbook={}
    for num in range(300):
        try:
            orderbook = exchange.fetch_order_book(symbol=cast.symbol)
            break
        except:
            time.sleep(0.3)
            continue
    bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
    currentprice = Decimal((ask + bid) / 2)
    sumactualfilled = Decimal(0.0)
    sumcost = Decimal(0.0)
    casthiss = CastHis.objects.filter(Q(process=0)&Q(cast_id=cast.id))
    if casthiss.exists():
        sumactualfilled = Decimal(casthiss.aggregate(Sum('actualfilled'))['actualfilled__sum'])
        sumcost = Decimal(casthiss.aggregate(Sum('cost'))['cost__sum'])
    if sumactualfilled == Decimal(0.0) or sumcost == Decimal(0.0):
        averageprice = currentprice
    else:
        averageprice = sumcost / sumactualfilled
    return currentprice,averageprice,sumactualfilled

def buy(cid):
    try:
        cast = Cast.objects.get(pk=cid)
        symbol = cast.symbol
        log.warn(getdt() + str(symbol)+'开始买入')
        amount = cast.buyamount
        exchange = login(cast.excode, cast.apikey, cast.secretkey)
        currentprice, averageprice, sumactualfilled = comcuravg(cast,exchange)
        log.warn('当前价格：'+str(currentprice)+'；持有均价：'+str(averageprice))
        if currentprice <= averageprice:
            orderdata = exchange.create_market_buy_order(symbol=symbol, amount=float(amount), params={'cost': float(amount)})
            if isinstance(orderdata['id'],str):
                orderinfo = exchange.fetch_order(symbol=symbol, id=orderdata['id'])
                casthis=CastHis(cast_id=cid,
                                orderid=orderinfo['id'],
                                orderstatus=orderinfo['status'],
                                ordertype=orderinfo['type'],
                                orderside=orderinfo['side'],
                                average=Decimal(orderinfo['average']),
                                cost=Decimal(orderinfo['cost']),
                                filled = Decimal(orderinfo['info']['field-amount']),
                                fees=Decimal(orderinfo['info']['field-fees']),
                                actualfilled=(Decimal(orderinfo['info']['field-amount']) - Decimal(
                                    orderinfo['info']['field-fees'])))
                casthis.save()
                log.warn(getdt()+ str(symbol )+'买入成功')
        else:
            log.warn('未满足买入条件')

    except:
        log.warn('买入异常：\n'+traceback.format_exc())


def compensate():
    try:
        casthiss=CastHis.objects.exclude(orderstatus='closed')
        if casthiss.exists():
            for casthis in casthiss:
                cast=Cast.objects.get(pk=casthis.cast_id)
                exchange = login(cast.excode, cast.apikey, cast.secretkey)
                orderinfo = exchange.fetch_order(symbol=cast.symbol, id=casthis.orderid)
                if orderinfo['status'] == 'closed':
                    casthis.orderstatus = orderinfo['status']
                    casthis.average= Decimal(orderinfo['average'])
                    casthis.cost = Decimal(orderinfo['cost'])
                    casthis.filled = Decimal(orderinfo['info']['field-amount'])
                    casthis.fees = Decimal(orderinfo['info']['field-fees'])
                    casthis.actualfilled = (Decimal(orderinfo['info']['field-amount']) - Decimal(
                    orderinfo['info']['field-fees']))
                    casthis.save()
    except:
        pass
def sell():
    try:
        casts=Cast.objects.all()
        for cast in casts:
            log.warn(getdt() + str(cast.symbol) + '开始卖出')
            exchange = login(cast.excode, cast.apikey, cast.secretkey)
            currentprice, averageprice, sumactualfilled = comcuravg(cast, exchange)
            wantprice=averageprice*(Decimal(cast.sellpercent)/100+1)
            log.warn('当前价格：' + str(currentprice) + '；持有均价：'+str(averageprice)+'；预期均价：' + str(wantprice))
            if currentprice > wantprice:
                try:
                    mail(str(cast.symbol)+'已达卖出条件','卖出通知')
                except:
                    pass
                orderdata=exchange.create_market_sell_order(symbol=cast.symbol, amount=float(sumactualfilled*0.99))
                if isinstance(orderdata['id'], str):
                    casthiss=CastHis.objects.filter(Q(process=0)&Q(cast_id=cast.id))
                    casthiss.update(process=1)
                    log.warn(getdt() +str(cast.symbol)+ '卖出成功')
            else:
                log.warn('未满足卖出条件')

    except:
        log.warn('卖出异常：\n' + traceback.format_exc())


