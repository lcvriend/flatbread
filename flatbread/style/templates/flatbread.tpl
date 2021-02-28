{% extends "html.tpl" %}
{% block table_styles %}
{% for s in flatbread_styles %}
#flatbread_{{uuid}} {{s.selector}} {
{% for p,val in s.props %}
  {{p}}: {{val}};
{% endfor %}
}
{% endfor %}
{{ super() }}
{% endblock table_styles %}
{% block table %}
<div id="flatbread_{{uuid}}" class="flatbread">
{% block table_title %}
{% if table_title %}<h3>{{table_title}}</h3>{% endif %}
{% endblock table_title %}
{{ super() }}
</div>
{% endblock table %}
{% block after_table %}{% endblock after_table %}
