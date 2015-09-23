#include "service_directory_test.hpp"
#include <service_directory.hpp>
using namespace awap;


void
ServiceDirectoryTest::testInsert()
{
	using Directory = AgentDirectory<3, 8>;

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

	// make sure duplicate entries do not take up space
	{
		Directory dir;
		Directory::Entry entry { { 0x12345678 }, {1, 2}, 0x22};
		for(auto ii = 0; ii < 8; ++ii) {
			dir.insert(entry);
		}
		TEST_ASSERT_EQUALS(dir.count(), 1u);
	}

}
