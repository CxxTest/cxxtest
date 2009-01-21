// Licenced under the GLPL, see http://www.gnu.org/licenses/lgpl.html

#ifndef __CXXTEST__XMLFORMATTER_H
#define __CXXTEST__XMLFORMATTER_H

//
// The XmlFormatter is a TestListener that
// prints reports of the errors to an output
// stream in the form of an XML document.
//

// The following definitions are used if stack trace support is enabled,
// to give the traces an easily-parsable XML format.  If stack tracing is
// not enabled, then these definitions will be ignored.
#define CXXTEST_STACK_TRACE_ESCAPE_AS_XML
#define CXXTEST_STACK_TRACE_NO_ESCAPE_FILELINE_AFFIXES

#define CXXTEST_STACK_TRACE_INITIAL_PREFIX "<stack-frame function=\""
#define CXXTEST_STACK_TRACE_INITIAL_SUFFIX "\"/>\n"
#define CXXTEST_STACK_TRACE_OTHER_PREFIX CXXTEST_STACK_TRACE_INITIAL_PREFIX
#define CXXTEST_STACK_TRACE_OTHER_SUFFIX CXXTEST_STACK_TRACE_INITIAL_SUFFIX
#define CXXTEST_STACK_TRACE_ELLIDED_MESSAGE ""
#define CXXTEST_STACK_TRACE_FILELINE_PREFIX "\" location=\""
#define CXXTEST_STACK_TRACE_FILELINE_SUFFIX ""


#include <cxxtest/TestRunner.h>
#include <cxxtest/TestListener.h>
#include <cxxtest/TestTracker.h>
#include <cxxtest/ValueTraits.h>
#include <cxxtest/ErrorFormatter.h>
#include <cxxtest/StdHeaders.h>
#include <iostream>
#include <sstream>

namespace CxxTest
{
    class ElementInfo
    {
    public:
        std::string name;
        std::string value;
        std::map<std::string,std::string> attribute;

        template <class Type>
        void add(const std::string& name, Type& value)
            {
            std::ostringstream os;
            os << value;
            attribute[name] = os.str();
            }

        void write(OutputStream& os) {
            os << "        <" << name.c_str() << " ";
            std::map<std::string,std::string>::iterator curr=attribute.begin();
            std::map<std::string,std::string>::iterator end =attribute.end();
            while (curr != end) {
              os << curr->first.c_str() << "=\"" << curr->second.c_str() << "\" ";
              curr++;
              }
            if (value == "") {
                os << "/>";
            }
            else {
                os << ">" << escape(value).c_str() << "</" << name.c_str() << ">";
            }
            os.endl(os);
            }

        std::string escape(const std::string& str)
        {
            std::string escStr = "";
            for(size_t i = 0; i < str.length(); i++)
            {
                switch(str[i])
                {
                    case '"':  escStr += "&quot;"; break;
                    case '\'': escStr += "&apos;"; break;
                    case '<':  escStr += "&lt;"; break;
                    case '>':  escStr += "&gt;"; break;
                    case '&':  escStr += "&amp;"; break;
                    default:   escStr += str[i]; break;
                }
            }
            return escStr;
        }

    };

    class TestCaseInfo
    {
    public:

        TestCaseInfo() : fail(false), error(false), runtime(0.0) {}
        std::string className;
        std::string testName;
        std::string line;
        bool fail;
        bool error;
        double runtime;
        std::list<ElementInfo> elements;
        typedef std::list<ElementInfo>::iterator element_t;

        element_t add_element(const std::string& name)
            {
            element_t elt = elements.insert(elements.end(), ElementInfo());
            elt->name=name;
            return elt;
            }

        void write( OutputStream &o )
            {
            o << "    <testcase classname=\"" << className.c_str() << "\" name=\"" << testName.c_str() << "\" ";
            o << "line=\"" << line.c_str() << "\"";
            bool elts=false;
            element_t curr = elements.begin();
            element_t end  = elements.end();
            while (curr != end) {
              if (!elts) {
                 o << ">";
                 o.endl(o);
                 elts=true;
              }
              curr->write(o);
              curr++;
              }
            if (elts)
               o << "    </testcase>";
            else
               o << " />";
            o.endl(o);
            }

    };

    class XmlFormatter : public TestListener
    {
        public:
        XmlFormatter( OutputStream *o, OutputStream *ostr, std::ostringstream *os) : _o(o), _ostr(ostr), _os(os) { }

        std::list<TestCaseInfo> info;
        std::list<TestCaseInfo>::iterator testcase;
        typedef std::list<ElementInfo>::iterator element_t;
        std::string classname;
        int ntests;
        int nfail;
        int nerror;
        double totaltime;

        int run()
        {
            TestRunner::runAllTests( *this );
            return tracker().failedTests();
        }

        void enterWorld( const WorldDescription & desc )
        {
            ntests=0;
            nfail=0;
            nerror=0;
            totaltime=0;
        }

