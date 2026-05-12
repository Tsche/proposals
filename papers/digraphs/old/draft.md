---
title:    Removing Digraphs
document: Dxxxx
date:     2025-05-12
audience: EWG, CWG
author:
 - name:  Matthias Wippich
   email: <mfwippich@gmail.com>
toc: true
toc-depth: 2
---


# Abstract                                                                      {-}

This paper proposes removal of digraphs from the C++ language.


\newpage
# Revision history                                                              {-}
### R0 May 2025                                                                 {-}

Original version of the paper.


\newpage
# Introduction                                                                  {#intro}

Digraphs are a complicated solution to a very old problem, that cause more problems
than they solve in a modern environment. Digraphs also severely limit the design space of C++,
although as we have seen with @P2996 we are already fine with special-casing our way out
of this pickle.

This however introduces an interesting problem:
If you need to use a source encoding that requires use of digraphs, you **cannot use all of C++26** 
directly.

Since we are most likely going to continue seeing similar problems, this paper proposes to remove digraphs from the language entirely.

# Design Space {#design}
As mentioned before, digraphs severely limit the design space of C++. This isn't an entirely 
new insight, in fact we've ran into issues because of digraphs already and will most likely
continue to run into new issues because of digraphs.

This leads to a fragmented language - some parts you can write if you need to use digraphs, 
some you don't. At the same time we're accumulating workarounds (like @CWG1104), which lead 
to an excessively complex language.

## Splicers                                                                      {#splicers}
Splicers from @P2996 were accepted for C++26 with the proposed syntax `[: expr :]`. However,
we are not allowed to use digraphs to spell this as `<:: expr ::>`.

While that seems to be in direct contradiction of the guarantees we're given in [[lex.digraph]/2](https://eel.is/c++draft/lex.digraph#2):
> In all respects of the language, each alternative token behaves the same, respectively, as its primary token, except for its spelling.

it actually isn't. The tokens `[:` and `:]` are distinct preprocessing tokens rather than being 
composed from `[` and `:` (or `:` and `]` respectively). Therefore it doesn't matter whether `<:` is a valid
alternative spelling for `[` - the splicer syntax does not contain `[` tokens.

Unfortunately that doesn't exactly help if your source encoding does not have angle brackets. In such
cases you cannot use this language feature directly - you'd have to find some workaround (such as 
inventing some arbitrary replacement sequence that is expanded to `[:` after transcoding).

## Interpolated string literals {#fstrings}
The design problems stemming from digraphs do not end there. In some of the recent discussions
around string interpolation (@P3412, @P3951) some interesting code was brought up. Consider the following:
```cpp
t"foo { bar %> baz"
```

In an interpolated string literal, the interpolated expression field is wrapped in curly braces. To parse
an interpolated string literal you must therefore switch between regular string literal parsing and expression parsing as soon
as you see a field introducer (`{`). 

However, once you parse the interpolated expression things get a little strange. `%>` is an alternative spelling of `}`. We haven't yet
returned back to literal parsing, so this would yield the correct token. So, should we be able to signify the end of the interpolation field with `%>`?

Since allowing anything but literal `}` to terminate a interpolation field seems extremely surprising and will most likely not match user expectations, we
are noce again looking to disallow digraphs in this context.

Unfortunately that also means that we are once again looking to introduce a feature that you cannot directly use 
if your source encoding requires the use of the corresponding digraphs.

# Compatibility {#compatibility}
In C++14 we removed support for trigraphs. Since this has been quite a while back now, it is fair
to assume that mitigations for users that required use of trigraphs but wanted to target anything
beyond C++11 are in place. 

While the situation around digraphs is arguably different and might require extra preprocessing to work
with source encodings that do not have angle brackets or curly braces, mitigations will likely look
similar to the ones required for trigraphs.


\newpage
# Wording                                                                       {#wording}

Make the following changes to the C++ Working Draft.  All wording is relative
to [@N5008], the latest draft at the time of writing.

### [lex.pptoken]{.sref} Preprocessing tokens {-}
Modify paragraph 5 as indicated

[5]{.pnum}
If the input stream has been parsed into preprocessing tokens up to a given character:

[5.1]{.pnum}
    If the next character begins a sequence of characters that could be the prefix and initial double quote of a raw string literal, such as `R"`, the next preprocessing token shall be a raw string literal.
    Between the initial and final double quote characters of the raw string, any transformations performed in phase 2 (line splicing) are reverted; this reversion is applied before any _d-char_, _r-char_, or delimiting parenthesis is identified.
    The raw string literal is defined as the shortest sequence of characters that matches the raw-string pattern

