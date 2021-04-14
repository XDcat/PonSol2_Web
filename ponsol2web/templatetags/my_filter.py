from django import template
import textwrap

register = template.Library()


@register.filter
def shorten_str(txt, max_len=20):
    wrapper = textwrap.TextWrapper(width=max_len, placeholder=" ...", max_lines=2)
    res = " ".join(wrapper.wrap(txt))
    return res