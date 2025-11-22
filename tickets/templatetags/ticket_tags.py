from django import template
from django.utils.safestring import mark_safe

register = template.Library()

STATUS_CONFIG = {
    'open': {
        'icon': 'fa-check-circle',
        'color': '#0f5132',
        'bg': '#d1e7dd',
        'text': 'باز',
        'icon_color': 'text-success',
    },

    'in_progress': {
        'icon': 'fa-cogs',
        'color': '#0c63e4',
        'bg': '#cfe2ff',
        'text': 'در حال پیگیری',
        'icon_color': 'text-info',
    },
    'pending_close': {
        'icon': 'fa-clock',
        'color': '#d97706',
        'bg': '#ffe5b4',
        'text': 'در انتظار بستن',
        'icon_color': 'text-warning',
    },
    'closed': {
        'icon': 'fa-lock',
        'color': '#721c24',
        'bg': '#f8d7da',
        'text': 'بسته شده',
        'icon_color': 'text-danger',
    },
}


@register.simple_tag
def render_status_badge(status):
    config = STATUS_CONFIG.get(status)
    html = f"""
    <span class="badge rounded-pill px-3 py-2" style="background: {config['bg']}; color: {config['color']};">
        <i class="fas {config['icon']} me-1"></i>
        {config['text']}
    </span>
    """
    return mark_safe(html)


@register.simple_tag
def render_status_icon(status):
    config = STATUS_CONFIG.get(status)
    html = f"""
    <i class="fas {config['icon']} me-1 {config['icon_color']}"></i>
    """
    return mark_safe(html)


@register.simple_tag
def render_status_color(status):
    config = STATUS_CONFIG.get(status)
    return config['color']


@register.simple_tag
def render_status_bg(status):
    config = STATUS_CONFIG.get(status)
    return config['bg']


@register.simple_tag
def render_status_text(status):
    config = STATUS_CONFIG.get(status)
    return config['text']
