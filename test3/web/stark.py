from stark.service.v1 import site
from web import models
from web.views.user_info import UserInfoHandler
from web.views.company import CompanyHandler
from web.views.department import DepartmentHandler
from web.views.location import LocationHandler
from web.views.ship_agent import ShipAgentHandler
from web.views.planstatus import PlanStatusHandler
from web.views.boatstatus import BoatStatusHandler
from web.views.plan_agent import PlanAgentHandler

site.register(models.UserInfo, UserInfoHandler)
site.register(models.Company, CompanyHandler)
site.register(models.Department, DepartmentHandler)
site.register(models.Location, LocationHandler)
site.register(models.Ship, ShipAgentHandler, prev='agent')
site.register(models.Plan, PlanAgentHandler, prev='agent')
site.register(models.PlanStatus, PlanStatusHandler)
site.register(models.BoatStatus, BoatStatusHandler)
