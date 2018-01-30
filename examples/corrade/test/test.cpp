#include <cmath>
#include <vector>

#include <Corrade/TestSuite/Tester.h>
#include <Corrade/Utility/Endianness.h>

namespace Corrade {
    namespace Examples {

        struct CorradeTest : TestSuite::Tester {
            explicit CorradeTest();

            void pass();
            void expect_fail();
            void skip();

            void benchmark();
        };

        CorradeTest::CorradeTest()
        {
            addTests({&CorradeTest::pass,
                &CorradeTest::expect_fail,
                &CorradeTest::skip});

            addBenchmarks({&CorradeTest::benchmark}, 100);
        }

        void CorradeTest::pass()
        {
            double a = 5.0;
            double b = 3.0;

            CORRADE_VERIFY(a * b == b * a);
        }

        void CorradeTest::expect_fail()
        {
            CORRADE_COMPARE(5 * (5 + 1), 30);
            CORRADE_EXPECT_FAIL("The next test should fail!");
            CORRADE_COMPARE(5 * 5 + 1, 30);
        }

        void CorradeTest::skip()
        {
            CORRADE_SKIP("This is an empty test! Skip!");
            CORRADE_VERIFY(true);
        }

        void CorradeTest::benchmark()
        {
            double a{};
            CORRADE_BENCHMARK(100)
            {
                std::vector<double> container;
                for (std::size_t i = 0; i != 1000; ++i)
                    container.insert(container.begin(), 1.0);
                a += container.back();
            }
            CORRADE_VERIFY(a); // to avoid the benchmark loop being optimized out
        }

    } // namespace Examples
} // namespace Corrade

CORRADE_TEST_MAIN(Corrade::Examples::CorradeTest)