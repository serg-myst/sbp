from django.db import models
from django.db.models import Case, When, Count, Sum, DateTimeField
from django.db.models.functions import TruncDay
import datetime


class Records(models.Model):
    bank_spb = models.CharField(max_length=128)
    shopid = models.IntegerField()
    op_merch = models.CharField(max_length=128)
    op_date = models.DateTimeField()
    day_shift = models.DateField(primary_key=True)  # Не важно, в данной таблице нет ID. Поэтому primary_key
    op_sum = models.DecimalField(decimal_places=2, max_digits=15)
    op_com = models.DecimalField(decimal_places=2, max_digits=15)

    def __str__(self):
        return f'{self.bank_spb} | {self.shopid} | {self.day_shift}'

    @staticmethod
    def get_op_type():
        return OpType.objects.filter(pk=1).first().op_type

    @staticmethod
    def get_total_sum(record_set):
        o = 0
        v = 0
        k = 0
        for op in record_set:
            o += 0 if op.get('o') is None else op.get('o')
            v += 0 if op.get('v') is None else op.get('v')
            k += 0 if op.get('k') is None else op.get('k')

        return o, v, k

    @staticmethod
    def get_total_bank_sum():
        total = Records.objects.values('bank_spb').annotate(count=Count('bank_spb'), total_sum=Sum('op_sum')).order_by(
            'bank_spb')
        total_sum = 0
        for op in total:
            total_sum += op.get('total_sum')
        return {'total': total, 'total_sum': total_sum}

    @staticmethod
    def get_shops(shop_number=99999):
        if shop_number == 99999:
            shops = Records.objects.values('shopid').annotate(scount=Count('shopid')).order_by('shopid')
        else:
            shops = Records.objects.filter(shopid=shop_number).values('shopid').annotate(
                scount=Count('shopid')).order_by('shopid')
        return shops

    # https://docs.djangoproject.com/en/4.1/ref/models/database-functions/#extract
    @staticmethod
    def get_top_shops():
        currentdate = datetime.datetime.today()
        start_day = currentdate.combine(currentdate.date(), currentdate.min.time()) - datetime.timedelta(days=1)
        end_day = start_day.combine(start_day.date(), start_day.max.time())
        top_shops = Records.objects.filter(op_date__range=(start_day, end_day)).values(
            'shopid', 'bank_spb').annotate(start_day=Count(TruncDay('op_date')),
                                           total_shop=Count('shopid'), total_bank=Count('bank_spb')).annotate(
            total=Sum('op_sum')).order_by('-total')[:5]
        return {'top_shops': top_shops, 'top_shops_date': start_day}

    @staticmethod
    def get_operations_by_shift(date, bank, shop=None):
        op_type = Records.get_op_type()
        if shop is None:
            if op_type == 0:
                operations = Records.objects.values('op_date').filter(day_shift=date, bank_spb=bank).annotate(
                    o=Case(When(op_sum__gt=0, then='op_sum')), v=Case(When(op_sum__lt=0, then='op_sum')),
                    k=Case(When(op_com__gt=0, then='op_com'))).order_by(
                    'op_date')
            else:
                operations = Records.objects.values(
                    'op_date').filter(
                    op_date__range=(
                        date.combine(date.date(), date.min.time()), date.combine(date.date(), date.max.time())),
                    bank_spb=bank).annotate(
                    o=Case(When(op_sum__gt=0, then='op_sum')), v=Case(When(op_sum__lt=0, then='op_sum')),
                    k=Case(When(op_com__gt=0, then='op_com'))).order_by(
                    'op_date')
        else:
            if op_type == 0:
                operations = Records.objects.values('op_date').filter(day_shift=date, bank_spb=bank,
                                                                      shopid=shop).annotate(
                    o=Case(When(op_sum__gt=0, then='op_sum')), v=Case(When(op_sum__lt=0, then='op_sum')),
                    k=Case(When(op_com__gt=0, then='op_com'))).order_by(
                    'op_date')
            else:
                operations = Records.objects.values(
                    'op_date').filter(op_date__range=(
                    date.combine(date.date(), date.min.time()), date.combine(date.date(), date.max.time())),
                    bank_spb=bank,
                    shopid=shop).annotate(
                    o=Case(When(op_sum__gt=0, then='op_sum')), v=Case(When(op_sum__lt=0, then='op_sum')),
                    k=Case(When(op_com__gt=0, then='op_com'))).order_by(
                    'op_date')

        o, v, k = Records.get_total_sum(operations)

        return {'operations': operations, 'total_o': o, 'total_v': v, 'total_k': k}

    @staticmethod
    def get_operations(date=None):
        op_type = Records.get_op_type()
        if date is None:
            if op_type == 0:
                operations = Records.objects.values('day_shift', 'bank_spb').annotate(
                    o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                    k=Sum(Case(When(op_com__gt=0, then='op_com'))), total=Count('day_shift')).order_by(
                    '-day_shift')
            else:
                operations = Records.objects.annotate(
                    start_day=TruncDay('op_date')).values('start_day', 'bank_spb').annotate(
                    o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                    k=Sum(Case(When(op_com__gt=0, then='op_com'))), total_days=Count('start_day')).order_by(
                    '-start_day')
        else:
            if op_type == 0:
                operations = Records.objects.values('day_shift', 'bank_spb').filter(day_shift=date).annotate(
                    o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                    k=Sum(Case(When(op_com__gt=0, then='op_com'))), total=Count('day_shift')).order_by(
                    '-day_shift')
            else:
                operations = Records.objects.annotate(
                    start_day=TruncDay('op_date')).values('start_day', 'bank_spb').filter(start_day=date).annotate(
                    o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                    k=Sum(Case(When(op_com__gt=0, then='op_com'))), total_days=Count('start_day')).order_by(
                    '-start_day')

            # operation_sum = Records.objects.raw(
            #    'SELECT'
            #    '   day_shift,'
            #    '   bank_spb,'
            #    '   sum(case when op_sum<0 then op_sum else 0 end) as v,'
            #    '   sum(case when op_sum>0 then op_sum else 0 end) as o,'
            #    '   sum(op_com) as k'
            #    ' FROM sbp_operations group by day_shift, bank_spb'+filter_date+
            #    ' order by day_shift DESC')

        return operations

    @staticmethod
    def get_operations_by_shop(shop):
        op_type = Records.get_op_type()
        if op_type == 0:
            operations = Records.objects.values('day_shift', 'shopid', 'bank_spb').filter(shopid=shop).annotate(
                o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                k=Sum(Case(When(op_com__gt=0, then='op_com'))), total=Count('day_shift')).order_by(
                '-day_shift')
        else:
            operations = Records.objects.filter(shopid=shop).annotate(start_day=TruncDay('op_date')).values('start_day',
                                                                                                            'shopid',
                                                                                                            'bank_spb').annotate(
                o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
                k=Sum(Case(When(op_com__gt=0, then='op_com'))), total=Count('start_day')).order_by(
                '-start_day')

        o, v, k = Records.get_total_sum(operations)

        return {'operations': operations, 'total_o': o, 'total_v': v, 'total_k': k}

        # operation_sum = Records.objects.raw(
        #    'SELECT'
        #    '   day_shift,'
        #    '   bank_spb,'
        #    '   sum(case when op_sum<0 then op_sum else 0 end) as v,'
        #    '   sum(case when op_sum>0 then op_sum else 0 end) as p,'
        #    '   sum(op_com) as k'
        #    ' FROM sbp_operations'
        #    ' where shopid = %s'
        #    ' group by bank_spb, day_shift'
        #    ' order by day_shift DESC', [shop, ])

    @staticmethod
    def get_operations_by_day(date, bank):
        start_day = date.combine(date.date(), date.min.time())
        end_day = start_day.combine(start_day.date(), start_day.max.time())
        op_type = Records.get_op_type()
        if op_type == 0:
            operations = Records.objects.filter(day_shift__range=(start_day, end_day), bank_spb=bank).annotate(
                o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
            ).order_by(
                'op_date')
        else:
            operations = Records.objects.filter(op_date__range=(start_day, end_day), bank_spb=bank).annotate(
                o=Sum(Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum'))),
            ).order_by(
                'op_date')
        return operations

    @staticmethod
    def get_operations_by_day_total(date, bank):
        start_day = date.combine(date.date(), date.min.time())
        end_day = start_day.combine(start_day.date(), start_day.max.time())
        op_type = Records.get_op_type()
        if op_type == 0:
            operations = Records.objects.filter(day_shift__range=(start_day, end_day),
                                                bank_spb=bank).annotate(start_day=TruncDay('day_shift')).values(
                'shopid', 'start_day', 'bank_spb').annotate(total_shop=Count('shopid'), total_day=Count('start_day'),
                                                            total_bank=Count('bank_spb'), o=Sum(
                    Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum')))).values(
                'shopid', 'start_day', 'bank_spb', 'o', 'v').order_by(
                'start_day', '-o')
        else:
            operations = Records.objects.filter(op_date__range=(start_day, end_day),
                                                bank_spb=bank).annotate(start_day=TruncDay('op_date')).values(
                'shopid', 'start_day', 'bank_spb').annotate(total_shop=Count('shopid'), total_day=Count('start_day'),
                                                            total_bank=Count('bank_spb'), o=Sum(
                    Case(When(op_sum__gt=0, then='op_sum'))), v=Sum(Case(When(op_sum__lt=0, then='op_sum')))).values(
                'shopid', 'start_day', 'bank_spb', 'o', 'v').order_by(
                'start_day', '-o')

        return operations

    class Meta:
        db_table = 'sbp_operations'
        managed = False
        ordering = ['-day_shift']


class OpType(models.Model):
    id = models.IntegerField(primary_key=True)
    op_type = models.IntegerField()

    def __str__(self):
        if self.op_type == 0:
            return 'По дате зачисления'
        else:
            return 'По дате операции'

    @staticmethod
    def get_op_type():
        return OpType.objects.filter(id=1).first()

    class Meta:
        db_table = 'sbp_op_type'
