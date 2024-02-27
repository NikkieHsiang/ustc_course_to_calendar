import re
import uuid
from datetime import datetime, time, timedelta

class Calendar:
    """ics文件格式:
    https://cloud.tencent.com/developer/article/1655829
    https://datatracker.ietf.org/doc/html/rfc5545"""
    HEADER = """BEGIN:VCALENDAR
        VERSION:2.0
        CALSCALE:GREGORIAN
        METHOD:PUBLISH
        CLASS:PUBLIC
        BEGIN:VTIMEZONE
        TZID:Asia/Shanghai
        TZURL:http://tzurl.org/zoneinfo-outlook/Asia/Shanghai
        X-LIC-LOCATION:Asia/Shanghai
        BEGIN:STANDARD
        TZOFFSETFROM:+0800
        TZOFFSETTO:+0800
        TZNAME:CST
        DTSTART:19700101T000000
        END:STANDARD
        END:VTIMEZONE""".replace(" ", "")  # 日历头，replace 用来去掉对齐用的缩进
    TAIL = "END:VCALENDAR"
    TIMETABLE_ST = [
        '_',
        time(7,50), time(8, 40), time(9, 45), time(10, 35), 
        time(11, 25), time(14, 0), time(14, 50),
        time(15, 55), time(16, 45), 
        time(17,35), time(19,30),  time(20,20), time(21,10)
    ]
    TIMETABLE_ED = [
        '_',
        time(8, 35), time(9, 25), time(10, 30), time(11, 20), 
        time(12, 10), time(14, 45), time(15, 35),
        time(16, 40), time(17, 30), 
        time(18,20), time(20,15), time(21,5), time(21,55)
        
    ]
    
    startTime2num = {"750":1,'840':2,'945':3,'1035':4,'1125':5,'1400':6,'1450':7,'1555':8,'1645':9,'1735':10,'1930':11,'2020':12,'2110':13}
    
    char2int = { "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "日": 7, "天": 7 }
    def __init__(self, first_day_of_term):
        self._events = []
        self.first_day = first_day_of_term
        self.events = []
        self.pat = re.compile("星期(\S)： 第((?:\d+、?)+)节。")

    def appendCourse(self, id, name, weeks, weekday, teacher, startTime, periods, place):
        """EXAMPLE   
        weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        weekday: 1 #星期一
        startTime: 945 #9:45开始上课
        periods: 2 #连上2节课
        place: G2-B503
        """

        day = weekday #星期几上课 int
        startNumber = self.startTime2num[str(startTime)] #第几节课开始
        endNumber = startNumber+periods-1 #第几节课结束
        startTime = self.TIMETABLE_ST[startNumber] #起始时间 (xx:xx)
        endTime = self.TIMETABLE_ED[endNumber]# 结束时间 (xx:xx) 
        
        
        for w in weeks:
            st_delt = timedelta(weeks=w-1, days=day-1, hours=startTime.hour, minutes=startTime.minute)
            ed_delt = timedelta(weeks=w-1, days=day-1, hours=endTime.hour, minutes=endTime.minute)
            start = self.first_day + st_delt  # 起始日期时间 datetime对象
            end = self.first_day + ed_delt  # 结束日期时间 datetime对象
            self._events.append(self._toEvent(id, name, start, end, place, teacher))

    def _toEvent(self, id, name, start: datetime, end: datetime, location, teacher):
        """
        事件格式：https://datatracker.ietf.org/doc/html/rfc5545#section-3.6.1

        example:
            BEGIN:VEVENT
            DTSTAMP:20210830T121455Z  # 创建时间
            DTSTART;TZID=Asia/Shanghai:20211110T142500 # 开始时间
            DTEND;TZID=Asia/Shanghai:20211110T180500  # 结束时间
            SUMMARY:课程名
            LOCATION:教室
            DESCRIPTION:课程编码：xxx\n主讲教师:xxx
            TRANSP:OPAQUE
            ORGANIZER:USTC
            UID:3ad5a81a-0f59-469c-bb37-e07fed6f9d9e
            END:VEVENT
        """

        time_format = "{date.year}{date.month:0>2d}{date.day:0>2d}T{date.hour:0>2d}{date.minute:0>2d}{date.second:0>2d}"
        res = []
        res += ['BEGIN:VEVENT']
        res += ['DTSTAMP:' + datetime.today().strftime("%Y%m%dT%H%M%SZ")]
        res += ['DTSTART;TZID=Asia/Shanghai:' + time_format.format(date=start)]
        res += ['DTEND;TZID=Asia/Shanghai:' + time_format.format(date=end)]
        res += ['SUMMARY:' + name]
        res += ['LOCATION:' + location]
        res += ['DESCRIPTION:' + '课程编码: ' + id + r'\n' + '主讲教师: ' + teacher]
        res += ['TRANSP:OPAQUE']
        res += ['ORGANIZER:USTC']
        res += ['UID:' + str(uuid.uuid4())]
        res += ['END:VEVENT']
        return '\n'.join(res)

    def to_ics(self, filename):
        eventsStr = '\n'.join(self._events)
        icsStr = '\n'.join([self.HEADER, eventsStr, self.TAIL])
        with open(filename, "w", encoding="utf8") as f:
            f.write(icsStr)