        static void totalTests( OutputStream &o )
        {
            char s[WorldDescription::MAX_STRLEN_TOTAL_TESTS];
            const WorldDescription &wd = tracker().world();
            o << wd.strTotalTests( s ) << (wd.numTotalTests() == 1 ? " test" : " tests");
        }

        void enterSuite( const SuiteDescription& desc )
        {
                classname=generate_classpath(desc.file()).c_str();
                classname += desc.suiteName();
                //std::cout << "HERE " << desc.file() << " " << classname << std::endl;

                //classname=desc.suiteName();
                //(*_o) << "file=\"" << desc.file() << "\" ";
                //(*_o) << "line=\"" << desc.line() << "\"";
                //_o->flush();
        }

        void leaveSuite( const SuiteDescription & )
        {
                std::list<TestCaseInfo>::iterator curr = info.begin();
                std::list<TestCaseInfo>::iterator end  = info.end();
                while (curr != end) {
                    if (curr->fail) nfail++;
                    if (curr->error) nerror++;
                    totaltime += curr->runtime;
                    ntests++;
                    curr++;
                }
                curr = info.begin();
                end  = info.end();
                while (curr != end) {
                  (*curr).write(*_ostr);
                  curr++;
                }
                info.clear();
        }

        void enterTest( const TestDescription & desc )
        {
                testcase = info.insert(info.end(),TestCaseInfo());
                testcase->testName = desc.testName();
                testcase->className = classname;
                std::ostringstream os;
                os << desc.line();
                testcase->line = os.str();
        }

        void leaveTest( const TestDescription & )
        {
        }

        void leaveWorld( const WorldDescription& desc )
        {
                std::ostringstream os;
                os << totaltime;
                (*_o) << "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>" << endl;
                (*_o) << "<testsuite name=\"" << desc.worldName() << "\" ";
                (*_o) << " tests=\"" << ntests << "\" errors=\"" << nerror << "\" failures=\"" << nfail << "\" time=\"" << os.str().c_str() << "\" >";
                _o->endl(*_o);
                (*_o) << _os->str().c_str();
                _os->clear();
                (*_o) << "</testsuite>" << endl;
                _o->flush();
        }

        void trace( const char* /*file*/, unsigned line, const char *expression )
        {
            element_t elt = testcase->add_element("trace");
            elt->add("line",line);
            elt->value = expression;
        }

        void warning( const char* /*file*/, unsigned line, const char *expression )
        {
            element_t elt = testcase->add_element("warning");
            elt->add("line",line);
            elt->value = expression;
        }

        void failedTest( const char* /*file*/, unsigned /*line*/, const char* /*expression*/ )
        {
            testcase->fail=true;
            //testFailure( file, line, "failure", expression );
        }

        void failedAssert( const char *file, unsigned line, const char *expression )
        {
            testFailure( file, line, "failedAssert",
              ( std::string( "Assertion failed: " ) + expression ).c_str() );
        }

        void failedAssertEquals( const char *file, unsigned line,
                                 const char* xStr, const char* yStr,
                                 const char *x, const char *y )
        {
            std::ostringstream os;
            os << "Error: Expected (" <<
                xStr << " == " << yStr << "), found (" <<
                x << " != " << y << ")";
            testFailure( file, line, "failedAssertEquals", os.str());
        }

        void failedAssertSameData( const char *file, unsigned line,
                                   const char *xStr, const char *yStr, const char *sizeStr,
                                   const void* /*x*/, const void* /*y*/, unsigned size )
        {
            std::ostringstream os;
            os << "Error: Expected " << sizeStr << " (" << size << ")  bytes to be equal at (" <<
                xStr << ") and (" << yStr << "), found";
            testFailure( file, line, "failedAssertSameData", os.str());
        }

        void failedAssertSameFiles( const char *file, unsigned line,
                                   const char *, const char *,
                                   const char* explanation
                                   )
        {
            std::ostringstream os;
            os << "Error: " << explanation;
            testFailure( file, line, "failedAssertSameFiles", os.str());
        }

        void failedAssertDelta( const char *file, unsigned line,
                                const char *xStr, const char *yStr, const char *dStr,
                                const char *x, const char *y, const char *d )
        {
            std::ostringstream os;
            os << "Error: Expected (" <<
                xStr << " == " << yStr << ") up to " << dStr << " (" << d << "), found (" <<
                x << " != " << y << ")";
            testFailure( file, line, "failedAssertDelta", os.str());
        }

        void failedAssertDiffers( const char *file, unsigned line,
                                  const char *xStr, const char *yStr,
                                  const char *value )
        {
            std::ostringstream os;
            os << "Error: Expected (" <<
                xStr << " != " << yStr << "), found (" <<
                value << ")";
            testFailure( file, line, "failedAssertDiffers", os.str());
        }

        void failedAssertLessThan( const char *file, unsigned line,
                                   const char *xStr, const char *yStr,
                                   const char *x, const char *y )
        {
            std::ostringstream os;
            os << "Error: Expected (" <<
                xStr << " < " << yStr << "), found (" <<
                x << " >= " << y << ")";
            testFailure( file, line, "failedAssertLessThan", os.str());
        }

