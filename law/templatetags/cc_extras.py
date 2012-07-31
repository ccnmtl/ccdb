from django import template

register = template.Library()


class ChargeAreaNode(template.Node):
    def __init__(self, charge, area):
        self.charge = template.Variable(charge)
        self.area = template.Variable(area)

    def render(self, context):
        area = self.area.resolve(context)
        charge = self.charge.resolve(context)
        areas = charge.all_consequences_by_area()
        # extract the correct one
        matched = [a for a in areas if a['area'].id == area.id]
        # swap it into the template context
        context['area'] = matched[0]
        return ""


def do_charge_area(parser, token):
    try:
        tag_name, charge, area = token.split_contents()
    except ValueError:
        raise (template.TemplateSyntaxError,
               "%r tag requires two arguments" % token.contents.split()[0])
    return ChargeAreaNode(charge, area)


register.tag('charge_area', do_charge_area)
