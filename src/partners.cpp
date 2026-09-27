#include "count256.hpp"
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include "frontier_map.hpp"
// Occupied slots store their partner index plus one; zero means empty.
using Key = unsigned __int128;
struct Hash {
  size_t operator()(Key x) const {
    return (uint64_t)x ^ ((uint64_t)(x >> 64) * 0x9e3779b97f4a7c15ULL);
  }
};
using Map = FrontierMap<Key, Count256, Hash>;
int main(int argc, char **argv) {
  int h = 16, w = 16;
  bool hole = true;
  try {
    if (argc > 4)
      throw std::invalid_argument("args");
    auto parse = [](const char *p) {
      size_t used;
      std::string s = p;
      int v = std::stoi(s, &used);
      if (used != s.size())
        throw std::invalid_argument("integer");
      return v;
    };
    if (argc > 1)
      h = parse(argv[1]);
    w = argc > 2 ? parse(argv[2]) : h;
    int v = argc > 3 ? parse(argv[3]) : 1;
    if (v != 0 && v != 1)
      throw std::invalid_argument("hole");
    hole = v;
    if (h < 1 || h > 24 || w < 1 || w > 24 || (hole && (h % 2 || w % 2)))
      throw std::invalid_argument("dimensions");
  } catch (...) {
    fprintf(stderr,
            "Usage: %s HEIGHT WIDTH HOLE; dimensions 1..24; HOLE 0 or 1; "
            "punctured dimensions even\n",
            argv[0]);
    return 2;
  }
  size_t peak = 1;
  int peakrow = 0, peakcol = 0;
  bool board[32][32] = {};
  int last = -1;
  for (int i = 0; i < h; i++)
    for (int j = 0; j < w; j++) {
      board[i][j] = !(hole && (i == h / 2 - 1 || i == h / 2) &&
                      (j == w / 2 - 1 || j == w / 2));
      if (board[i][j])
        last = i * w + j;
    }
  Map cur, nxt;
  cur[0] = Count256(1);
  Count256 answer;
  auto start = std::chrono::steady_clock::now();
  auto encode = [&](const int *m) {
    Key k = 0;
    for (int z = 0; z <= w; z++)
      k |= Key(m[z] + 1) << (5 * z);
    return k;
  };
  for (int i = 0; i < h; i++) {
    for (int j = 0; j < w; j++) {
      nxt.clear();
      nxt.reserve(cur.size() * 1.3 + 100);
      int p = j, q = j + 1;
      bool down = i + 1 < h && board[i + 1][j],
           right = j + 1 < w && board[i][j + 1];
      for (const auto &kv : cur) {
        int m[32];
        for (int z = 0; z <= w; z++)
          m[z] = int((kv.first >> (5 * z)) & 31) - 1;
        int a = m[p], b = m[q];
        auto add = [&]() { nxt[encode(m)] += kv.second; };
        if (!board[i][j]) {
          if (a < 0 && b < 0)
            add();
          continue;
        }
        if (a < 0 && b < 0) {
          if (down && right) {
            m[p] = q;
            m[q] = p;
            add();
          }
        } else if (a < 0 || b < 0) {
          int partner = a >= 0 ? a : b;
          m[p] = m[q] = -1;
          if (down) {
            m[p] = partner;
            m[partner] = p;
            add();
            m[p] = -1;
          }
          if (right) {
            m[q] = partner;
            m[partner] = q;
            add();
          }
        } else {
          m[p] = m[q] = -1;
          if (a == q) {
            if (i * w + j == last && encode(m) == 0)
              answer += kv.second;
          } else {
            m[a] = b;
            m[b] = a;
            add();
          }
        }
      }
      cur.swap(nxt);
      if (cur.size() > peak) {
        peak = cur.size();
        peakrow = i + 1;
        peakcol = j + 1;
      }
    }
    nxt.clear();
    nxt.reserve(cur.size() + 100);
    for (const auto &kv : cur) {
      int m[32];
      m[0] = -1;
      for (int z = 0; z < w; z++) {
        int a = int((kv.first >> (5 * z)) & 31) - 1;
        m[z + 1] = a < 0 ? -1 : a + 1;
      }
      nxt[encode(m)] += kv.second;
    }
    cur.swap(nxt);
    fprintf(
        stderr, "row %d: %zu states, %.2fs\n", i + 1, cur.size(),
        std::chrono::duration<double>(std::chrono::steady_clock::now() - start)
            .count());
  }
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  double rss_mib = ru.ru_maxrss /
#ifdef __APPLE__
                   1048576.0;
#else
                   1024.0;
#endif
  printf("{\"height\":%d,\"width\":%d,\"hole\":%s,\"count\":\"%s\",\"peak_"
         "states\":%zu,\"peak_row\":%d,\"peak_col\":%d,\"seconds\":%.6f,\"max_"
         "rss_mib\":%.3f}\n",
         h, w, hole ? "true" : "false", answer.str().c_str(), peak, peakrow,
         peakcol,
         std::chrono::duration<double>(std::chrono::steady_clock::now() - start)
             .count(),
         rss_mib);
}