        void failedAssertLessThanEquals( const char *file, unsigned line,
                                         const char *xStr, const char *yStr,
                                         const char *x, const char *y )
        {
            std::ostringstream os;
            os << "Error: Expected (" <<
                xStr << " <= " << yStr << "), found (" <<
                x << " > " << y << ")";
            testFailure( file, line, "failedAssertLessThanEquals", os.str());
        }

        void failedAssertRelation( const char *file, unsigned line,
                                   const char *relation, const char *xStr, const char *yStr,
                                   const char *x, const char *y )
        {
            std::ostringstream os;
            os << "Error: Expected " << relation << "( " <<
                xStr << ", " << yStr << " ), found !" << relation << "( " << x << ", " << y << " )";
            testFailure( file, line, "failedAssertRelation", os.str());
        }

        void failedAssertPredicate( const char *file, unsigned line,
                                    const char *predicate, const char *xStr, const char *x )
        {
            std::ostringstream os;
            os << "Error: Expected " << predicate << "( " <<
                xStr << " ), found !" << predicate << "( " << x << " )";
            testFailure( file, line, "failedAssertPredicate", os.str());
        }

        void failedAssertThrows( const char *file, unsigned line,
                                 const char *expression, const char *type,
                                 bool otherThrown )
        {
            std::ostringstream os;
            os << "Error: Expected (" << expression << ") to throw ("  <<
                type << ") but it " << (otherThrown ? "threw something else" : "didn't throw");
            testFailure( file, line, "failedAssertThrows", os.str());
        }

        void failedAssertThrowsNot( const char *file, unsigned line, const char *expression )
        {
            std::ostringstream os;
            os << "Error: Expected (" << expression << ") not to throw, but it did";
            testFailure( file, line, "failedAssertThrowsNot", os.str());
        }

    protected:

        OutputStream *outputStream() const
        {
            return _o;
        }

        /// Guess a class path to help structure the XML output
        std::string generate_classpath(const char* filename)
        {
        if (filename == 0) 
            // Empty filename
            return "";
        if (filename[0] == '\000') 
            return "";

        const char* prev = filename;
        const char* tmp = strstr(filename, "/");

        while (tmp != 0) {
            prev = tmp+1;
            tmp = strstr(prev, "/");
            //std::cout << "HERE X " << prev << " " << tmp << std::endl;
            }
        tmp = strstr(prev, "\\");
        while (tmp != 0) {
            prev = tmp+1;
            tmp = strstr(prev, "\\");
            //std::cout << "HERE Y " << prev << " " << tmp << std::endl;
            }
        filename = prev;

        std::string ans;
        int n=strlen(filename);
        int i=0;
        while (i<n) {
          //std::cout << i << " " << filename[i] << std::endl;
          if (filename[i] == '/') ans += ".";
          else if (filename[i] == '\\') ans += ".";
          else if (filename [i] == '.') {
                if (i==(n-1)) 
                    ans += filename[i];
                else if ((filename[i+1] == '/') || (filename[i+1] == '\\'))
                    i++;
                else if (strcmp(&(filename[i+1]),"h")==0) {
                    i = n;
                    }
                else if (strcmp(&(filename[i+1]),"H")==0) {
                    i = n;
                    }
                else if (strcmp(&(filename[i+1]),"hpp")==0) {
                    i = n;
                    }
                else
                    ans += filename[i];
                }
          else ans += filename[i];
          i++;
          }
        if (ans != "") ans += ".";
        return ans;
        }

    private:
        XmlFormatter( const XmlFormatter & );
        XmlFormatter &operator=( const XmlFormatter & );

        void testFailure( const char* file, unsigned line, const char *failureType, const std::string& message)
        {
            element_t elt = testcase->add_element("failure");
            elt->add("type",failureType);
            elt->add("line",line);
            elt->add("file",file);
            elt->value = message;
            failedTest(file,line,message.c_str());
        }

#if 0
        void attributeBinary( const char* name, const void *value, unsigned size )
        {
            (*_o) << name;
            (*_o) << "=\"";
            dump(value, size);
            (*_o) << "\" ";
        }

        void dump( const void *buffer, unsigned size )
        {
            if (!buffer) return;

            unsigned dumpSize = size;
            if ( maxDumpSize() && dumpSize > maxDumpSize() )
                dumpSize = maxDumpSize();

            const unsigned char *p = (const unsigned char *)buffer;
            for ( unsigned i = 0; i < dumpSize; ++ i )
                (*_o) << byteToHex( *p++ ) << " ";
            if ( dumpSize < size )
                (*_o) << "... ";
        }
#endif

        static void endl( OutputStream &o )
        {
            OutputStream::endl( o );
        }

        OutputStream *_o;
        OutputStream *_ostr;
        std::ostringstream *_os;
    };
}

#endif // __CXXTEST__XMLFORMATTER_H

// Copyright 2008 Sandia Corporation. Under the terms of Contract
// DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
// retains certain rights in this software.

