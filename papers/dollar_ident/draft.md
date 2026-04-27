---
title:    $identifiers
document: Dxxxx
date:     2026-04-26
audience: EWG
author:
 - name:  Matthias Wippich
   email: <mfwippich@gmail.com>
toc: true
toc-depth: 2
---

\newpage
# Abstract                                                                      {-}

This paper proposes making `$` in identifiers conditionally-supported to align with C23.

# Revision history                                                              {-}
### R0 April 2026                                                               {-}
Original version of the paper.


\newpage
# Introduction                                                                  {#intro}

One of the most popular extensions to C++ is allowing `$` in identifiers. For example,
this is supported by MSVC (@MSVC), GCC (@GCC), Clang, EDG (might 
need opt-in), icx and nvc++ (see [Compiler Explorer](https://compiler-explorer.com/z/bxKEMx54o)).

In recent years, C has made quite a few changes to what they consider an identifier. The
original rules allowed any implementation-defined characters, the revised ones did not. To
address this, @N3145 introduced a carve-out to allow `$` anywhere in identifiers as an
implementation extension.

@N3145 mentions that during discussion it was noted that allowing `$` in identifiers 
is a massive syntactic land-grab. However, due to the popularity of this extension it 
seems unrealistic that we can ever use `$` for anything that would conflict with $identifiers.

# Why not allow it unconditionally?                                             {#allow}

GCC notes in its documentation

> However, dollar signs in identifiers are not supported on a few target machines, 
> typically because the target assembler does not allow them. 
(@GCC)

Examples for such targets are @RS6000 (because of the AIX assembler), @AVR and @MMIX.

In theory we could mandate `$` to be valid in identifiers and ask compilers to work
around such problematic assemblers in some way or another. However, the purpose of 
this paper is to align the standard with the implementation reality and C23.

# Motivation                                                                    {#motivation}

Aside from aligning with C, there are a few more motivating uses.

## Linker-defined symbols                                                       {#symbols}

Some linkers emit linker-defined symbols with dollars in their identifiers.

One such example is armlink from the ARM MDK toolchain:

> Symbols that contain the character sequence \$\$, and all other external 
> names containing the sequence \$\$, are names reserved by ARM.
(@ARMLINK)

Unfortunately the examples given in armlink's documentation are not valid C++.
<!--
extern int @Image$$ER_ZI$$Limit@; // oops, not a valid identifier
-->
<div class="sourceCode" id="cb1"><pre class="sourceCode cpp"><code class="sourceCode cpp"><span id="cb1-1"><a href="#cb1-1" aria-hidden="true" tabindex="-1"></a><span class="kw">extern</span> <span class="dt">int</span> Image$$ER_ZI$$Limit; <span class="co">// oops, not a valid identifier</span></span></code></pre></div>

With GCC and Clang this can also be addressed by explicitly specifying the name used in assembler code ([Compiler Explorer](https://compiler-explorer.com/z/WE8TzTsav))
<!--
extern int Image_ER_ZI_Limit asm("Image$$ER_ZI$$Limit");
-->
<div class="sourceCode" id="cb2"><pre class="sourceCode cpp"><code class="sourceCode cpp"><span id="cb2-1"><a href="#cb2-1" aria-hidden="true" tabindex="-1"></a><span class="kw">extern</span> <span class="dt">int</span> Image_ER_ZI_Limit <span class="kw">asm</span><span class="op">(</span><span class="st">"Image$$ER_ZI$$Limit"</span><span class="op">)</span>;</span></code></pre></div>

However, it seems much cleaner and less error-prone to avoid repetition and instead 
actually allow such implementations to support dollars in identifiers directly.

## Macros                                                                       {#macros}

Another somewhat common use is in macro identifiers. Github search finds more
than 5600 uses in code recognized as C++ (@GHSEARCH)

For example consider
<!--
```cpp
#if MSVC
#   define $inline_never  __declspec(noinline)
#   define $inline_always __forceinline
#else
#   define $inline_never  [[gnu::noinline]]
#   define $inline_always [[gnu::always_inline]] inline
#endif

#define $inline(_opt)     $inline_##_opt
#define $template         template for (auto _ : "")
#define $pi               3
#define $assert(...)                                                        \
    do {                                                                    \
        ((__VA_ARGS__) ? (void)0 : throw std::runtime_error(#__VA_ARGS__)); \
    } while (false)

$inline(always) int foo(int a) {
    $assert(a > 0);
    return a * $pi;
}

$inline(never) int bar(int, char) {
    $template {
        constexpr auto ctx = std::meta::current_function();
        static constexpr auto [... Idx] = std::make_index_sequence<parameters_of(ctx).size()>{};
        return (foo([:variable_of(parameters_of(ctx)[Idx]):]) + ... + 0);
    }
}
```
-->
<div class="sourceCode" id="cb1"><pre class="sourceCode cpp"><code class="sourceCode cpp"><span id="cb1-1"><a href="#cb1-1" aria-hidden="true" tabindex="-1"></a><span class="pp">#if MSVC</span></span>
<span id="cb1-2"><a href="#cb1-2" aria-hidden="true" tabindex="-1"></a><span class="pp">#   define $inline_never  </span><span class="ex">__declspec(noinline)</span></span>
<span id="cb1-3"><a href="#cb1-3" aria-hidden="true" tabindex="-1"></a><span class="pp">#   define $inline_always </span>__forceinline</span>
<span id="cb1-4"><a href="#cb1-4" aria-hidden="true" tabindex="-1"></a><span class="pp">#else</span></span>
<span id="cb1-5"><a href="#cb1-5" aria-hidden="true" tabindex="-1"></a><span class="pp">#   define $inline_never  </span><span class="op">[[</span><span class="ex">gnu::noinline</span><span class="op">]]</span></span>
<span id="cb1-6"><a href="#cb1-6" aria-hidden="true" tabindex="-1"></a><span class="pp">#   define $inline_always </span><span class="op">[[</span><span class="ex">gnu::always_inline</span><span class="op">]]</span><span class="pp"> </span><span class="kw">inline</span></span>
<span id="cb1-7"><a href="#cb1-7" aria-hidden="true" tabindex="-1"></a><span class="pp">#endif</span></span>
<span id="cb1-8"><a href="#cb1-8" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-9"><a href="#cb1-9" aria-hidden="true" tabindex="-1"></a><span class="pp">#define $inline(_opt)     $inline_##</span>_opt</span>
<span id="cb1-10"><a href="#cb1-10" aria-hidden="true" tabindex="-1"></a><span class="pp">#define $template         </span><span class="kw">template</span><span class="pp"> </span><span class="cf">for</span><span class="pp"> </span><span class="op">(</span><span class="kw">auto</span><span class="pp"> </span>_<span class="pp"> </span><span class="op">:</span><span class="pp"> </span><span class="st">&quot;&quot;</span><span class="op">)</span></span>
<span id="cb1-11"><a href="#cb1-11" aria-hidden="true" tabindex="-1"></a><span class="pp">#define $pi               </span><span class="dv">3</span></span>
<span id="cb1-12"><a href="#cb1-12" aria-hidden="true" tabindex="-1"></a><span class="pp">#define $assert</span><span class="op">(...)</span><span class="pp">                                                        </span>\</span>
<span id="cb1-13"><a href="#cb1-13" aria-hidden="true" tabindex="-1"></a><span class="pp">    </span><span class="cf">do</span><span class="pp"> </span><span class="op">{</span><span class="pp">                                                                    </span>\</span>
<span id="cb1-14"><a href="#cb1-14" aria-hidden="true" tabindex="-1"></a><span class="pp">        </span><span class="op">((</span><span class="ot">__VA_ARGS__</span><span class="op">)</span><span class="pp"> </span><span class="op">?</span><span class="pp"> </span><span class="op">(</span><span class="dt">void</span><span class="op">)</span><span class="dv">0</span><span class="pp"> </span><span class="op">:</span><span class="pp"> </span><span class="cf">throw</span><span class="pp"> </span>std<span class="op">::</span>runtime_error<span class="op">(</span><span class="pp">#</span><span class="ot">__VA_ARGS__</span><span class="op">))</span>;<span class="pp"> </span>\</span>
<span id="cb1-15"><a href="#cb1-15" aria-hidden="true" tabindex="-1"></a><span class="pp">    </span><span class="op">}</span><span class="pp"> </span><span class="cf">while</span><span class="pp"> </span><span class="op">(</span><span class="kw">false</span><span class="op">)</span></span>
<span id="cb1-16"><a href="#cb1-16" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-17"><a href="#cb1-17" aria-hidden="true" tabindex="-1"></a><span >$</span><span class="kw">inline</span><span class="op">(</span>always<span class="op">)</span> <span class="dt">int</span> foo<span class="op">(</span><span class="dt">int</span> a<span class="op">)</span> <span class="op">{</span></span>
<span id="cb1-18"><a href="#cb1-18" aria-hidden="true" tabindex="-1"></a>    <span >$</span>assert<span class="op">(</span>a <span class="op">&gt;</span> <span class="dv">0</span><span class="op">)</span>;</span>
<span id="cb1-19"><a href="#cb1-19" aria-hidden="true" tabindex="-1"></a>    <span class="cf">return</span> a <span class="op">*</span> <span >$</span>pi;</span>
<span id="cb1-20"><a href="#cb1-20" aria-hidden="true" tabindex="-1"></a><span class="op">}</span></span>
<span id="cb1-21"><a href="#cb1-21" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-22"><a href="#cb1-22" aria-hidden="true" tabindex="-1"></a><span >$</span><span class="kw">inline</span><span class="op">(</span>never<span class="op">)</span> <span class="dt">int</span> bar<span class="op">(</span><span class="dt">int</span>, <span class="dt">char</span><span class="op">)</span> <span class="op">{</span></span>
<span id="cb1-23"><a href="#cb1-23" aria-hidden="true" tabindex="-1"></a>    <span >$</span><span class="kw">template</span> <span class="op">{</span></span>
<span id="cb1-24"><a href="#cb1-24" aria-hidden="true" tabindex="-1"></a>        <span class="kw">constexpr</span> <span class="kw">auto</span> ctx <span class="op">=</span> std<span class="op">::</span>meta<span class="op">::</span>current_function<span class="op">()</span>;</span>
<span id="cb1-25"><a href="#cb1-25" aria-hidden="true" tabindex="-1"></a>        <span class="kw">static</span> <span class="kw">constexpr</span> <span class="kw">auto</span> <span class="op">[...</span> Idx<span class="op">]</span> <span class="op">=</span> std<span class="op">::</span>make_index_sequence<span class="op">&lt;</span>parameters_of<span class="op">(</span>ctx<span class="op">).</span>size<span class="op">()&gt;{}</span>;</span>
<span id="cb1-26"><a href="#cb1-26" aria-hidden="true" tabindex="-1"></a>        <span class="cf">return</span> <span class="op">(</span>foo<span class="op">([:</span>variable_of<span class="op">(</span>parameters_of<span class="op">(</span>ctx<span class="op">)[</span>Idx<span class="op">]):])</span> <span class="op">+</span> <span class="op">...</span> <span class="op">+</span> <span class="dv">0</span><span class="op">)</span>;</span>
<span id="cb1-27"><a href="#cb1-27" aria-hidden="true" tabindex="-1"></a>    <span class="op">}</span></span>
<span id="cb1-28"><a href="#cb1-28" aria-hidden="true" tabindex="-1"></a><span class="op">}</span></span></code></pre></div>


As noted earlier, using $ in any identifiers that survive until the assembler takes over
can be problematic with some targets. Since macros are long gone at this point,
using dollars in macros is relatively safe.

If used only for macros consistently, this has the benefit of making them 
visually stand out. Not only does this reduce chances of name collisions,
it also helps when surveying code - after all, macros come with sharp edges. 

\newpage
# Wording                                                                       {#wording}

Make the following changes to the C++ Working Draft.  All wording is relative
to [@N5032], the latest draft at the time of writing.

### [lex.name]{.sref} Identifiers                                     {-}
Add a new paragraph after [lex.name]{.sref}/1

|  _identifier_:
|       _identifier-start_
|       _identifier_ _identifier-continue_

|  _identifier-start_:
|       _nondigit_
|       an element of the translation character set with the Unicode property XID_Start

|  _identifier-continue_:
|       _digit_
|       _nondigit_
|       an element of the translation character set with the Unicode property XID_Continue

|  _nondigit_: one of
|       a b c d e f g h i j k l m
|       n o p q r s t u v w x y z
|       A B C D E F G H I J K L M
|       N O P Q R S T U V W X Y Z _

|  _digit_: one of
|       0 1 2 3 4 5 6 7 8 9 

::: note
The character properties XID_Start and XID_Continue are described by UAX #44 of the Unicode Standard.
:::

[1]{.pnum} The program is ill-formed if an _identifier_ does not conform to Normalization Form C as specified in the Unicode Standard.

::: note
Identifiers are case-sensitive.
:::

::: note
[uaxid]{.sref} compares the requirements of UAX #31 of the Unicode Standard with the C++ rules for identifiers.
:::

::: note
In translation phase 4, _identifier_ also includes those preprocessing-tokens ([lex.pptoken]{.sref}) differentiated as keywords ([lex.key]{.sref}) in the later translation phase 7 ([lex.token]{.sref}).
:::

::: add
[2]{.pnum} 
The inclusion of `$` in _nondigit_ is conditionally-supported.

::: note
Use of `$` anywhere in an identifier is allowed if the implementation supports it.
:::

:::


\newpage
# Acknowledgements                                                              {#ack}

Thanks to Michael Park for the pandoc-based framework used to transform this
document's source from Markdown.

---
references:
  - id: N5008
    citation-label: N5032
    author: Thomas Köppe
    title:  Working Draft, Programming Languages --- C++
    URL:    https://wg21.link/n5032
  - id: MSVC
    citation-label: MSVC documentation
    URL: https://learn.microsoft.com/en-us/cpp/cpp/identifiers-cpp?view=msvc-170#:~:text=The%20dollar%20sign%20%24%20is%20a%20valid%20identifier%20character%20in%20the%20Microsoft%20C%2B%2B%20compiler%20%28MSVC%29%2E
  - id: GCC
    citation-label: GCC documentation
    URL: https://gcc.gnu.org/onlinedocs/gcc/Dollar-Signs.html

  - id: ARMLINK
    citation-label: armlink documentation
    URL: https://developer.arm.com/documentation/dui0803/f/Accessing-and-Managing-Symbols-with-armlink/Linker-defined-symbols

  - id: RS6000
    citation-label: RS/6000
    URL: https://github.com/gcc-mirror/gcc/blob/master/gcc/config/rs6000/xcoff.h#L57

  - id: AVR
    citation-label: AVR
    URL: https://github.com/gcc-mirror/gcc/blob/master/gcc/config/avr/avr.h#L480

  - id: MMIX
    citation-label: MMIX
    URL: https://github.com/gcc-mirror/gcc/blob/master/gcc/config/mmix/mmix.h#L792

  - id: GHSEARCH
    citation-label: Github code search
    URL: https://github.com/search?q=%22%23define+%24%22+language%3AC%2B%2B+&type=code

  - id: N3145
    citation-label: WG14 N3145
    title: $ in Identifiers v2
    URL: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3145.pdf
---
