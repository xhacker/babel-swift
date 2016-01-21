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
    var indexingGenerator: IndexingGenerator<String.CharacterView>

    init(source: String) {
        self.source = source
        self.indexingGenerator = source.characters.generate()
    }
    
    func findNext() -> Token? {
        guard let ch = nextMeaningfulCharacter() else {
            return nil
        }
        
        print(ch)
        
        return Token()
    }
    
    private func nextMeaningfulCharacter() -> Character? {
        guard let ch = indexingGenerator.next() else {
            return nil
        }
        
        if ch.isWhiteSpace() {
            return nextMeaningfulCharacter()
        }
        
        return ch
    }
    
}


extension Character {
    
    func isWhiteSpace() -> Bool {
        return isInCharacterSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())
    }
    
    func isDigit() -> Bool {
        return isInCharacterSet(NSCharacterSet.decimalDigitCharacterSet())
    }
    
    func isAlpha() -> Bool {
        return isInCharacterSet(NSCharacterSet.letterCharacterSet())
    }
    
    func isPunctuatorStart() -> Bool {
        return self == "*" || self == "." || self == ";" || self == "=";
    }
    
    private func isInCharacterSet(characterSet: NSCharacterSet) -> Bool {
        let s = String(self)
        let unicode = String(self).unicodeScalars[s.unicodeScalars.startIndex]
        return characterSet.longCharacterIsMember(unicode.value)
    }
}
