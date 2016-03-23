#define BABEL_SWIFT_SOME_TYPE id

{% for key, cls in classes.iteritems()  %}
@class {{ cls.name }};
{% endfor %}

{% for key, cls in classes.iteritems()  %}
@interface {{ cls.name }} : NSObject
{% for property in cls.properties %}
@property {{ property.ocClass.name }} *{{ property.identifier }};
{% endfor %}
@end

{% endfor %}

{% for variableName in variableNames %}
BABEL_SWIFT_SOME_TYPE {{ variableName }};
{% endfor %}
