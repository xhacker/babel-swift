// http://stackoverflow.com/questions/1126726/how-to-make-a-uitextfield-move-up-when-keyboard-is-present

scrollView.frame = CGRectMake(scrollView.frame.origin.x, 
                     scrollView.frame.origin.y, 
scrollView.frame.size.width,
scrollView.frame.size.height - 215 + 50);   //resize
