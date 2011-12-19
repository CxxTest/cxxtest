// BadTestSuite1.h
#include <cxxtest/TestSuite.h>

class MyTestSuite3 : public CxxTest::TestSuite 
{
public:
   void testAddition( void )
   {
      TS_ASSERT( 1 + 1 > 1 );
      TS_ASSERT_EQUALS( 1 + 1, 2 );
   }
#if 0
   void testSubtraction( void )
   {
      TS_ASSERT( 1 - 1 < 1 );
      TS_ASSERT_EQUALS( 1 - 1, 0 );
   }
#endif
};
