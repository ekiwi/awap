#include "database_test.hpp"
#include <database.hpp>


struct IntegerQuery {
	int key;
	IntegerQuery(int key) : key(key) {}
	bool match(int& other) { return other == key; }
};

void
DatabaseTest::testInsert()
{
	using DB = Database<int, IntegerQuery, 10>

	DB db;
	TEST_ASSERT_EQUALS(db.count(), 0u);
	TEST_ASSERT_TRUE(db.insert(2));
	TEST_ASSERT_EQUALS(db.count(), 1u);

	// test inser with initializer list
	TEST_ASSERT_TRUE(db.insert(3,5,7,11,13));
	TEST_ASSERT_EQUALS(db.count(), 6u);
	TEST_ASSERT_TRUE(db.insert(17,19,23,29));
	TEST_ASSERT_EQUALS(db.count(), 10u);

	// check that db rejects results if full
	TEST_ASSERT_FALSE(db.insert(37));
	TEST_ASSERT_EQUALS(db.count(), 10u);

	// test insert through constructor
	DB db2(0,1,2,3);
	TEST_ASSERT_EQUALS(db2.count(), 4u);
}

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

void
DatabaseTest::testFind()
{
	using DB = Database<int, IntegerQuery, 100>;

	DB db(2,3,5,7,5,19,11,2,13,19,17,7,2);
	TEST_ASSERT_EQUALS(db.count(), 10u);

	// find single elements
	for(int value : { 3, 11, 13, 17 }) {
		TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(value))), 1u);
		TEST_ASSERT_EQUALS(*(db.find(IntegerQuery(value)).begin()), value);
	}

	// find elements that appear twice
	for(int value : { 5, 7, 19 }) {
		TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(value))), 2u);
		auto res = db.find(IntegerQuery(value));
		for(auto res_value : res) {
			TEST_ASSERT_EQUALS(*res_value, value);
		}
	}

	// 2 appears three times
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(2))), 3u);
	auto res = db.find(IntegerQuery(value));
	for(auto res_value : res) {
		TEST_ASSERT_EQUALS(*res_value, 2);
	}

}
