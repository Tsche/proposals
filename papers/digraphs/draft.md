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
than they solve in a modern environment. Digraphs severely limit the design space of C++,
although as we have seen with @P2996 we are already fine with special-casing our way out
of this pickle.

This however introduces an interesting problem:
If you need to use a source encoding that requires use of digraphs, you **cannot use all of C++26**.

We therefore propose to remove digraphs from the language entirely.

# History
EBCDIC, trigraphs

# Code survey

Naturally we want to avoid breaking code. This raises an important question: Is there 
code out there, encoded in a way that _needs_ use of digraphs **and** targeting a relatively
modern C++ dialect?

Thanks to GitHub Code search it is possible to find all open-source C++ code matching
a specific pattern. So, here's some data:

- unfiltered
- filtered comment/string pass
- mixed usage
- has trigraphs?
- usage guarded by macro?

# Splicers                                                                      {#splicers}
Splicers from @P2996 currently have the proposed syntax `[: expr :]`. The alternate digraph
representation `<:` of `[` (and similarly `:>` for `]`) cannot be used for splicers.

This choice was made because `::` in front of an identifier already has meaning in C++,
therefore allowing `<::foo` instead of `[:foo` would require significant lookahead 
to disambiguate from a comparison with `::foo`.

\newpage
# Wording                                                                       {#wording}

Make the following changes to the C++ Working Draft.  All wording is relative
to [@N5008], the latest draft at the time of writing.

### [lex.digraph]{.sref} Alternative tokens                                     {-}
Rename to `lex.alt`.

Replace Table 3
::: add
Alternative | Primary | Alternative | Primary
---------------------------------------------
`and` | `&&` | `and_eq` | `&=`
`bitor` | `|` | `or_eq` | `|=`
`or` | `||` | `xor_eq` | `^=`
`xor` |  `^` | `not` | `!`
`compl` | `~` | `not_eq` | `!=`
`bitand` | `&`
:::

This removes the first column
::: remove
Alternative | Primary
---------------------
`<%` | `{`
`%>` | `}`
`<:` | `[`
`:>` | `]`
`%:` | `#`
`%:%:` | `##`
:::


\newpage
# Acknowledgements                                                              {#ack}


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
