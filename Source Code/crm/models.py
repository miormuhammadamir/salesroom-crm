from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

class Customer(models.Model):
    STAGES = [('lead','New lead'),('contacted','Contacted'),('qualified','Qualified'),('proposal','Proposal'),('negotiation','Negotiation'),('client','Client'),('lost','Lost')]
    name = models.CharField(max_length=160)
    company = models.CharField(max_length=160,blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40,blank=True)
    address = models.TextField(blank=True)
    source = models.CharField(max_length=80,blank=True)
    stage = models.CharField(max_length=20,choices=STAGES,default='lead',db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='customers')
    estimated_value = models.DecimalField(max_digits=12,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at']
        constraints = [models.CheckConstraint(condition=Q(estimated_value__gte=0),name='customer_value_nonnegative')]
    def __str__(self): return self.name

class JourneyEvent(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='journey')
    from_stage = models.CharField(max_length=20,blank=True)
    to_stage = models.CharField(max_length=20,choices=Customer.STAGES)
    note = models.CharField(max_length=250,blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']

class Product(models.Model):
    name = models.CharField(max_length=160)
    sku = models.CharField(max_length=40,unique=True)
    price = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    class Meta:
        ordering=['name']
        constraints=[models.CheckConstraint(condition=Q(price__gte=0),name='product_price_nonnegative')]
    def __str__(self): return f'{self.name} ({self.sku})'

class Order(models.Model):
    STATUSES=[('draft','Draft'),('confirmed','Confirmed'),('processing','Processing'),('completed','Completed'),('cancelled','Cancelled')]
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,related_name='orders')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders')
    status = models.CharField(max_length=20,choices=STATUSES,default='draft',db_index=True)
    order_date = models.DateField(default=timezone.localdate,db_index=True)
    due_date = models.DateField(null=True,blank=True)
    discount = models.DecimalField(max_digits=12,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    tax_percent = models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-order_date','-id']
        constraints=[models.CheckConstraint(condition=Q(discount__gte=0),name='discount_nonnegative'),models.CheckConstraint(condition=Q(tax_percent__gte=0,tax_percent__lte=100),name='tax_valid')]
    def __str__(self): return f'SO-{self.pk:05d}' if self.pk else 'New order'
    @property
    def subtotal(self): return sum((i.total for i in self.items.all()),Decimal('0.00'))
    @property
    def total(self): return ((self.subtotal-self.discount)*(1+Decimal(self.tax_percent)/100)).quantize(Decimal('.01'))
    @property
    def paid(self): return sum((p.amount for p in self.payments.all()),Decimal('0.00'))
    @property
    def balance(self): return self.total-self.paid
    @property
    def payment_status(self): return 'Paid' if self.balance<=0 else ('Partial' if self.paid else 'Unpaid')
    def clean(self):
        if self.due_date and self.due_date<self.order_date: raise ValidationError({'due_date':'Due date cannot precede order date.'})
        if self.tax_percent>100: raise ValidationError({'tax_percent':'Tax must be between 0 and 100.'})

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.PROTECT,null=True,blank=True)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(quantity__gte=1),name='item_quantity_positive'),models.CheckConstraint(condition=Q(unit_price__gte=0),name='item_price_nonnegative')]
    @property
    def total(self): return self.quantity*self.unit_price

class Payment(models.Model):
    order = models.ForeignKey(Order,on_delete=models.PROTECT,related_name='payments')
    amount = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal('.01'))])
    paid_on = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20,choices=[('transfer','Bank transfer'),('cash','Cash'),('card','Card'),('other','Other')],default='transfer')
    reference = models.CharField(max_length=100,blank=True)
    class Meta:
        ordering=['-paid_on','-id']
        constraints=[models.CheckConstraint(condition=Q(amount__gt=0),name='payment_positive')]
    def __str__(self): return f'{self.order} · RM {self.amount}'

class FollowUp(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='followups')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='followups')
    subject = models.CharField(max_length=200)
    kind = models.CharField(max_length=20,choices=[('call','Call'),('whatsapp','WhatsApp'),('email','Email'),('meeting','Meeting'),('task','Task')],default='call')
    due_at = models.DateTimeField(db_index=True)
    priority = models.CharField(max_length=10,choices=[('low','Low'),('normal','Normal'),('high','High')],default='normal')
    status = models.CharField(max_length=15,choices=[('open','Open'),('done','Done'),('cancelled','Cancelled')],default='open',db_index=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True,blank=True,editable=False)
    class Meta: ordering=['due_at']
    def __str__(self): return self.subject
    @property
    def overdue(self): return self.status=='open' and self.due_at<timezone.now()

class SalesTarget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    month = models.DateField(help_text='First day of the month.')
    amount = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal('.01'))])
    class Meta:
        ordering=['-month','user__username']
        constraints=[models.UniqueConstraint(fields=['user','month'],name='unique_monthly_target'),models.CheckConstraint(condition=Q(amount__gt=0),name='target_positive')]
    def clean(self):
        if self.month and self.month.day!=1: raise ValidationError({'month':'Use the first day of the month.'})
    def __str__(self): return f'{self.user} · {self.month:%b %Y}'

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    action = models.CharField(max_length=30)
    entity = models.CharField(max_length=50)
    object_id = models.PositiveBigIntegerField()
    label = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    class Meta: ordering=['-created_at']
