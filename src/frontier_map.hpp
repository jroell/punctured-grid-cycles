#pragma once
#include <functional>
#ifdef USE_BOOST_FLAT_MAP
#include <boost/unordered/unordered_flat_map.hpp>
template <class K, class V, class H = std::hash<K>>
using FrontierMap = boost::unordered_flat_map<K, V, H>;
#else
#include <unordered_map>
template <class K, class V, class H = std::hash<K>>
using FrontierMap = std::unordered_map<K, V, H>;
#endif
