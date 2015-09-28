/**
 * database_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "database_test.hpp"
#include <database.hpp>
#include "iterator_utils.hpp"

struct IntegerQuery {
	const int key;
	IntegerQuery(const int key) : key(key) {}
	bool match(const int& other) const { return other == key; }
};

void
DatabaseTest::testInsert()
{
	using DB = awap::Database<int, IntegerQuery, IntegerQuery, 10>;

	DB db;
	TEST_ASSERT_EQUALS(db.count(), 0u);
	TEST_ASSERT_TRUE(db.insert(2));
	TEST_ASSERT_EQUALS(db.count(), 1u);

	// test inser with initializer list
	TEST_ASSERT_TRUE(db.insert({3,5,7,11,13}));
	TEST_ASSERT_EQUALS(db.count(), 6u);
	TEST_ASSERT_TRUE(db.insert({17,19,23,29}));
	TEST_ASSERT_EQUALS(db.count(), 10u);

	// check that db rejects results if full
	TEST_ASSERT_FALSE(db.insert(37));
	TEST_ASSERT_EQUALS(db.count(), 10u);

	// test insert through constructor
	DB db2({0,1,2,3});
	TEST_ASSERT_EQUALS(db2.count(), 4u);
}

void
DatabaseTest::testFind()
{
	using DB = awap::Database<int, IntegerQuery, IntegerQuery, 100>;

	DB db({2,3,5,7,5,19,11,2,13,19,17,7,2});
	TEST_ASSERT_EQUALS(db.count(), 13u);

	// test count iterator
	std::array<uint8_t, 4> testArray;
	TEST_ASSERT_EQUALS(countIterator(testArray), 4u);

	// find trailing element
	db.insert(101);
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(101))), 1u);

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
			TEST_ASSERT_EQUALS(res_value, value);
		}
	}

	// 2 appears three times
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(2))), 3u);
	auto res = db.find(IntegerQuery(2));
	for(auto res_value : res) {
		TEST_ASSERT_EQUALS(res_value, 2);
	}

}

void
DatabaseTest::testRemove()
{
	using DB = awap::Database<int, IntegerQuery, IntegerQuery, 5>;

	DB db({2,3,5,2,3});
	TEST_ASSERT_EQUALS(db.count(), 5u);

	// test for some values that should not be found
	TEST_ASSERT_EQUALS(db.remove(IntegerQuery(4)), 0u);
	TEST_ASSERT_EQUALS(db.remove(IntegerQuery(4000)), 0u);

	// remove the 5
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(5))), 1u);
	TEST_ASSERT_EQUALS(db.remove(IntegerQuery(5)), 1u);
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(5))), 0u);
	TEST_ASSERT_EQUALS(db.count(), 4u);
	TEST_ASSERT_TRUE(db.insert(5));

	// remove all 2, 3
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(2))), 2u);
	TEST_ASSERT_EQUALS(db.remove(IntegerQuery(2)), 2u);
	TEST_ASSERT_EQUALS(countIterator(db.find(IntegerQuery(2))), 0u);

	DB db2({2,2,2,2,2});
	TEST_ASSERT_EQUALS(db2.count(), 5u);
	TEST_ASSERT_EQUALS(db2.remove(IntegerQuery(2)), 5u);
	TEST_ASSERT_EQUALS(db2.count(), 0u);

}
