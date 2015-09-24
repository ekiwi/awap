#ifndef ITERATOR_UTILS_HPP
#define ITERATOR_UTILS_HPP

template<typename T>
static inline size_t countIterator(T begin, T end) {
	size_t count = 0;
	while(begin != end) {
		++count;
		++begin;
	}
	return count;
}

template<typename T>
static inline size_t countIterator(T queryResult) {
	return countIterator(queryResult.begin(), queryResult.end());
}

#endif // ITERATOR_UTILS_HPP
