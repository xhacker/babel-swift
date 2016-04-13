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

{% for varDecl in varDeclarations %}
{{ varDecl.ocClass.name }} *{{ varDecl.identifier }};
{% endfor %}
