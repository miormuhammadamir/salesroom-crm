from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Customer, Product, Order, OrderItem, FollowUp, Payment, SalesTarget

class ScopedForm(forms.ModelForm):
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if isinstance(field,forms.DateTimeField):
                field.widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type':'datetime-local'})
                field.input_formats=['%Y-%m-%dT%H:%M']
            elif isinstance(field,forms.DateField): field.widget=forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'})
        if 'owner' in self.fields:
            self.fields['owner'].queryset=get_user_model().objects.filter(is_active=True)
            if not user.is_staff: self.fields.pop('owner')
        if 'customer' in self.fields:
            self.fields['customer'].queryset=Customer.objects.all() if user.is_staff else Customer.objects.filter(owner=user)
        if 'order' in self.fields:
            self.fields['order'].queryset=Order.objects.exclude(status__in=['draft','cancelled']) if user.is_staff else Order.objects.filter(owner=user).exclude(status__in=['draft','cancelled'])
    def clean(self):
        data=super().clean()
        if data.get('customer') and data.get('owner') and data['customer'].owner_id!=data['owner'].pk:
            raise forms.ValidationError('Assign the customer to this owner first. Orders and follow-ups must have the same owner as their customer.')
        return data

class CustomerForm(ScopedForm):
    class Meta: model=Customer; fields=['name','company','email','phone','address','source','stage','owner','estimated_value','notes']
class ProductForm(ScopedForm):
    class Meta: model=Product; fields=['name','sku','price','active']
class OrderForm(ScopedForm):
    class Meta: model=Order; fields=['customer','owner','status','order_date','due_date','discount','tax_percent','notes']
class FollowUpForm(ScopedForm):
    class Meta: model=FollowUp; fields=['customer','owner','subject','kind','due_at','priority','status','notes']
class PaymentForm(ScopedForm):
    class Meta: model=Payment; fields=['order','amount','paid_on','method','reference']
class TargetForm(ScopedForm):
    class Meta: model=SalesTarget; fields=['user','month','amount']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['user'].queryset=get_user_model().objects.filter(is_active=True)

class ItemForm(forms.ModelForm):
    class Meta: model=OrderItem; fields=['product','description','quantity','unit_price']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['product'].queryset=Product.objects.filter(active=True) | Product.objects.filter(pk=self.instance.product_id)
class ItemSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return
        rows=[f.cleaned_data for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]
        if not rows: raise forms.ValidationError('Add at least one order item.')
Items=inlineformset_factory(Order,OrderItem,form=ItemForm,formset=ItemSet,extra=1,can_delete=True,max_num=100,validate_max=True,absolute_max=200)
