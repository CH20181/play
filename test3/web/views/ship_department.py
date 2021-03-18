from django.urls import re_path

from stark.service.v1 import StarkHandler, get_datetime_text


# 各执勤队在港船舶预览

class ShipDepartmentHandler(StarkHandler):
    """
    代理公司视图
    """

    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '名称'
        return '%s   %s' % (obj.chinese_name, obj.english_name)

    has_add_btn = False

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    list_display = [display_name, 'nationality', 'crew_total', 'IMO', 'MMSI', 'purpose', 'last_port', 'port_in',
                    'boat_status', 'status', get_datetime_text('添加时间', 'create_time')]
