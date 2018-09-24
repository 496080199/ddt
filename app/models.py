from django.db.models import *

# Create your models here.
class Cast(Model):
    name = CharField('名称', max_length=50)
    excode = CharField('交易所代码', max_length=50)
    symbol = CharField('交易对', max_length=20)
    buyamount = DecimalField('金额', max_digits=40, decimal_places=20)
    sellpercent = DecimalField('卖出比率', max_digits=5, decimal_places=2)
class CastHis(Model):
    cast = ForeignKey('Cast', on_delete=CASCADE, null=True)
    datetime = DateTimeField('时间',auto_now=True)
    type = CharField('类型', max_length=20)
    side = CharField('方向', max_length=20)
    price = DecimalField('j价格', max_digits=40, decimal_places=20)