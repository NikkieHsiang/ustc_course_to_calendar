import os
import json
import requests as r
from datetime import datetime
from bs4 import BeautifulSoup
import argparse

from coursecalendar import Calendar
from httpRequestUtil_contextmanager import httpRequest

parser = argparse.ArgumentParser()
parser.add_argument('--output', '-o', default='courses')
args = parser.parse_args()

def error(msg):
    print(msg)
    os.system('pause')
    exit()

firstdayofterm = '2024.2.26'#input("学期第一天的年月日，用'.'隔开，如2022.8.22：")
sessionid = input('SESSIONID：')
# sessionid ='75a2c5ff-2056-4b08-a2ba-4ee21885ffca'

host = 'https://jw.ustc.edu.cn'
url_selected = host+'/ws/for-std/course-select/selected-lessons'
s = r.Session()
cookies = {
    '_ga':'GA1.3.814254003.1694996265',
    'SESSION':sessionid,
    'SVRNAME':'student1',
    '_gid': 'GA1.3.1621261981.1709018170',
    '_ga_VR0TZSDVGE' : 'GS1.3.1709018170.11.1.1709018172.0.0.0'
}

payload = 'studentId=378917&turnId=882'
headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

lessonsId = []
with httpRequest(s, url_selected, 'post', cookies=cookies, headers=headers, data=payload) as resp:
    #解析已选课程id
    selectedlessonsList = json.loads(resp.content)
    for lesson in selectedlessonsList:
        lessonsId.append(lesson['id'])
        
print(lessonsId)

url = host + '/ws/schedule-table/datum'

s = r.Session()
cookies = {
    'SESSION': sessionid,#'75a2c5ff-2056-4b08-a2ba-4ee21885ffca',
}

firstday = datetime(*map(int, firstdayofterm.split('.')))
calendar = Calendar(firstday)

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)
    
d = json.dumps({"lessonIds":lessonsId, "studentId":378917})
headers = {'content-type': 'application/json'}

with httpRequest(s, url, 'post', cookies=cookies, headers=headers, data= d) as resp:
    #根据已选课程id和student id解析得到课表
    lessonList = json.loads(resp.content).get('result').get('lessonList')
    scheduleList = json.loads(resp.content).get('result').get('scheduleList')

    save_fn = 'test.json'
    file = open(save_fn,'w',encoding='utf-8');
    jj = json.dumps(lessonList,cls=MyEncoder,indent=4)
    file.write(jj)
    file.close()
    
    for i in lessonList:
        lessonId = i['id']
        courseCode = i['code']
        courseName = i['courseName']
        weeks = i['suggestScheduleWeeks']
        teacher = i['teacherAssignmentList'][0]['name']
        for k in scheduleList:
            if k['lessonId']==lessonId:
                place = k['customPlace']
                if place == None:
                    place = k['room']['code']
                startTime = k['startTime']
                endTime = k['endTime']
                weekday = k['weekday']
                periods = k['periods']
                print(courseCode, courseName, weeks, weekday, teacher, startTime, periods, place)
                calendar.appendCourse(courseCode, courseName, weeks, weekday, teacher, startTime, periods, place)
                break
 
print('解析完成，正在生成文件' + args.output + '.ics')
calendar.to_ics(args.output + '.ics')
print('成功！\n\n通过邮件等方式发送到手机后，即可导入到手机日历，安卓苹果通用。\n导入时建议新建一个日历账户，这样方便统一删除以及颜色区分。\n')
os.system('pause')


