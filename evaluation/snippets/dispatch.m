// http://stackoverflow.com/questions/4139219/how-do-you-trigger-a-block-after-a-delay-like-performselectorwithobjectafter

CGFloat time1 = 3.49;
CGFloat time2 = 8.13;

// Delay 2 seconds
dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2.0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
    CGFloat newTime = time1 + time2;
    NSLog(@"New time: %f", newTime);
});
