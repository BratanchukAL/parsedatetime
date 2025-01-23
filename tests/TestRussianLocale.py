# -*- coding: utf-8 -*-
"""
Test parsing of simple date and times using the Russian locale
"""
import sys
import time
import datetime
import unittest
import parsedatetime as pdt
from parsedatetime.context import pdtContext
from . import utils


class test(unittest.TestCase):

    @utils.assertEqualWithComparator
    def assertExpectedResult(self, result, check, **kwargs):
        return utils.compareResultByTimeTuplesAndFlags(result, check, **kwargs)

    def setUp(self):
        locale = 'ru_RU'
        self.ptc = pdt.Constants(locale, usePyICU=False)
        self.cal = pdt.Calendar(self.ptc)

        (self.yr, self.mth, self.dy, self.hr,
         self.mn, self.sec, self.wd, self.yd, self.isdst) = time.localtime()

        if self.ptc.localeID != locale:
            raise unittest.SkipTest(
                'Locale not set to %s - check if PyICU is installed' % locale)

    def testTimes(self):
        start = datetime.datetime(
            self.yr, self.mth, self.dy, self.hr, self.mn, self.sec).timetuple()
        target = datetime.datetime(
            self.yr, self.mth, self.dy, 23, 0, 0).timetuple()

        self.assertExpectedResult(
            self.cal.parse('23:00:00', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN | pdtContext.ACU_SEC)))
        self.assertExpectedResult(self.cal.parse('23:00', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
        self.assertExpectedResult(self.cal.parse('2300', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))

        target = datetime.datetime(
            self.yr, self.mth, self.dy, 11, 0, 0).timetuple()

        self.assertExpectedResult(
            self.cal.parse('11:00:00', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN | pdtContext.ACU_SEC)))
        self.assertExpectedResult(self.cal.parse('11:00', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
        self.assertExpectedResult(self.cal.parse('1100', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))

        target = datetime.datetime(
            self.yr, self.mth, self.dy, 7, 30, 0).timetuple()

        self.assertExpectedResult(self.cal.parse('730', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
        self.assertExpectedResult(self.cal.parse('0730', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))

        target = datetime.datetime(
            self.yr, self.mth, self.dy, 17, 30, 0).timetuple()

        self.assertExpectedResult(self.cal.parse('1730', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
        self.assertExpectedResult(self.cal.parse('173000', start), (target, pdtContext(pdtContext.ACU_HOUR | pdtContext.ACU_MIN | pdtContext.ACU_SEC)))

    def testDates(self):
        start = datetime.datetime(
            self.yr, self.mth, self.dy, self.hr, self.mn, self.sec).timetuple()
        target = datetime.datetime(
            2006, 8, 25, self.hr, self.mn, self.sec).timetuple()

        self.assertExpectedResult(
            self.cal.parse('25.08.2006', start), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY)))
        self.assertExpectedResult(
            self.cal.parse('25.8.06', start), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY)))

        if self.mth > 8 or (self.mth == 8 and self.dy > 25):
            target = datetime.datetime(
                self.yr + 1, 8, 25, self.hr, self.mn, self.sec).timetuple()
        else:
            target = datetime.datetime(
                self.yr, 8, 25, self.hr, self.mn, self.sec).timetuple()

        self.assertExpectedResult(self.cal.parse('25.8', start), (target, pdtContext(pdtContext.ACU_MONTH | pdtContext.ACU_DAY)))
        self.assertExpectedResult(self.cal.parse('25.08', start), (target, pdtContext(pdtContext.ACU_MONTH | pdtContext.ACU_DAY)))

    def testDatesLang(self):
        if sys.version_info >= (3, 0):
            target = datetime.datetime(2006, 8, 25, 23, 5).timetuple()
            self.assertExpectedResult(
                self.cal.parse('25 августа 2006 23:05'), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY | pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
            target = datetime.datetime(
                2006, 8, 25, self.hr, self.mn, self.sec).timetuple()
            self.assertExpectedResult(
                self.cal.parse('25 августа 2006'), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY)))

    def testConjugate(self):
        if sys.version_info >= (3, 0):
            target = datetime.datetime(2006, 9, 25, 23, 5).timetuple()
            self.assertExpectedResult(
                self.cal.parse('25 сентября 2006 23:05'), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY | pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))
            # self.assertExpectedResult(
            #     self.cal.parse('25 сентябрь 2006 23:05'), (target, pdtContext(pdtContext.ACU_YEAR | pdtContext.ACU_MONTH | pdtContext.ACU_DAY | pdtContext.ACU_HOUR | pdtContext.ACU_MIN)))

    def testdayOffsets(self):
        def get_datetime(tuple_time):
            return datetime.datetime(*tuple_time[:6]).date()

        now = datetime.datetime.today().date()

        self.assertEqual(
            get_datetime(self.cal.parse("вчера")[0]),
            now - datetime.timedelta(days=1)
        )
        self.assertEqual(
            get_datetime(self.cal.parse("завтра")[0]),
            now + datetime.timedelta(days=1)
        )

        self.assertEqual(
            get_datetime(self.cal.parse("позавчера")[0]),
            now - datetime.timedelta(days=2)
        )

        self.assertEqual(
            get_datetime(self.cal.parse("послезавтра")[0]),
            now + datetime.timedelta(days=2)
        )

    def testDayNumberOffsets(self):
        start_dt = datetime.datetime(2014, 10, 25, hour=0)
        start = start_dt.timetuple()

        def get_datetime(tuple_time):
            return datetime.datetime(*tuple_time[:6])

        self.assertEqual(
            get_datetime(self.cal.parse("за 3 дня", sourceTime=start)[0]),
            start_dt + datetime.timedelta(days=3)
        )
        self.assertEqual(
            get_datetime(self.cal.parse("за 90 дней", sourceTime=start)[0]),
            start_dt + datetime.timedelta(days=90)
        )
        self.assertEqual(
            get_datetime(self.cal.parse("за 24 месяца", sourceTime=start)[0]),
            start_dt + datetime.timedelta(days=30*24+11)
        )
        self.assertEqual(
            get_datetime(self.cal.parse("за 4 часа", sourceTime=start)[0]),
            start_dt + datetime.timedelta(hours=4)
        )

    def testDayNumberOffsetsMany(self):
        start_dt = datetime.datetime(2014, 10, 25, hour=0)

        self.assertListEqual(
            [datetime.timedelta(days=3), datetime.timedelta(days=8)],
            self.cal.parse_only_durations("от 3 дней и до 8 дней", sourceTime=start_dt)[2],
        )
        self.assertListEqual(
            [datetime.timedelta(days=90), datetime.timedelta(days=180)],
            self.cal.parse_only_durations("от 90 дней до 180 д", sourceTime=start_dt)[2],
        )
        self.assertListEqual(
            [datetime.timedelta(days=30 * 24 + 11), ],
            self.cal.parse_only_durations("за 24 месяца", sourceTime=start_dt)[2],
        )
        self.assertListEqual(
            [datetime.timedelta(hours=4), datetime.timedelta(days=60)],
            self.cal.parse_only_durations("за 4 часа или до 60 дней", sourceTime=start_dt)[2],
        )

    def testOnlyDate(self):
        start_dt = datetime.datetime(2014, 10, 25)
        start = start_dt.timetuple()

        def get_datetime(tuple_time):
            return datetime.datetime(*tuple_time[:6])

        self.assertNotEqual(
            start_dt + datetime.timedelta(days=3),
            get_datetime(self.cal.parse_only_dates("за 3 дня", sourceTime=start)[0])
        )

        self.assertNotEqual(
            get_datetime(self.cal.parse_only_dates("за 4:01:00 часа", sourceTime=start)[0]),
            start_dt + datetime.timedelta(hours=4, minutes=1)
        )

        self.assertEqual(
            datetime.datetime(2014, 9, 25),
            get_datetime(self.cal.parse_only_dates("25 сентября 2014", sourceTime=start)[0])
        )

        self.assertEqual(
            datetime.datetime(2014, 9, 25),
            get_datetime(self.cal.parse_only_dates("25 сентября 2014 года", sourceTime=start)[0])
        )

        self.assertEqual(
            datetime.datetime(2014, 9, 25),
            get_datetime(self.cal.parse_only_dates("25.09.2014 года", sourceTime=start)[0])
        )

        self.assertEqual(
            datetime.datetime(2014, 9, 2),
            get_datetime(self.cal.parse_only_dates("  02-9-2014 года", sourceTime=start)[0])
        )

    def testOnlyDatesMany(self):
        start_dt = datetime.datetime(2014, 10, 25)
        start = start_dt.timetuple()

        def get_datetime(tuple_time):
            return datetime.datetime(*tuple_time[:6])

        self.assertListEqual(
            [],
            self.cal.parse_only_dates("от года до года", sourceTime=start)[2]
        )

        self.assertListEqual(
            [datetime.datetime(2014, 9, 2), datetime.datetime(2014, 9, 6)],
            self.cal.parse_only_dates("от 02-9-2014  до 06-9-2014 ", sourceTime=start)[2]
        )

        self.assertListEqual(
            [datetime.datetime(2006, 9, 25)],
            self.cal.parse_only_dates("25 сентября 2006 23:05", sourceTime=start)[2]
        )


if __name__ == "__main__":
    unittest.main()
