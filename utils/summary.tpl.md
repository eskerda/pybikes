# systems status report (Python {{ version }})

| overall success rate | {{ int((health.passed / health.total) * 100) }}% |
|-|-|
| passed | {{ health.passed }} |
| failed | {{ health.failed }} |
| total  | {{ health.total }} |

| | class    | instances | success rate |
|-|----------|-----------|--------------|
{% for system in systems %}
    {% for cls in system.classes %}
|{{format_outcome("passed" if cls.failed == 0)}}| [{{system.name}}.{{ cls.name }}](#cls-{{ cls.name }}-{{ version }}) | {{ cls.total }} | {{ int((cls.passed / cls.total) * 100) }}% |
    {% endfor %}
{% endfor %}

---

{% for system in systems %}
    {% for cls in system.classes %}
## <a name="user-content-cls-{{cls.name}}-{{version}}">{{system.name}}.{{ cls.name }}</a>

| | instance | outcome | duration |
|-|----------|---------|----------|
        {% for instance in cls.instances %}
|{{format_outcome(instance.report.outcome)}}|[{{system.name}}.{{cls.name}}::{{instance.tag}}](#tag-{{instance.tag}}-{{version}})|{{instance.report.outcome}}|{{format_duration(instance.report.call.duration)}}|
        {% endfor %}

    {% endfor %}
{% endfor %}
