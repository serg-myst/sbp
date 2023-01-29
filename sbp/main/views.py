from django.shortcuts import render
from django.views.generic import ListView
from main.models import Records, OpType
import datetime
from django.http import HttpResponseNotFound, JsonResponse
from main.utils import PaginationMixin, Datamixin
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string


class SbpHome(PaginationMixin, Datamixin, ListView):
    model = Records
    template_name = 'main/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        dict = Records.get_total_bank_sum()
        context['total'] = dict.get('total')
        context['total_sum'] = dict.get('total_sum')

        shop_paginate_context = self.get_shop_paginate_context()
        records_paginate_context = self.get_records_paginate_context()
        mixin_context = self.get_shop_details()

        return context | shop_paginate_context | records_paginate_context | mixin_context


def change_operation(request):
    value = request.POST.get("answer", "Undefined")
    op_type = get_object_or_404(OpType, pk=1)
    op_type.op_type = int(value)
    op_type.save()
    return redirect('home')


def show_details(request, year, month, day, bank):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        date = datetime.datetime(int(year), int(month),
                                 int(day))
        operations = Records.get_operations_by_day(date, bank)
        return JsonResponse(data={'data': render_to_string(
            'main/_modal_text.html',
            {
                'operations': operations,
            })})


class SearchHome(PaginationMixin, Datamixin, ListView):
    model = Records
    template_name = 'main/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('q')
        if not search_query:
            search_query = 99999

        search_query_date = self.request.GET.get('d')
        if not search_query_date:
            search_query_date = None
        else:
            search_query_date = datetime.datetime.strptime(search_query_date, "%Y-%m-%d")

        dict = Records.get_total_bank_sum()
        context['total'] = dict.get('total')
        context['total_sum'] = dict.get('total_sum')
        context['shop_number'] = search_query

        shop_paginate_context = self.get_shop_paginate_context(int(search_query))
        records_paginate_context = self.get_records_paginate_context(search_query_date)
        mixin_context = self.get_shop_details()

        return context | shop_paginate_context | records_paginate_context | mixin_context


class ShowShopDetails(PaginationMixin, ListView):
    model = Records
    template_name = 'main/shop_details.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.kwargs.get('shop')
        dict = Records.get_operations_by_shop(shop)
        context['shop'] = shop
        context['total_o'] = dict.get('total_o')
        context['total_v'] = dict.get('total_v')
        context['total_k'] = dict.get('total_k')
        context['shopdetail'] = True
        context['op_type'] = OpType.get_op_type().op_type

        paginate_context = self.get_other_paginate_context(dict.get('operations'))

        return context | paginate_context


class ShowShopOperations(PaginationMixin, ListView):
    model = Records
    template_name = 'main/details.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        date = datetime.datetime(int(self.kwargs.get('year')), int(self.kwargs.get('month')),
                                 int(self.kwargs.get('day')))
        shop = self.kwargs.get('shop')
        bank = self.kwargs.get('bank')
        dict = Records.get_operations_by_shift(date, bank, shop)
        context['shopdetail'] = False
        context['day_shift'] = date
        context['bank'] = bank
        context['shop'] = shop
        context['total_o'] = dict.get('total_o')
        context['total_v'] = dict.get('total_v')
        context['total_k'] = dict.get('total_k')

        paginate_context = self.get_other_paginate_context(dict.get('operations'))

        return context | paginate_context


class ShowDetails(PaginationMixin, ListView):
    model = Records
    template_name = 'main/details.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        bank = self.kwargs.get('bank')
        date = datetime.datetime(int(self.kwargs.get('year')), int(self.kwargs.get('month')),
                                 int(self.kwargs.get('day')))
        context = super().get_context_data(**kwargs)
        dict = Records.get_operations_by_shift(date, bank)
        context['day_shift'] = date
        context['bank'] = bank
        context['shop'] = 99999
        context['total_o'] = dict.get('total_o')
        context['total_v'] = dict.get('total_v')
        context['total_k'] = dict.get('total_k')
        context['shopdetail'] = False
        context['op_type'] = OpType.get_op_type().op_type
        paginate_context = self.get_other_paginate_context(dict.get('operations'))

        return context | paginate_context


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
