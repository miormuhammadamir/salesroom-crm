from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import load_workbook
from .models import Customer, Order, OrderItem, Payment, Product, FollowUp, AuditLog, JourneyEvent, SalesTarget

class CRMTests(TestCase):
    def setUp(self):
        U=get_user_model()
        self.manager=U.objects.create_user('manager',password='Testing-safe-123!',is_staff=True)
        self.a=U.objects.create_user('alice',password='Testing-safe-123!')
        self.b=U.objects.create_user('bob',password='Testing-safe-123!')
        self.customer=Customer.objects.create(name='Alice Customer',owner=self.a)
        self.other=Customer.objects.create(name='Bob Customer',owner=self.b)
        self.product=Product.objects.create(name='Service',sku='SVC',price=100)
        self.order=Order.objects.create(customer=self.customer,owner=self.a,status='confirmed')
        OrderItem.objects.create(order=self.order,description='Service',quantity=2,unit_price=100)
        self.client.force_login(self.a)
    def url(self,name,*args): return reverse(name,args=args)
    def customer_data(self,**extra):
        self.customer.refresh_from_db()
        return dict(name='Updated Alice',company='',email='',phone='',address='',source='',stage='qualified',estimated_value='500',notes='',revision=self.customer.updated_at.isoformat(),**extra)
    def item_data(self):
        return {'items-TOTAL_FORMS':'1','items-INITIAL_FORMS':'0','items-MIN_NUM_FORMS':'0','items-MAX_NUM_FORMS':'100','items-0-description':'Package','items-0-quantity':'2','items-0-unit_price':'100','items-0-product':''}
    def order_data(self,**extra):
        data={'customer':self.customer.pk,'status':'confirmed','order_date':timezone.localdate().isoformat(),'due_date':'','discount':'10','tax_percent':'6','notes':''}; data.update(self.item_data());data.update(extra);return data
    def test_login_required(self):
        self.client.logout()
        for path in ['/', '/customers/','/orders/export/csv/','/operations/']:
            self.assertEqual(self.client.get(path).status_code,302)
    def test_all_staff_screens_render(self):
        self.client.force_login(self.manager)
        for path in ['/','/operations/','/customers/','/orders/','/followups/','/products/','/payments/','/targets/','/customers/new/','/orders/new/','/followups/new/','/products/new/','/payments/new/','/targets/new/',f'/customers/{self.customer.pk}/',f'/orders/{self.order.pk}/',f'/orders/{self.order.pk}/edit/',f'/customers/{self.customer.pk}/edit/',f'/products/{self.product.pk}/delete/','/accounts/password/']:
            with self.subTest(path=path): self.assertEqual(self.client.get(path).status_code,200)
    def test_own_list_excludes_other_customer(self):
        response=self.client.get('/customers/'); self.assertContains(response,'Alice Customer');self.assertNotContains(response,'Bob Customer')
    def test_other_customer_hidden(self):
        for suffix in ['', 'edit/','delete/']:
            self.assertEqual(self.client.get(f'/customers/{self.other.pk}/{suffix}').status_code,404)
    def test_other_order_and_payment_hidden(self):
        order=Order.objects.create(customer=self.other,owner=self.b,status='confirmed')
        OrderItem.objects.create(order=order,description='Other',quantity=1,unit_price=100)
        payment=Payment.objects.create(order=order,amount=20)
        self.assertEqual(self.client.get(f'/orders/{order.pk}/').status_code,404)
        self.assertEqual(self.client.get(f'/payments/{payment.pk}/edit/').status_code,404)
    def test_sales_cannot_access_management(self):
        for path in ['/operations/','/targets/','/targets/export/csv/','/products/new/',f'/products/{self.product.pk}/edit/',f'/products/{self.product.pk}/delete/']:
            self.assertEqual(self.client.get(path).status_code,403)
    def test_customer_create_sets_owner_and_history(self):
        data=self.customer_data();data.pop('revision');data['owner']=self.b.pk
        response=self.client.post('/customers/new/',data)
        self.assertEqual(response.status_code,302)
        c=Customer.objects.get(name='Updated Alice');self.assertEqual(c.owner,self.a);self.assertEqual(c.journey.count(),1)
    def test_stage_change_records_journey(self):
        self.client.post(f'/customers/{self.customer.pk}/edit/',self.customer_data())
        self.assertTrue(JourneyEvent.objects.filter(customer=self.customer,to_stage='qualified',actor=self.a).exists())
    def test_stale_edit_rejected(self):
        data=self.customer_data();data['revision']='old'
        response=self.client.post(f'/customers/{self.customer.pk}/edit/',data)
        self.assertContains(response,'This record changed'); self.customer.refresh_from_db();self.assertEqual(self.customer.name,'Alice Customer')
    def test_reassignment_moves_related_records(self):
        f=FollowUp.objects.create(customer=self.customer,owner=self.a,subject='Call',due_at=timezone.now())
        self.client.force_login(self.manager)
        self.client.post(f'/customers/{self.customer.pk}/edit/',self.customer_data(owner=self.b.pk))
        self.order.refresh_from_db();f.refresh_from_db();self.assertEqual(self.order.owner,self.b);self.assertEqual(f.owner,self.b)
    def test_order_calculation(self):
        response=self.client.post('/orders/new/',self.order_data());self.assertEqual(response.status_code,302)
        o=Order.objects.latest('id');self.assertEqual(o.subtotal,200);self.assertEqual(o.total,Decimal('201.40'))
    def test_order_cross_customer_rejected(self):
        response=self.client.post('/orders/new/',self.order_data(customer=self.other.pk))
        self.assertEqual(response.status_code,200);self.assertEqual(Order.objects.count(),1)
    def test_discount_cannot_exceed_subtotal(self):
        self.assertContains(self.client.post('/orders/new/',self.order_data(discount='201')),'Discount cannot exceed');self.assertEqual(Order.objects.count(),1)
    def test_empty_items_rejected(self):
        data=self.order_data();data.update({'items-TOTAL_FORMS':'0'})
        self.assertContains(self.client.post('/orders/new/',data),'at least one order item');self.assertEqual(Order.objects.count(),1)
    def test_negative_quantity_rejected(self):
        self.client.post('/orders/new/',self.order_data(**{'items-0-quantity':'-1'}));self.assertEqual(Order.objects.count(),1)
    def test_invalid_due_date_rejected(self):
        data=self.order_data(due_date=(timezone.localdate()-timedelta(days=1)).isoformat())
        self.assertContains(self.client.post('/orders/new/',data),'Due date cannot precede');self.assertEqual(Order.objects.count(),1)
    def test_product_price_is_snapshot(self):
        self.product.price=999;self.product.save();self.assertEqual(self.order.total,200)
    def test_payment_and_balance(self):
        response=self.client.post('/payments/new/',{'order':self.order.pk,'amount':'50','paid_on':timezone.localdate(),'method':'cash'})
        self.assertEqual(response.status_code,302);self.assertEqual(self.order.balance,150);self.assertEqual(self.order.payment_status,'Partial')
    def test_overpayment_rejected(self):
        response=self.client.post('/payments/new/',{'order':self.order.pk,'amount':'201','paid_on':timezone.localdate(),'method':'cash'})
        self.assertContains(response,'exceed the order balance');self.assertEqual(Payment.objects.count(),0)
    def test_payment_on_draft_rejected(self):
        self.order.status='draft';self.order.save()
        self.client.post('/payments/new/',{'order':self.order.pk,'amount':'50','paid_on':timezone.localdate(),'method':'cash'})
        self.assertFalse(Payment.objects.exists())
    def test_payment_update_excludes_current_payment(self):
        p=Payment.objects.create(order=self.order,amount=100)
        response=self.client.post(f'/payments/{p.pk}/edit/',{'order':self.order.pk,'amount':'200','paid_on':timezone.localdate(),'method':'cash'})
        self.assertEqual(response.status_code,302);self.assertEqual(self.order.balance,0)
    def test_paid_order_cannot_cancel(self):
        Payment.objects.create(order=self.order,amount=100)
        data=self.order_data(status='cancelled',revision=self.order.updated_at.isoformat());data.update({'items-INITIAL_FORMS':'1','items-0-id':self.order.items.first().pk})
        self.assertContains(self.client.post(f'/orders/{self.order.pk}/edit/',data),'Remove payments')
        self.order.refresh_from_db();self.assertEqual(self.order.status,'confirmed')
    def test_total_cannot_drop_below_paid(self):
        Payment.objects.create(order=self.order,amount=200)
        data=self.order_data(revision=self.order.updated_at.isoformat());data.update({'items-INITIAL_FORMS':'1','items-0-id':self.order.items.first().pk,'items-0-unit_price':'10'})
        self.assertContains(self.client.post(f'/orders/{self.order.pk}/edit/',data),'less than recorded payments');self.assertEqual(self.order.total,200)
    def test_followup_completion_stamp(self):
        data={'customer':self.customer.pk,'subject':'Call customer','kind':'call','due_at':timezone.localtime().strftime('%Y-%m-%dT%H:%M'),'priority':'normal','status':'done','notes':'Discussed quote'}
        self.assertEqual(self.client.post('/followups/new/',data).status_code,302)
        f=FollowUp.objects.get();self.assertIsNotNone(f.completed_at);self.assertEqual(f.owner,self.a)
        data['status']='open';self.client.post(f'/followups/{f.pk}/edit/',data);f.refresh_from_db();self.assertIsNone(f.completed_at)
    def test_protected_customer_delete(self):
        response=self.client.post(f'/customers/{self.customer.pk}/delete/')
        self.assertEqual(response.status_code,200);self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists());self.assertFalse(AuditLog.objects.filter(action='delete').exists())
    def test_delete_requires_post(self):
        self.client.get(f'/customers/{self.other.pk}/delete/')
        self.assertTrue(Customer.objects.filter(pk=self.other.pk).exists())
    def test_unlinked_customer_delete(self):
        c=Customer.objects.create(name='Unused',owner=self.a)
        self.assertEqual(self.client.post(f'/customers/{c.pk}/delete/').status_code,302)
        self.assertFalse(Customer.objects.filter(pk=c.pk).exists());self.assertTrue(AuditLog.objects.filter(action='delete',object_id=c.pk).exists())
    def test_export_csv_scope_and_formula_escape(self):
        self.customer.name='=1+1';self.customer.save()
        response=self.client.get('/customers/export/csv/');text=response.content.decode('utf-8-sig')
        self.assertIn("'=1+1",text);self.assertNotIn('Bob Customer',text)
    def test_excel_export_and_filters(self):
        for kind in ['customers','orders','payments','products','followups']:
            response=self.client.get(f'/{kind}/export/xlsx/');self.assertEqual(response.status_code,200)
            wb=load_workbook(BytesIO(response.content));self.assertEqual(wb.active.freeze_panes,'A2')
        response=self.client.get('/customers/export/csv/?q=missing');self.assertNotIn('Alice Customer',response.content.decode())
    def test_manager_target_export(self):
        self.client.force_login(self.manager)
        for fmt in ['csv','xlsx']: self.assertEqual(self.client.get(f'/targets/export/{fmt}/').status_code,200)
    def test_dashboard_excludes_draft_and_cancelled(self):
        for status in ['draft','cancelled']:
            o=Order.objects.create(customer=self.customer,owner=self.a,status=status)
            OrderItem.objects.create(order=o,description='Ignored',quantity=1,unit_price=900)
        self.assertEqual(self.client.get('/').context['revenue'],200)
    def test_bad_dates_return_400(self):
        self.assertEqual(self.client.get('/?start=bad').status_code,400)
        self.assertEqual(self.client.get('/customers/?start=bad').status_code,400)
        self.assertEqual(self.client.get('/orders/export/csv/?start=bad').status_code,400)
    def test_csrf_protected(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.a)
        self.assertEqual(client.post('/customers/new/',self.customer_data()).status_code,403)
    def test_target_first_day_and_unique(self):
        self.client.force_login(self.manager)
        first=timezone.localdate().replace(day=1)
        data={'user':self.a.pk,'month':first.isoformat(),'amount':'1000'}
        self.assertEqual(self.client.post('/targets/new/',data).status_code,302)
        self.assertEqual(self.client.post('/targets/new/',data).status_code,200)
        data['month']=(first+timedelta(days=1)).isoformat()
        self.assertContains(self.client.post('/targets/new/',data),'first day');self.assertEqual(SalesTarget.objects.count(),1)
    def test_invalid_kind_is_404(self):
        self.assertEqual(self.client.get('/unknown/').status_code,404)
    def test_demo_refuses_nonempty_database(self):
        with self.assertRaises(CommandError): call_command('seed_demo')
        self.assertEqual(Customer.objects.count(),2)