> |    _encoding-prefix~opt~_ R _raw-string_

::: rm
[5.2]{.pnum}
    Otherwise, if the next three characters are `<​::`​ and the subsequent character is neither `:` nor `>`, the `<` is treated as a preprocessing token by itself and not as the first character of the alternative token `<:`.
:::
[5.3]{.pnum}
    Otherwise, if the next three characters are `[​::​` and the subsequent character is not `:`[, or if the next three characters are `[:>`,]{.rm} the `[` is treated as a preprocessing token by itself and not as the first character of the preprocessing token `[:`.

::: rm
::: note
    The tokens [: and :] cannot be composed from digraphs.
:::
:::
[5.4]{.pnum}
    Otherwise, the next preprocessing token is the longest sequence of [...]


### [lex.operators]{.sref} Operators and punctuators {-}
Modify as indicated.

> [1]{.pnum} 
> The lexical representation of C++ programs includes a number of preprocessing tokens that are used in the syntax of the preprocessor or are converted into tokens for operators and punctuators:
> 
> |  preprocessing-op-or-punc:
> |      preprocessing-operator
> |      operator-or-punctuator
> |  preprocessing-operator: one of

| `#` | `##` | [`%:`]{.rm} | [`%:%:`]{.rm} |

> |  operator-or-punctuator: one of        

--------     -------      --------     ---------    ---------  -------   ------    ----   -----
`{`          `}`          `[`          `]`          `(`        `)`       `[:`      `:]`        
[`<%`]{.rm}  [`%>`]{.rm}  [`<:`]{.rm}  [`:>`]{.rm}  `;`        `:`       `...`                 
`?`          `::`         `.`          `.*`         `->`       `->*`     `^^`      `~`         
`!`          `+`          `-`          `*`          `/`        `%`       `^`       `&`    `|`  
`=`          `+=`         `-=`         `*=`         `/=`       `%=`      `^=`      `&=`   `|=` 
`==`         `!=`         `<`          `>`          `<=`       `>=`      `<=>`     `&&`   `||` 
`<<`         `>>`         `<<=`        `>>=`        `++`       `--`      `,`                   
`and`        `or`         `xor`        `not`        `bitand`   `bitor`   `compl`               
`and_eq`     `or_eq`      `xor_eq`     `not_eq`                                                
--------     -------      --------     ---------    ---------  -------   ------    ----   -----

> |
> | Each _operator-or-punctuator_ is converted to a single token in translation phase 6 ([lex.phases]{.sref}).

### [lex.digraph]{.sref} Alternative tokens                                     {-}
Rename to `lex.alt`.

Replace Table 3

::: add
| Alternative  | Primary | Alternative | Primary |
|--------------|---------|-------------|---------|
| `and`        | `&&`    | `and_eq`    | `&=`    |
| `bitor`      | `|`     | `or_eq`     | `|=`    |
| `or`         | `||`    | `xor_eq`    | `^=`    |
| `xor`        |  `^`    | `not`       | `!`     |
| `compl`      | `~`     | `not_eq`    | `!=`    |
| `bitand`     | `&`     |             |         |
:::

::: draftnote
This removes the first column

::: rm
| Alternative | Primary |
|-------------|---------|
|`<%`         | `{`     |
|`%>`         | `}`     |
|`<:`         | `[`     |
|`:>`         | `]`     |
|`%:`         | `#`     |
|`%:%:`       | `##`    |
:::
:::

Remove footnote 10

::: rm

> These include “digraphs” and additional reserved words.
> The term “digraph” (token consisting of two characters) is not perfectly descriptive, since one of the alternative preprocessing-tokens is %:%: and of course several primary tokens contain two characters.
> Nonetheless, those alternative tokens that aren't lexical keywords are colloquially known as “digraphs”.
:::


\newpage
# Acknowledgements                                                              {#ack}

Thanks to Michael Park for the pandoc-based framework used to transform this
document's source from Markdown.

---
references:
  - id: N5008
    citation-label: N5008
    author: Thomas Köppe
    title:  Working Draft, Programming Languages --- C++
    URL:    https://wg21.link/n5008

  - id: P2996
    citation-label: P2996
    author: Wyatt Childers, Peter Dimov, Dan Katz, Barry Revzin, Andrew Sutton, Faisal Vali, Daveed Vandevoorde
    title: "Reflection for C++26"
    URL: https://wg21.link/p2996

---
