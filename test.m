#import "AppKit/AppKit.h"

@class MyCustomClass;

@interface BABEL_SWIFT_WRAPPER_CLASS : NSObject
@end

@implementation BABEL_SWIFT_WRAPPER_CLASS

- (id)BABEL_SWIFT_WRAPPER_METHOD {
    int someVar = 42;
    float pi = 3.14;
    double e = 2.71828;

    if (someVar == 42) {
        NSPopover *popover = [[NSPopover alloc] init];
        [popover run];
    }

    int b = (int) pi;
    MyCustomClass *obj = [[MyCustomClass alloc] init];
    MyCustomClass *obj2 = obj;

    if (obj == obj2) {
        [obj doSomething];
    }

    int a = 2;
}

@end
