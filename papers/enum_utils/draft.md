---
title:    Enum utilities
document: DXXXX
date:     2025-12-10
audience: EWG, LEWG
author:
 - name:  Matthias Wippich
   email: <mfwippich@gmail.com>
toc: true
toc-depth: 2
---


# Abstract                                                                      {-}

This paper proposes several utilities for enumerations.


\newpage
# Revision history                                                              {-}
### R0 December 2025                                                            {-}

Original version of the paper.


\newpage
# Introduction                                                                  {#intro}

C++ 26 gives us reflection capabilities that can be used with enumerations. However, we currently lack several common queries shifting the burden onto users.

# Reusing `numeric_limits`
Key points: 

- enums are numeric types
- querying the numeric limits of an enum is meaningful
- numeric limits of underlying type might be different => UB
- knowing range is important for consteval

# New queries

- `is_fixed_enum_type` for numeric limits
- `in_enum` vs `in_range`

# Stringification

- `to_string`/`from_string`
- `format`
- `iostreams`

\newpage
# Wording                                                                       {#wording}

Make the following changes to the C++ Working Draft.  All wording is relative
to [@N5014], the latest draft at the time of writing.

### [limits.syn]{.sref} Header <limits> synopsis                        {-}

```
// all freestanding
namespace std {
  // [round.style], enumeration float_round_style
  enum float_round_style;

  // [numeric.limits], class template numeric_limits
  template<class T> class numeric_limits;

  template<class T> class numeric_limits<const T>;
  template<class T> class numeric_limits<volatile T>;
  template<class T> class numeric_limits<const volatile T>;

  template<> class numeric_limits<bool>;

  template<> class numeric_limits<char>;
  template<> class numeric_limits<signed char>;
  template<> class numeric_limits<unsigned char>;
  template<> class numeric_limits<char8_t>;
  template<> class numeric_limits<char16_t>;
  template<> class numeric_limits<char32_t>;
  template<> class numeric_limits<wchar_t>;

  template<> class numeric_limits<short>;
  template<> class numeric_limits<int>;
  template<> class numeric_limits<long>;
  template<> class numeric_limits<long long>;
  template<> class numeric_limits<unsigned short>;
  template<> class numeric_limits<unsigned int>;
  template<> class numeric_limits<unsigned long>;
  template<> class numeric_limits<unsigned long long>;

  template<> class numeric_limits<float>;
  template<> class numeric_limits<double>;
  template<> class numeric_limits<long double>;
```
:::add
```
  template <typename T>
    requires std::is_enum_v<T>
  class numeric_limits<T>;
``` 
:::
```
}
```

\newpage

### [numeric.special]{.sref} `numeric_limits` specializations                   {-}

::: add

[4]{.pnum}

The partial specialization for an enumeration type E matches the specialization for the underlying type of E, with the following exceptions:

```
static constexpr bool min() noexcept;
static constexpr bool max() noexcept;
```

[4.1]{.pnum}

If E is an unscoped enumeration without fixed underlying type, `min()` is the smallest and `max()` the largest value representable by the smallest bit-field large enough to hold all the values of E ([dcl.enum]{.sref}). 

Otherwise, `min()` and `max()` match `min()` and `max()` for the underlying type of E.


```
static constexpr bool digits = @_see-below_@;
static constexpr bool digits10 = digits * 3 / 10;
```

[4.2]{.pnum}

If E is an unscoped enumeration without fixed underlying type, `digits` is the width of the smallest bit-field large enough to hold all values of E ([dcl.enum]{.sref}). 

Otherwise, `digits` is `numeric_limits<underlying_type_t<E>>::digits`.
:::

\newpage

### [meta.syn]{.sref} Header `<meta>` synopsis                        {-}

```
  // associated with [meta.unary.prop], type properties
  ...
  consteval bool is_scoped_enum_type(info type);
```
:::add
```
  consteval bool is_fixed_enum_type(info type);
```
:::

### [meta.unary.prop]{.sref} Type properties                        {-}

Add to table [tab:meta.unary.prop]{.sref}:
```
template<class T>
struct is_fixed_enum;
```
_Condition_: T is an enumeration type with a fixed underlying value.
_Precondition_: T is an enumeration type.

\newpage

### [utility.syn]{.sref} Header `<utility>` synopsis                        {-}

TODO insert in_enum

### [utility.intcmp]{.sref} Integer comparison functions                        {-}

```
template<class R, class T>
  constexpr bool in_range(T t) noexcept;
```

[9]{.pnum}

_Mandates:_ [If T is an enumeration, R is T or convertible to the underlying type of T.]{.add}
[B]{.rm}[Otherwise, b]{.add}oth T and R are standard integer types or extended integer types([basic.fundamental]).

[10]{.pnum}

_Effects:_ Equivalent to: 
```
  return cmp_greater_equal(t, numeric_limits<R>::min()) &&
       cmp_less_equal(t, numeric_limits<R>::max());
```
TODO must cast to underlying type if T is enum

\newpage
# Acknowledgements                                                              {#ack}

Thanks to Michael Park for the pandoc-based framework used to transform this
document's source from Markdown.

Thanks to Peter Bindels for motivating this paper, Brian Bi for suggesting
reuse of `numeric_limits`, Peter Dimov and Will Wray for providing an implementation
of `has_fixed_underlying_type` and numerous other cool people for giving feedback.

---
references:
  - id: N5014
    citation-label: N5014
    author: Thomas Köppe
    title:  Working Draft, Programming Languages --- C++
    URL:    https://wg21.link/N5014

---
