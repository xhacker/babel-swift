float pi = 3.14;
double e = 2.71828;
NSNumber *num = @42;

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


PFInstallation *currentInstallation = [PFInstallation currentInstallation];
[currentInstallation setDeviceTokenFromData:deviceToken];
currentInstallation.channels = @[ @"global" ];
[currentInstallation saveInBackground];
