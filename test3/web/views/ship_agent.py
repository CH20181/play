from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, re_path
from django.utils.safestring import mark_safe
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm
from web import models


class ShipGetMove(StarkModelForm):
    class Meta:
        model = models.Plan
        fields = ['title', 'move_time', 'next_port']
        widgets = {
            'move_time': DateTimePickerInput,
        }

    def __init__(self, *args, **kwargs):
        super(ShipGetMove, self).__init__(*args, **kwargs)
        self.fields['title'].queryset = models.PlanStatus.objects.filter(pk__in=[1, 2])


class ShipCheckModelForm(StarkModelForm):
    class Meta:
        model = models.Ship
        exclude = ['user', 'boat_status', 'status', 'port_in', 'display', 'location']

    def clean_IMO(self):
        IMO = self.cleaned_data.get('IMO')
        if len(IMO) < 7:
            raise ValidationError('输入的IMO长度不够！')
        return IMO

    def clean_MMSI(self):
        MMSI = self.cleaned_data.get('MMSI')
        if len(MMSI) < 7:
            raise ValidationError('输入的MMSI长度不够！')
        return MMSI


class ShipAgentHandler(StarkHandler):
    """
    代理公司视图
    """
    model_form_class = ShipCheckModelForm

    def display_plan(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '入港/入境/移泊计划'
        record_url = reverse('stark:web_plan_agent_list', kwargs={'ship_id': obj.pk})
        return mark_safe('<a  href="%s">添加</a>' % record_url)

    def display_move(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '出港/出境'
        record_url = reverse('stark:web_ship_agent_get_move', kwargs={'ship_id': obj.pk})
        return mark_safe('<a  href="%s">添加</a>' % record_url)

    def display_port(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '在港位置'
        location = obj.location
        if not location:
            return obj.port_in
        return '%s--%s' % (location, obj.port_in)

    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶名称'
        return '%s\n%s' % (obj.chinese_name, obj.english_name)

    def extra_urls(self):
        return [
            re_path(r'^add/move/(?P<ship_id>\d+)/$', self.wrapper(self.add_move), name=self.get_url_name('get_move')), ]

    def add_move(self, request, *args, **kwargs):
        """
        添加出港/出境
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user_id = 1
        ship_id = kwargs.get('ship_id')
        form = ShipGetMove()
        if request.method == 'POST':
            form = ShipGetMove(request.POST)
            if form.is_valid():
                title_num = form.instance.title_id  # 船舶计划名称的id
                form.instance.ship_id = ship_id
                form.instance.boat_status_id = title_num  # 船舶状态的id
                form.save()
                form.instance.ship.boat_status_id = title_num
                form.instance.ship.agent_id = user_id
                form.instance.ship.save()
                return redirect(reverse('stark:web_plan_agent_list', kwargs={'ship_id': ship_id}))
        return render(request, 'stark/change.html', {'form': form})

    list_display = [display_name, 'IMO', 'MMSI', 'nationality', 'crew_detail', 'goods', 'purpose',
                    'last_port', display_port, 'boat_status',
                    get_choice_text('是否在港', 'status'), display_plan, display_move, ]
    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """
        origin_list_url = self.reverse_list_url(*args, **kwargs)
        if request.method == 'GET':
            return render(request, self.delete_template or 'stark/delete.html', {'cancel': origin_list_url})
        obj = models.Ship.objects.filter(pk=pk, boat_status_id__in=[1,2]).first()
        # 船舶如果已经属于在港或者离港，就不能删除
        if obj:
            obj.update(display=2)
            return redirect(origin_list_url)
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)
    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """
        current_change_object = self.model_class.objects.filter(pk=pk).first()
        if not current_change_object:
            return HttpResponse('要修改的数据不存在，请重新选择！')
        obj = self.model_class.objects.filter(status__in=[1,2]).first()
        if obj:
            return HttpResponse('禁止修改！！！')

        model_form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class(instance=current_change_object)
            return render(request, self.change_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST, instance=current_change_object)
        if form.is_valid():
            response = self.save(form, request, is_update=True, *args, **kwargs)
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.change_template or 'stark/change.html', {'form': form})

    # 过滤没有被删除的船舶，后期加上代理公司的id进行过滤
    def get_query_set(self, request, *args, **kwargs):
        return self.model_class.objects.filter(display=1)