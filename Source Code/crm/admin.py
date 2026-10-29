from django.contrib import admin
from .models import Customer, Product, Order, OrderItem, Payment, FollowUp, SalesTarget, JourneyEvent, AuditLog
# Business writes go through validated app workflows. Django admin is a read-only inspector.
class Inspector(admin.ModelAdmin):
    def has_module_permission(self,request): return request.user.is_superuser
    def has_view_permission(self,request,obj=None): return request.user.is_superuser
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
@admin.register(Customer)
class CustomerAdmin(Inspector):
    list_display=['name','company','stage','owner','updated_at']; list_filter=['stage','owner']; search_fields=['name','email','phone']
@admin.register(Order)
class OrderAdmin(Inspector):
    list_display=['id','customer','owner','status','order_date']; list_filter=['status','owner']; search_fields=['customer__name']
@admin.register(FollowUp)
class FollowUpAdmin(Inspector):
    list_display=['subject','customer','owner','status','due_at']; list_filter=['status','owner','priority']
@admin.register(AuditLog)
class AuditAdmin(Inspector):
    list_display=['created_at','actor','action','entity','object_id','label']; list_filter=['action','entity','actor']; search_fields=['label']
for model in [Product,OrderItem,Payment,SalesTarget,JourneyEvent]: admin.site.register(model,Inspector)
admin.site.site_header='Salesroom administration'
admin.site.site_title='Salesroom admin'
