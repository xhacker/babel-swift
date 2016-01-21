//
//  AppDelegate.swift
//  Babel
//
//  Created by Dongyuan Liu on 2015-09-01.
//  Copyright © 2015 Xhacker. All rights reserved.
//

import Cocoa

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    func applicationDidFinishLaunching(aNotification: NSNotification) {
        let source = "NSPopover* popover = self.calendarPopover;"
        let lexer = Lexer(source: source)
        while let t = lexer.findNext() {
            print(t)
        }
    }

    func applicationWillTerminate(aNotification: NSNotification) {
        // Insert code here to tear down your application
    }

}

