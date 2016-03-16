#define BABEL_SWIFT_SOME_TYPE id

{% for className in classNames %}
@class {{ className }};
{% endfor %}

{% for variableName in variableNames %}
BABEL_SWIFT_SOME_TYPE {{ variableName }};
{% endfor %}
