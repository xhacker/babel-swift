// http://stackoverflow.com/questions/24062509/location-services-not-working-in-ios-8

locationManager = [[CLLocationManager alloc] init];
locationManager.delegate = self;
locationManager.distanceFilter = kCLDistanceFilterNone; //whenever we move
locationManager.desiredAccuracy = kCLLocationAccuracyBest;

[locationManager startUpdatingLocation];
[locationManager requestWhenInUseAuthorization]; // Add This Line
