#include "util_test.hpp"
#include <util.hpp>
using namespace awap;

void
UtilTest::testDivideCeil()
{
	TEST_ASSERT_EQUALS(divideCeil(5, 4), 2);
	TEST_ASSERT_EQUALS(divideCeil(4, 4), 1);
	TEST_ASSERT_EQUALS(divideCeil(3, 4), 1);
}
