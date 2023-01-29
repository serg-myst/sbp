from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from main.models import Records, OpType


class Datamixin:

    def get_shop_details(self, **kwargs):
        context = kwargs
        top_shops = Records.get_top_shops()
        context['top_shops'] = top_shops.get('top_shops')
        context['top_shops_date'] = top_shops.get('top_shops_date')
        context['op_type'] = OpType.get_op_type().op_type

        return context


class PaginationMixin:
    paginate_by = 10
    paginate_by_records = 9

    def return_pagination(self, list, key, page, context):
        try:
            context[key] = list.page(page)
        except PageNotAnInteger:
            context[key] = list.page(1)
        except EmptyPage:
            context[key] = list.page(list.num_pages)

        return context

    def get_shop_paginate_context(self, shop_number=99999, **kwargs):
        context = kwargs
        page = self.request.GET.get('page')
        p_shops = Paginator(Records.get_shops(shop_number), self.paginate_by)

        return self.return_pagination(p_shops,'shops',page,context)

    def get_records_paginate_context(self, date=None, **kwargs):
        context = kwargs
        p_operations = Paginator(Records.get_operations(date), self.paginate_by_records)
        page = self.request.GET.get('other-page')

        return self.return_pagination(p_operations,'operations',page,context)

    def get_other_paginate_context(self, recordset, **kwargs):
        context = kwargs
        p_operations = Paginator(recordset, self.paginate_by)
        page = self.request.GET.get('other-page')

        return self.return_pagination(p_operations, 'operations', page, context)
