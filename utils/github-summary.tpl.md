# systems status report (Python {{ version }})

{% if systems %}
| overall success rate | {{ int((health.passed / health.total) * 100) }}% |
|-|-|
| passed | {{ health.passed }} |
| failed | {{ health.failed }} |
| total  | {{ health.total }} |

| | class    | instances | success rate |
|-|----------|-----------|--------------|
{% for system in systems %}
    {% for cls in system.classes %}
|{{format_outcome("passed" if cls.failed == 0)}}| [{{system.name}}.{{ cls.name }}](#user-content-cls-{{cls.name|lower}}-{{version}}) | {{ cls.total }} | {{ int((cls.passed / cls.total) * 100) }}% |
    {% endfor %}
{% endfor %}

---

{% for system in systems %}
    {% for cls in system.classes %}
## <a name="user-content-cls-{{cls.name|lower}}-{{version}}">{{system.name}}.{{ cls.name }}</a>

| | instance | outcome | duration | stations |
|-|----------|---------|----------|----------|
        {% for instance in cls.instances %}
|{{format_outcome(instance.report.outcome)}}|[{{system.name}}.{{cls.name}}::{{instance.tag}}](#user-content-tag-{{instance.tag|lower}}-{{version}})|{{instance.report.outcome}}|{{format_duration(instance.report.call.duration)}}|
{%- if instance.report.user_properties -%}
{{len(instance.report.user_properties[0].geojson.features)}}
{%- else -%}0{%- endif -%}|
        {% endfor %}

    {% endfor %}
{% endfor %}

---

{% for system in systems %}
    {% for cls in system.classes %}
        {% for instance in cls.instances %}
---
### <a name="user-content-tag-{{instance.tag|lower}}-{{version}}">{{system.name}}.{{cls.name}}::{{instance.tag}}</a>

```
{{ pformat(instance.instance) }}
```

            {% if instance.report.outcome == "failed" %}
#### Error Traceback

```
{{ instance.report.call.crash.message }}
```
            {% endif %}

        {% endfor %}
    {% endfor %}
{% endfor %}
{% else %}
No systems
{% endif %}
