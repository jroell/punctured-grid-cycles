#include "count256.hpp"
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include <unordered_map>
// Each slot is 0 (empty), 1 (opening endpoint), or 2 (closing endpoint).
using Map = std::unordered_map<uint64_t, Count256>;
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
    if (h < 1 || h > 16 || w < 1 || w > 16 || (hole && (h % 2 || w % 2)))
      throw std::invalid_argument("dimensions");
  } catch (...) {
    fprintf(stderr,
            "Usage: %s HEIGHT WIDTH HOLE; dimensions 1..16; HOLE 0 or 1; "
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
  for (int i = 0; i < h; i++) {
    for (int j = 0; j < w; j++) {
      nxt.clear();
      nxt.reserve(cur.size() * 1.3 + 100);
      int p = j, q = j + 1;
      bool down = i + 1 < h && board[i + 1][j],
           right = j + 1 < w && board[i][j + 1];
      for (const auto &kv : cur) {
        uint64_t s = kv.first;
        const Count256 &n = kv.second;
        int a = (s >> (2 * p)) & 3, b = (s >> (2 * q)) & 3;
        uint64_t t = s & ~((3ULL << (2 * p)) | (3ULL << (2 * q)));
        auto add = [&](uint64_t u) { nxt[u] += n; };
        if (!board[i][j]) {
          if (!a && !b)
            add(s);
          continue;
        }
        if (!a && !b) {
          if (down && right)
            add(t | (1ULL << (2 * p)) | (2ULL << (2 * q)));
        } else if (!a || !b) {
          int c = a ? a : b;
          if (down)
            add(t | ((uint64_t)c << (2 * p)));
          if (right)
            add(t | ((uint64_t)c << (2 * q)));
        } else if (a == 1 && b == 2) {
          // Closing a component early would leave a disconnected cycle.
          if (i * w + j == last && t == 0)
            answer += n;
        } else if (a == 2 && b == 1)
          add(t);
        else if (a == 1 && b == 1) {
          int depth = 1;
          for (int k = q + 1; k <= w; k++) {
            int c = (s >> (2 * k)) & 3;
            if (c == 1)
              depth++;
            if (c == 2)
              depth--;
            if (depth == 0) {
              add(t ^ (3ULL << (2 * k)));
              break;
            }
          }
        } else if (a == 2 && b == 2) {
          int depth = 1;
          for (int k = p - 1; k >= 0; k--) {
            int c = (s >> (2 * k)) & 3;
            if (c == 2)
              depth++;
            if (c == 1)
              depth--;
            if (depth == 0) {
              add(t ^ (3ULL << (2 * k)));
              break;
            }
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
      if (kv.first >> (2 * w))
        abort();
      nxt[kv.first << 2] += kv.second;
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
