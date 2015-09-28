/**
 * service_directory_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "service_directory_test.hpp"
#include <service_directory.hpp>
using namespace awap;

#include "iterator_utils.hpp"


void
ServiceDirectoryTest::testInsert()
{
	using Directory = ServiceDirectory<3, 8>;

	// test capacity limit
	{
		Directory dir;
		Directory::Entry entry { { 0x12345678 }, {1, 2}, 0x22};
		for(auto ii = 0; ii < 8; ++ii) {
			dir.insert(entry);
			entry.serviceType++;
		}
		TEST_ASSERT_EQUALS(dir.count(), 8u);
		TEST_ASSERT_FALSE(dir.insert(entry));
		TEST_ASSERT_EQUALS(dir.count(), 8u);
	}
}

void
ServiceDirectoryTest::testFind()
{
	using Directory = ServiceDirectory<3, 10>;

	Directory dir;
	// some entries with the same service type, but different properties
	Directory::Entry entryA { { 0xaa101f }, {1, 1}, 0};
	Directory::Entry entryB { { 0xbb110f }, {2, 2}, 0};
	Directory::Entry entryC { { 0xcc011f }, {3, 3}, 0};

	TEST_ASSERT_TRUE(dir.insert(entryB));
	TEST_ASSERT_TRUE(dir.insert(entryC));
	TEST_ASSERT_TRUE(dir.insert(entryA));

	// some queries for individual elements
	Directory::Query queryA { { 0xff0000 },
	                          { 0xaa0000 }, 0};
	Directory::Query queryB { { 0xff0000 },
	                          { 0xbb0000 }, 0};
	Directory::Query queryC { { 0xff0000 },
	                          { 0xcc0000 }, 0};

	// all queries should only find one element
	TEST_ASSERT_EQUALS(countIterator(dir.find(queryA)), 1u);
	TEST_ASSERT_EQUALS(countIterator(dir.find(queryB)), 1u);
	TEST_ASSERT_EQUALS(countIterator(dir.find(queryC)), 1u);

	// check that it is the correct element
	TEST_ASSERT_EQUALS(dir.find(queryA).begin()->service.agent, 1u);
	TEST_ASSERT_EQUALS(dir.find(queryB).begin()->service.agent, 2u);
	TEST_ASSERT_EQUALS(dir.find(queryC).begin()->service.agent, 3u);

	// some queries that should result in two elements
	Directory::Query queryAB { { 0x00f000 },
	                           { 0x001000 }, 0};
	Directory::Query queryAC { { 0x0000f0 },
	                           { 0x000010 }, 0};
	Directory::Query queryBC { { 0x000f00 },
	                           { 0x000100 }, 0};

	TEST_ASSERT_EQUALS(countIterator(dir.find(queryAB)), 2u);
	TEST_ASSERT_EQUALS(countIterator(dir.find(queryAC)), 2u);
	TEST_ASSERT_EQUALS(countIterator(dir.find(queryBC)), 2u);

	TEST_ASSERT_EQUALS(   dir.find(queryAB).begin()->service.agent,  2u);
	TEST_ASSERT_EQUALS((++dir.find(queryAB).begin())->service.agent, 1u);
	TEST_ASSERT_EQUALS(   dir.find(queryAC).begin()->service.agent,  3u);
	TEST_ASSERT_EQUALS((++dir.find(queryAC).begin())->service.agent, 1u);
	TEST_ASSERT_EQUALS(   dir.find(queryBC).begin()->service.agent,  2u);
	TEST_ASSERT_EQUALS((++dir.find(queryBC).begin())->service.agent, 3u);

}
