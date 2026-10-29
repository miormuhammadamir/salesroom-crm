from django import template
register=template.Library()
@register.filter
def money(value):
    try: return f'{value:,.2f}'
    except (ValueError,TypeError): return '0.00'
@register.filter
def percent(value,total):
    return round(value/total*100,1) if total else 0
