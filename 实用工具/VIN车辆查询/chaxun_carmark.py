import requests
from bs4 import BeautifulSoup
import xlrd
import xlwt
import time
def readxls(fileName="1.xls"):
    data=[]
    try:
        wb=xlrd.open_workbook(fileName)
    except:
        print("打开文件失败，请检查文件名是否输入错误。")
        exit()
    sheet=wb.sheet_by_index(0)
    rows=sheet.nrows
    for row in range(1,rows):
        d=sheet.row_values(row)
        temp="0000"
        if type(d[0])==str and len(d[0])==7:
            data.append([d[0],temp])
        else:
            print("第",row+1,"行车牌号",d[0],"格式不对")
    return data

def getOne(session,carmark):
    url="http://10.104.20.232:88/sinoiais/showall/query.do?dimensionSelect=03"
    header = {
        'User-Agent': r'Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4843.400 QQBrowser/9.7.13021.400',
        'Upgrade-Insecure-Requests': '1',
        'Referer': r'http://10.104.20.232:88/sinoiais/showall/query.do?dimensionSelect=03',
        # 'Cookie':'JSESSIONID=0001Law7FAwiRdWJw35gT6OMl1N:-18C2M72',
        'Origin': r'http://10.104.20.232:88',
        'Host': r'10.104.20.232:88',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control':'max-age=0',
        #'Cookie':'JSESSIONID=xybcqH_kOdf-96LToqXiGeC3unzSd3eGSxqQM_fyM7kMDuHCTsZL!1836396137',
    }
    params=[
        ('queryLicensetype','02'),
        ('queryCredentialcode','01'),
        ('licensetype','02'),
        ('carmark',carmark.encode('gb2312')),
        ( 'credentialcode',"01"),
        ('CheckboxGroup1', '02'),
        ('requestSource','http://10.192.0.36:80/flexitm/itm/product/result.jsp?vinflag=0'),
    ]
    try:
        #r=session.post(url=url,headers=header,data=params)
        r = session.post(url=url, headers=header, data=params)
        soup=BeautifulSoup(r.text,"html.parser")
        table1=soup.find_all('table',)[0]
        #print(table1)
        tr1=table1.find_all('tr')[1]
        #print(tr1)
        td=tr1.find_all('td',)

        due=td[5].text
        vin=td[8].text
        print(vin,due)
        result=(carmark,vin,due,)
    except:
        print(carmark,"未找到")
        result=(carmark,"","")
    return result


def getSession():
    url = "http://10.104.20.232:88/sinoiais/checklogin/checkLoginInfo.do"
    session = requests.session()
    param = {
        "sysUserCode": 'CICPdl01',
        'sysPassWord': '5B89C6',
        'random': 'vhtx'
    }
    header = {
        'User-Agent': r'Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4843.400 QQBrowser/9.7.13021.400',
        'Upgrade-Insecure-Requests': '1',
        'Referer': r'http://10.104.20.232:88/sinoiais/',
        'Origin': r'http://10.104.20.232:88',
        'Host': r'10.104.20.232:88',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Cookie':'JSESSIONID=xybcqH_kOdf-96LToqXiGeC3unzSd3eGSxqQM_fyM7kMDuHCTsZL!1836396137',
    }
    t = int(time.time() * 1000)
    session.get(url="http://10.104.20.232:88/sinoiais/")
    randpic = session.get(url="http://10.104.20.232:88/sinoiais/pages/login/RandomNumUtil.jsp?d=" + str(t))
    with open("captcha.png", "wb") as f:
        f.write(randpic.content)
    vcode = input("输入验证码：")
    param['random'] = vcode
    r = session.post(url=url, data=param, headers=header)
    print("登录状态：",r.json()['msg'])
    if r.json()['msg']!="success":
        session=getSession()
    return  session

def getAllitem(data):
    session=getSession()
    print("登录完成！")
    print("开始查询！")
    res_list=[]
    for item in data:
        if item[1]=='0000':
            tmp=getOne(session,item[0])
            res_list.append(tmp)
    return res_list

def writexls(newData,saveFileName='result.xls'):
    wbk=xlwt.Workbook(encoding='ascii')
    sheet=wbk.add_sheet('查询结果')
    for i,x in enumerate(newData):
        sheet.write(i,0,x[0])
        sheet.write(i,1,x[1])
        sheet.write(i, 2, x[2])
    wbk.save(saveFileName)
    print("查询结果已经保存到",saveFileName)

#x=getOne(getsession(),'1LN6L9S98H5613768')
#print(x)



if __name__=='__main__':
    fileName=input("请输入文件名，默认1.xls")
    if fileName=='':
        data=readxls()
    else:
        data=readxls(fileName)
    print("共",len(data),"条有效记录")
    print("开始登录...")
    newData=getAllitem(data)
    print("查询完成，写入文件")
    writexls(newData)
    print("写入完成！")