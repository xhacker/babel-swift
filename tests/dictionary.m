NSDictionary *productInfo = @{
                              kPADCurrentPrice: @"19.99",
                              kPADDevName: @"Regular SIA",
                              kPADCurrency: @"USD",
                              kPADImage: @"http://inboardapp.com/images/inboard_icon.png",
                              kPADProductName: @"Inboard",
                              kPADTrialDuration: @"14",
                              kPADTrialText: @"Thanks for downloading Inboard trial!",
                              kPADProductImage: @"Icon",
                             };

[[Paddle sharedInstance] startLicensing:productInfo timeTrial:YES withWindow:self.mainWindowController.window];

[self.updateMenuItem setHidden:NO];
