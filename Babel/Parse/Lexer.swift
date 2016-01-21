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
    let tokens: [CKToken]
    var tokenGenerator: IndexingGenerator<[CKToken]>

    init(source: String) {
        self.source = source
        
        let translationUnit = CKTranslationUnit(text: source, language: CKLanguageObjC, args: [])
        self.tokens = translationUnit.tokens as! [CKToken]
        self.tokenGenerator = self.tokens.generate()
    }
    
    func findNext() -> Token? {
        guard let ckToken = tokenGenerator.next() else {
            return nil
        }
        
        print(ckToken)
        
        return Token()
    }
    
}
