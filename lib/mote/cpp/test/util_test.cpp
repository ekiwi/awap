#include "util_test.hpp"
#include <util.hpp>
using namespace awap;


void
UtilTest::testArrayCount()
{
	uint8_t a[10];
	float b[3];
	int64_t c[3000];

	TEST_ASSERT_EQUALS(arrayCount(a), 10u);
	TEST_ASSERT_EQUALS(arrayCount(b), 3u);
	TEST_ASSERT_EQUALS(arrayCount(c), 3000u);
}

void
UtilTest::testDivideCeil()
{
	TEST_ASSERT_EQUALS(divideCeil(5, 4), 2);
	TEST_ASSERT_EQUALS(divideCeil(4, 4), 1);
	TEST_ASSERT_EQUALS(divideCeil(3, 4), 1);
}

void
UtilTest::testString()
{
	char testCString[200] = "This is a test";

	String a(testCString);
	TEST_ASSERT_EQUALS(a.data, testCString);
	// the length is the actual string length, not counting the '\0'
	TEST_ASSERT_EQUALS(a.length, 14);

	testCString[5] = '\0';
	String b(testCString);
	TEST_ASSERT_EQUALS(b.data, testCString);
	TEST_ASSERT_EQUALS(b.length, 5);

	String c(testCString, 10);
	TEST_ASSERT_EQUALS(c.data, testCString);
	TEST_ASSERT_EQUALS(c.length, 10);
}
