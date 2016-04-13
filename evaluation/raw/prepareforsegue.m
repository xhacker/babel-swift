// http://stackoverflow.com/questions/5210535/passing-data-between-view-controllers

-(void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender{
    if([segue.identifier isEqualToString:@"showDetailSegue"]){
        UINavigationController *navController = (UINavigationController *)segue.destinationViewController;
        ViewControllerB *controller = (ViewControllerB *)navController.topViewController;
        controller.isSomethingEnabled = YES;
    }
}
