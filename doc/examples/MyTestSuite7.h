// MyTestSuite7.h

#include <cxxtest/TestSuite.h>
#include <iostream>

class TestMyData : public CxxTest::TestSuite
{
public:
   struct Data
   {
      char data[3];
      bool operator==(Data o) {
          return (memcmp(this, &o, sizeof(o)) == 0);
      }
   };

   void testCompareData()
   {
      Data x, y;
      memset( x.data, 0x12, sizeof(x.data) );
      memset( y.data, 0xF6, sizeof(y.data) );
      TS_ASSERT_EQUALS( x, y );
   }
};

