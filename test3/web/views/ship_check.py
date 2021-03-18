from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_choice_text, get_datetime_text, StarkModelForm
from web import models


############## 指挥中心审核船情

class CheckPlanModelForm(StarkModelForm):
    class Meta:
        model = models.Plan
        exclude = ['boat_status', 'check_user']
        widgets = {
            'move_time': DateTimePickerInput,
        }


class ShipCheckHandler(StarkHandler):
    model_form_class = CheckPlanModelForm
    order_list = ['-id', 'boat_status']

    def action_multi_confirm(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            plan_obj = models.Plan.objects.filter(pk=pk, boat_status__lt=6).first()
            if not plan_obj:
                continue
            plan_obj.boat_status_id = 7
            plan_obj.save()
            plan_obj.ship.boat_status_id = 7
            plan_obj.ship.save()

    action_multi_confirm.text = '批量通过'

    def action_multi_cancel(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            plan_obj = models.Plan.objects.filter(pk=pk, boat_status__lt=6).first()
            if not plan_obj:
                continue
            plan_obj.boat_status_id = 8
            plan_obj.save()
            plan_obj.ship.boat_status_id = 8
            plan_obj.ship.save()

    action_multi_cancel.text = '批量取消'
    action_list = [action_multi_confirm, action_multi_cancel]

    def save(self, form, request, is_update, *args, **kwargs):
        user_id = 1
        plan_choice = form.instance.title_id
        if not is_update:
            form.instance.boat_status = plan_choice
            form.instance.check_user_id = user_id
            form.save()
        form.save()


    def display_location(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '申请停靠地点'
        location = obj.location
        if not location:  # 如果没有值得话，说明是出港、出境情况
            return obj.next_port

        return '%s--%s' % (obj.location, obj.next_port)

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '申请人'
        return '%s:%s' % (obj.agent.company, obj.agent)

    def display_imo(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return 'IMO'
        return obj.ship.IMO

    list_display = [StarkHandler.display_checkbox, 'ship', display_imo, 'title',
                    get_datetime_text('计划时间', 'move_time', time_format='%m-%d %H:%M'), display_location,
                    'boat_status', display_agent]
