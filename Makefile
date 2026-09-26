CXX = clang++
CXXFLAGS = -O3 -std=c++17 -Wall -Wextra

all: build/parentheses build/partners build/symmetry

build:
	mkdir -p build

build/%: src/%.cpp src/count256.hpp | build
	$(CXX) $(CXXFLAGS) $< -o $@

benchmark: all
	python3 scripts/benchmark.py
	python3 scripts/symmetry_benchmark.py

clean:
	rm -f build/parentheses build/partners build/symmetry

test: all
	python3 scripts/verify.py

.PHONY: all benchmark test clean
