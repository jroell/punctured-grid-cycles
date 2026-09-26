#include "count256.hpp"
#include <chrono>
#include <cstdio>
#include <stdexcept>
#include <sys/resource.h>
#include <unordered_map>

using Key = unsigned __int128;
struct Hash {
  size_t operator()(Key x) const {
    return uint64_t(x) ^ (uint64_t(x >> 64) * 0x9e3779b97f4a7c15ULL);
  }
};
using Map = std::unordered_map<Key, Count256, Hash>;

int main(int argc, char **argv) {
  int n;
  bool quarter;
  try {
    if (argc != 3)
      throw std::invalid_argument("arguments");
    std::string s = argv[1];
    size_t used;
    n = std::stoi(s, &used);
    if (used != s.size() || n < 2 || n > 8)
      throw std::invalid_argument("n");
    s = argv[2];
    if (s != "half" && s != "quarter")
      throw std::invalid_argument("mode");
    quarter = s == "quarter";
  } catch (...) {
    fprintf(stderr,
            "Usage: %s N half|quarter; 2 <= N <= 8, full board "
            "side = 2N\n",
            argv[0]);
    return 2;
  }
  const int h = n, w = quarter ? n : 2 * n, slots = quarter ? 2 * w : w + 1;
  bool board[16][16] = {};
  for (int i = 0; i < h; i++)
    for (int j = 0; j < w; j++)
      board[i][j] =
          !(i == h - 1 && (quarter ? j == w - 1 : (j == n - 1 || j == n)));
  auto encode = [&](const int *m) {
    Key s = 0;
    for (int k = 0; k < slots; k++)
      s |= Key(m[k] + 1) << (5 * k);
    return s;
  };
  auto decode = [&](Key s, int *m) {
    for (int k = 0; k < slots; k++)
      m[k] = int((s >> (5 * k)) & 31) - 1;
  };
  Map current, next;
  current[0] = Count256(1);
  size_t peak = 1;
  auto start = std::chrono::steady_clock::now();
  for (int i = 0; i < h; i++) {
    for (int j = 0; j < w; j++) {
      next.clear();
      next.reserve(current.size() * 1.3 + 100);
      int p = j, q = j + 1;
      bool down = i + 1 == h || board[i + 1][j];
      bool right = j + 1 < w ? board[i][j + 1] : quarter && i < h - 1;
      for (const auto &entry : current) {
        int m[32];
        decode(entry.first, m);
        int a = m[p], b = m[q];
        auto add = [&]() { next[encode(m)] += entry.second; };
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
        } else if (a != q) {
          m[p] = m[q] = -1;
          m[a] = b;
          m[b] = a;
          add();
        }
      }
      current.swap(next);
      peak = std::max(peak, current.size());
      if (peak > 3000000) {
        fprintf(stderr, "State limit exceeded: %zu\n", peak);
        return 3;
      }
      if (std::chrono::duration<double>(std::chrono::steady_clock::now() -
                                        start)
              .count() > 240) {
        fprintf(stderr, "Time limit exceeded: 240 seconds\n");
        return 3;
      }
    }
    next.clear();
    next.reserve(current.size() + 100);
    for (const auto &entry : current) {
      int m[32], out[32], permutation[32];
      decode(entry.first, m);
      for (int k = 0; k < slots; k++) {
        out[k] = -1;
        permutation[k] = k;
      }
      for (int k = 0; k < w; k++)
        permutation[k] = k + 1;
      if (m[w] >= 0) {
        if (!quarter || i == h - 1)
          abort();
        permutation[w] = w + 1 + i;
      }
      for (int k = 0; k < slots; k++)
        if (m[k] >= 0)
          out[permutation[k]] = permutation[m[k]];
      next[encode(out)] += entry.second;
    }
    current.swap(next);
    fprintf(stderr, "row %d: %zu states\n", i + 1, current.size());
  }
  Count256 rotation, reflection;
  for (const auto &entry : current) {
    int m[32];
    decode(entry.first, m);
    int active = 0, first = -1, bottom = 0;
    for (int k = 0; k < slots; k++)
      if (m[k] >= 0) {
        active++;
        first = k;
        if (k >= 1 && k <= w)
          bottom++;
      }
    if (active == 2 && (!quarter || bottom == 1))
      reflection += entry.second;
    if (active == 0 || (active / 2) % 2 == 0)
      continue;
    auto seam = [&](int k) {
      return quarter ? (k <= w ? w + k : k - w) : w + 1 - k;
    };
    bool valid = true;
    for (int k = 0; k < slots; k++)
      if (m[k] >= 0) {
        int v = seam(k);
        if (v < 0 || v >= slots || m[v] < 0) {
          valid = false;
          break;
        }
      }
    if (!valid)
      continue;
    bool seen[32] = {};
    int stack[64], top = 0, visited = 0;
    stack[top++] = first;
    while (top) {
      int k = stack[--top];
      if (seen[k])
        continue;
      seen[k] = true;
      visited++;
      if (!seen[m[k]])
        stack[top++] = m[k];
      if (!seen[seam(k)])
        stack[top++] = seam(k);
    }
    if (visited == active)
      rotation += entry.second;
  }
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  double rss = ru.ru_maxrss /
#ifdef __APPLE__
               1048576.0;
#else
               1024.0;
#endif
  printf("{\"n\":%d,\"mode\":\"%s\",\"rotation\":\"%s\",\"reflection\":\"%s\","
         "\"peak_states\":%zu,\"seconds\":%.6f,\"max_rss_mib\":%.3f}\n",
         n, quarter ? "quarter" : "half", rotation.str().c_str(),
         reflection.str().c_str(), peak,
         std::chrono::duration<double>(std::chrono::steady_clock::now() - start)
             .count(),
         rss);
}
