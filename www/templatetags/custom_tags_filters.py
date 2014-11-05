from django import template
register = template.Library()

@register.filter(name='addcss')
def add_css(field, css):
   return field.as_widget(attrs={"class":css})