from django.db.models import *
from django_apscheduler.models import DjangoJob

# Create your models here.
class Cast(Model):
    name = CharField('名称', max_length=50,null=True)
    excode = CharField('交易所代码', max_length=50,null=False)
    apikey = CharField('API_KEY', max_length=100,null=False)
    secretkey = CharField('SECRET_KEY', max_length=100,null=False)
    symbol = CharField('交易对', max_length=20,null=False)
    buyamount = DecimalField('金额', max_digits=40, decimal_places=20,null=False)
    sellpercent = DecimalField('卖出比率', max_digits=5, decimal_places=2,null=False)
class CastHis(Model):
    cast = ForeignKey('Cast', on_delete=CASCADE,null=True)
    orderid = CharField('订单ID', max_length=100)
    orderstatus = CharField('订单状态', max_length=10,db_index=True)
    datetime = DateTimeField('时间',auto_now_add=True)
    ordertype = CharField('类型', max_length=20)
    orderside = CharField('方向', max_length=20)
    average = DecimalField('成交均价', max_digits=40, decimal_places=20)
    cost = DecimalField('成本', max_digits=40, decimal_places=20)
    filled = DecimalField('成交数量', max_digits=40, decimal_places=20)
    fees = DecimalField('成交手续费', max_digits=40, decimal_places=20)
    actualfilled = DecimalField('实际成交数量', max_digits=40, decimal_places=20)
    process = BooleanField('处理',default=0)

    class Meta:
        index_together = ["cast", "process"]