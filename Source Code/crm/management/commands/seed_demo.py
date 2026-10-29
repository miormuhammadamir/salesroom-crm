import random
from datetime import date, timedelta, datetime, time
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from crm.models import Customer, Product, Order, OrderItem, Payment, FollowUp, SalesTarget, JourneyEvent
class Command(BaseCommand):
    help='Add fictional demo records to an empty CRM. Creates demo users with unusable passwords; use changepassword to enable logins.'
    @transaction.atomic
    def handle(self,*args,**options):
        if Customer.objects.exists() or Product.objects.exists() or Order.objects.exists():
            raise CommandError('Demo seeding requires an empty CRM database. No records were changed.')
        rng=random.Random(8); today=timezone.localdate(); User=get_user_model()
        users=[]
        for username,first,last in [('demo_aina','Aina','Rahman'),('demo_daniel','Daniel','Tan'),('demo_sara','Sara','Lim')]:
            if User.objects.filter(username=username).exists(): raise CommandError(f'{username} already exists. No records were changed.')
            u=User(username=username,first_name=first,last_name=last); u.set_unusable_password(); u.save(); users.append(u)
        products=[Product.objects.create(name=n,sku=sku,price=price) for n,sku,price in [('Starter package','PKG-01','249.00'),('Growth package','PKG-02','699.00'),('Consultation','SVC-01','150.00'),('Premium package','PKG-03','1299.00')]]
        names=[('Nadia Abdullah','Bloom Studio'),('Adam Hassan','Kopi Collective'),('Mei Ling','The Little Shop'),('Arif Zain','Zain Trading'),('Sofia Amir','Sofia Creative'),('Jason Lee','Northpoint Co.'),('Hana Ismail','Hana Living'),('Farah Noor','Noor & Co.'),('Ravi Kumar','Kumar Ventures'),('Amira Yusuf','Amira Studio'),('Grace Wong','Grace Retail'),('Danish Hakim','Hakim Group'),('Lina Aziz','Lina Lifestyle'),('Ben Lim','Lim Services'),('Nur Atiqah','Atiqah Works'),('Irfan Ali','Irfan Enterprise'),('Eva Tan','Eva Design'),('Siti Maryam','Maryam House')]
        customers=[]
        for i,(name,company) in enumerate(names):
            owner=users[i%3]; stage=Customer.STAGES[i%7][0]
            c=Customer.objects.create(name=name,company=company,email=f'customer{i+1}@example.com',phone=f'010-000-{i+1:04d}',owner=owner,source=['Website','Referral','Social media'][i%3],stage=stage,estimated_value=Decimal(rng.randrange(500,5000)),notes='Fictional demonstration customer.')
            JourneyEvent.objects.create(customer=c,to_stage='lead',actor=owner,note='Initial enquiry received')
            if stage!='lead': JourneyEvent.objects.create(customer=c,from_stage='lead',to_stage=stage,actor=owner,note='Demo relationship progress')
            customers.append(c)
            FollowUp.objects.create(customer=c,owner=owner,subject=['Discuss the proposal','Check in after consultation','Confirm package details','Arrange a discovery call'][i%4],kind=['call','whatsapp','email','meeting'][i%4],due_at=timezone.make_aware(datetime.combine(today+timedelta(days=i%9-3),time(10+i%6,30))),status='done' if i%5==0 else 'open',completed_at=timezone.now() if i%5==0 else None,priority='high' if i%4==0 else 'normal',notes='Demo task. Update with conversation notes after following up.')
        for offset in range(6):
            n=today.year*12+today.month-1-offset; year,month=divmod(n,12)
            for j in range(5+5-offset):
                c=rng.choice(customers); product=rng.choice(products)
                day=min(today.day,1+j*2) if offset==0 else 1+j*2
                o=Order.objects.create(customer=c,owner=c.owner,order_date=date(year,month+1,day),status=rng.choice(['confirmed','processing','completed']),tax_percent=6)
                OrderItem.objects.create(order=o,product=product,description=product.name,quantity=rng.randrange(1,4),unit_price=product.price)
                if j%3!=0: Payment.objects.create(order=o,amount=o.total if j%2 else (o.total/2).quantize(Decimal('.01')),paid_on=o.order_date,method='transfer',reference=f'DEMO-{o.pk}')
        for u in users: SalesTarget.objects.create(user=u,month=today.replace(day=1),amount=12000)
        self.stdout.write(self.style.SUCCESS('Fictional demo records created. Demo users have no usable password. Create your admin with createsuperuser.'))
