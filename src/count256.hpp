#pragma once
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
struct Count256 {
  uint64_t a[4] = {};
  Count256(uint64_t x = 0) { a[0] = x; }
  Count256 &operator+=(const Count256 &b) {
    unsigned __int128 c = 0;
    for (int i = 0; i < 4; i++) {
      c += (unsigned __int128)a[i] + b.a[i];
      a[i] = (uint64_t)c;
      c >>= 64;
    }
    if (c) {
      fprintf(stderr, "Count256 overflow: addition exceeds 2^256 - 1\n");
      abort();
    }
    return *this;
  }
  std::string str() const {
    Count256 t = *this;
    std::string s;
    while (t.a[0] || t.a[1] || t.a[2] || t.a[3]) {
      unsigned __int128 r = 0;
      for (int i = 3; i >= 0; i--) {
        r = (r << 64) | t.a[i];
        t.a[i] = (uint64_t)(r / 10);
        r %= 10;
      }
      s += char('0' + r);
    }
    if (s.empty())
      s = "0";
    std::reverse(s.begin(), s.end());
    return s;
  }
};
