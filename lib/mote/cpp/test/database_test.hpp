#include <unittest/testsuite.hpp>

class DatabaseTest : public unittest::TestSuite
{
public:
	void testInsert();
	void testFind();
};
