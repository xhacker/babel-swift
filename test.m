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

if (!(obj == obj2)) {
    [obj doSomething];
}

int a = 2;


PFInstallation *currentInstallation = [PFInstallation currentInstallation];
[currentInstallation setDeviceTokenFromData:deviceToken];
currentInstallation.channels = @[@"global", @"app", @42];
[currentInstallation saveInBackground];


self.some.dict = @{
    @"key": @"value",
    @"anotherKey": @[@1, @2, @3]
};


if (self.some.property) {
    self.yesOrNo = NO;
}
else if (YES) {
    self.yesOrNo = YES;
}
else {
    self.some.integer = 42;
}


for (int i = 0; i < count; ++i) {
    int b = 3;
}


while (YES) {
    NSLog(@"Oh %@ %@", a, b);
}
