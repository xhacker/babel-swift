//
//  Token.h
//  Babel
//
//  Created by Dongyuan Liu on 2016-01-21.
//  Copyright © 2016 Xhacker. All rights reserved.
//

#import <Foundation/Foundation.h>

typedef NS_ENUM(NSInteger, TokenKind) {

#define KEYWORD(X) kw_ ## X,
#define PUNCTUATOR(X, Y) X,
#include "Tokens.def"

};
