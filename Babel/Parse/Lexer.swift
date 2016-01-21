//
//  Lexer.swift
//  Babel
//
//  Created by Dongyuan Liu on 2016-01-20.
//  Copyright © 2016 Xhacker. All rights reserved.
//

import Foundation

class Lexer {
    
    let source: String

    init(source: String) {
        self.source = source
    }
    
    func findNext() -> Token? {
        guard let ch = nextMeaningfulCharacter() else {
            return nil
        }
        
        print(ch)
        
        return Token()
    }
    
}
