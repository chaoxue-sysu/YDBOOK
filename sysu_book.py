## sysu venue booking
import requests,json,time, datetime,sys,threading,copy
from pyquery import PyQuery as pq

from sysu_cas import login,check_passwd
from recognize_captcha import get_AT
from log import Logger


head_data = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}


def get_time_para(time):
    time_size=len(time['time'])
    # time={'date':'2019-09-16','time':['08:00-09:00','09:00-10:00'],'name_priority':[]}
    url='http://gym.sysu.edu.cn/product/findOkArea.html?s_date=%s&serviceid=61'%time['date']
    rq=session.get(url,headers=head_data)
    avt=rq.json()
    stocks=[]
    stockid_time={}
    if not avt['object']:
        return
    for ele in avt['object']:
        if time['time'].__contains__(ele['stock']['time_no'].strip()):
            stocks.append([str(ele['stockid']),str(ele['id']),str(ele['stock']['time_no'].strip()),str(ele['name'])])
            stockid_time[str(ele['id'])]=[str(ele['stock']['time_no'].strip()),str(ele['name'])]
    if len(stocks)<time_size:
        return
    name_stock={}
    for ele in stocks:
        if not name_stock.__contains__(ele[3]):
            name_stock[ele[3]]=[]
        name_stock[ele[3]].append(ele)
    all_two={}
    for name in name_stock.keys():
        if len(name_stock[name])==time_size:
            all_two[name]=name_stock[name]
    if len(all_two)==0:
        sort_names=sorted(name_stock.keys(),key=lambda x:time['name_priority'].index(str(x)))
        tmp_time={}
        for name in sort_names:
            if not tmp_time.__contains__(name_stock[name][0][2]):
                tmp_time[name_stock[name][0][2]]=name_stock[name][0:2]
            else:
                continue
        if len(tmp_time)!=time_size:
            return
        sep_stocks=[tmp_time[x] for x in tmp_time.keys()]
        select_stocks= sep_stocks
    else:
        sort_names=sorted(all_two.keys(),key=lambda x:time['name_priority'].index(str(x)))
        two_stocks=[]
        for stock in all_two[sort_names[0]]:
            two_stocks.append(stock[0:2])
        select_stocks= two_stocks
    # example: {"param":{"activityPrice":0,"flag":"0","isbookall":"0","isfreeman":"0","istimes":"1","shoppingcart":"0","stock":{"100935":"1"},"stockdetail":{"100935":"750617"},"stockdetailids":"750617","subscriber":"0"},"json":"true"}
    # extra param in "param": {"time_detailnames": "null", "userBean": "null", "activityStr": "null", "address": "null", "dates": "null", "extend": "null", "merccode": "null", "order": "null", "orderfrom": "null", "remark": "null", "serviceid": "null", "sno": "null"}
    para={"param":{"activityPrice":0,"flag":"0","isbookall":"0","isfreeman":"0","istimes":"1","shoppingcart":"0","subscriber":"0"},"json":"true"}
    # "stock": {stockid: "1"}, "stockdetail": {stockid: obj_id}, "stockdetailids": obj_id,
    for stockid in select_stocks:
        if not para['param'].__contains__('stock'):
            para['param']['stock']={}
        para['param']['stock'][stockid[0]]='1'
        if not para['param'].__contains__('stockdetail'):
            para['param']['stockdetail']={}
        para['param']['stockdetail'][stockid[0]]=stockid[1]
    para['param']['stockdetailids'] = ','.join([x[1] for x in select_stocks])
    paras={'param':json.dumps(para['param']),'json':'true'}
    recall_time=[stockid_time[x[1]] for x in select_stocks]
    # print(paras)
    return paras,recall_time



def get_book_id(paras):
    url='http://gym.sysu.edu.cn/order/book.html'
    rq=session.post(url,paras,headers=head_data)
    respones=rq.json()
    # print(respones)
    if  respones['message']== 'USERNOTLOGINYET':
        # log('No login! exit. Check your session')
        # sys.exit()
        cks=requests.utils.dict_from_cookiejar(rq.cookies)
        # print(cks)
        raise Exception('No login! exit. Check your session')
    if respones['object']:
        return respones['object']['orderid']
    else:
        return

def pay(book_id):
    url='http://gym.sysu.edu.cn/pay/account/topay.html'
    data={'param': {"payid": 2, "ctypeindex": 0},'json':'true'}
    data['param']['orderid']=book_id
    datas={'param': json.dumps(data['param']),'json':'true'}
    # print(datas)
    rq=session.post(url,datas,headers=head_data)
    # {"backObject":null,"message":"支付成功","object":null,"reason":null,"result":"1"}
    return rq.json()

def book_main(interval_sec,times,end_time,id,pw,logger,AK,SK):
    fail_msg='您预定失败！预定信息: %s %s'%(times['date'],', '.join(times['time']))
    global session
    session=login(id,pw,logger,AK,SK)
    # interval_sec=1
    # times = {'date': '2019-09-20', 'time': ['08:00-09:00', '09:01-10:00'], 'name_priority': ['3','4','5','6','1','2','7','8']}
    count=0
    logger.log('start to get position')
    inend = False
    while True:
        stocks=get_time_para(times)
        if stocks:
            break
        if break_point(end_time):
            logger.log(fail_msg)
            return fail_msg
        time.sleep(interval_sec)
        count+=1
        logger.log_flow('retry to get position: %s'%count)
        inend=True
    # print(stocks)
    count=0
    if inend:
        logger.log()
    inend = False
    logger.log('get position: %s '%times['date']+'; '.join(['%s 场地%s'%(x[0],x[1]) for x in stocks[1]]))
    logger.log('start to get book id')
    while True:
        book_id = get_book_id(stocks[0])
        if book_id:
            break
        if break_point(end_time):
            logger.log(fail_msg)
            return fail_msg
        time.sleep(interval_sec)
        count+=1
        logger.log_flow('retry to book: %s'%count)
        inend=True
    if inend:
        logger.log()
    logger.log('get book id: %s'%book_id)
    logger.log('start to pay')
    result=pay(book_id)
    if result['message']=='支付成功':
        logger.log('pay successfully!')
        logger.log('booked successfully! book info: %s '%times['date']+'; '.join(['%s 场地%s'%(x[0],x[1]) for x in stocks[1]]))
        return '你已经预定成功！预定信息: %s '%times['date']+'; '.join(['%s 场地%s'%(x[0],x[1]) for x in stocks[1]])+' 订单号：'+book_id
    else:
        logger.log('failure to pay!')
        logger.log(fail_msg)
        return fail_msg


def break_point(end_time):
    # end_time='2019-09-19 00:03:00'
    nt = datetime.datetime.now()
    et = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if nt>et:
        return True
    else:
        return False

def start_book(paras):
    ## change the parameters
    start_time=paras['start_time']
    end_time=paras['end_time']
    active_sec=paras['active_sec']
    interval_sec=paras['interval_sec']
    times = paras['times']
    paras['log'].log('程序将于%s开始预定，%s结束预定！'%(start_time,end_time))
    paras['log'].log('请不要关闭程序！！！')
    ## parameters end
    st = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    while True:
        nt = datetime.datetime.now()
        if nt>st:
            break
        time.sleep(active_sec)
    msg=book_main(interval_sec,times,end_time,paras['id'],paras['pw'],paras['log'],paras['AK'],paras['SK'])
    session.close()
    return msg

class book(threading.Thread):
    def __init__(self,paras):
        threading.Thread.__init__(self)
        self._paras=paras
    # def set_para(self,paras):
    #     self._paras=paras
    def run(self):
        logger=self._paras['log']
        logger.log('开始执行')
        # time.sleep(20)
        self.msg=start_book(self._paras)
        logger.log('完成')
        pass
    def get_msg(self):
        threading.Thread.join(self)
        try:
            return self.msg
        except:
            return 'Exception!'


def time_offset(st,offset):
    time=datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S')
    return (time+datetime.timedelta(seconds=offset)).strftime('%Y-%m-%d %H:%M:%S')

def infer_start_time(date,offset):
    time=datetime.datetime.strptime('%s 23:59:00'%date, '%Y-%m-%d %H:%M:%S')
    return (time-datetime.timedelta(days=offset+1)).strftime('%Y-%m-%d %H:%M:%S')

def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_time_list():
    time_list=[]
    time_list.append('08:00-09:00')
    for i in range(9,22):
        time_list.append('%02d:01-%02d:00'%(i,i+1))
    return json.dumps(time_list)

def get_available_time_list(date):
    # time={'date':'2019-09-16','time':['08:00-09:00','09:00-10:00'],'name_priority':[]}
    url='http://gym.sysu.edu.cn/product/findOkArea.html?s_date=%s&serviceid=61'%date
    rq=requests.get(url,headers=head_data)
    avt=rq.json()
    stocks=set()
    if not avt['object']:
        return json.dumps([])
    for ele in avt['object']:
        stocks.add(ele['stock']['time_no'].strip())
    rq.close()
    return json.dumps(sorted(stocks,key=lambda x:int(str(x).split('-')[0].split(':')[0])))


def delorder(order_id,id,pw):
    session=login(id,pw)
    url='http://gym.sysu.edu.cn/order/delorder.html'
    para={'orderid': order_id,'json':'true'}
    res=session.post(url,para)
    print(res.json())


def get_available_area(date):
    url='http://gym.sysu.edu.cn/product/findOkArea.html?s_date=%s&serviceid=61'%date
    rq=requests.get(url,headers=head_data)
    avt=rq.json()
    stocks={}
    if not avt['object']:
        return
    for ele in avt['object']:
        ti=ele['stock']['time_no'].strip()
        if not stocks.__contains__(ti):
            stocks[ti]=[]
        stocks[ti].append(ele['sname'])
    return stocks



def test_ticket_time(date,now=False):
    tom_date=(datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    if now:
        tims=get_available_area(date)
        if tims:
            print('; '.join(['%s (%s)'%(ti,','.join(tims[ti])) for ti in tims.keys()]))
        return
    startts=[]
    for i in range(24):
        startts.append('%02d:00:00'%i)
        startts.append('%02d:30:00'%i)
    for sti in startts:
        stt='%s %s'%(tom_date,sti)
        st = datetime.datetime.strptime(stt,'%Y-%m-%d %H:%M:%S')
        et=datetime.datetime.strptime(time_offset(stt,3),'%Y-%m-%d %H:%M:%S')
        nt =datetime.datetime.now()
        if nt>et:
            continue
        print('测试时间：%s - %s'%(st,et))
        while True:
            nt = datetime.datetime.now()
            if  nt>et:
                break
            if nt>st:
                tims=get_available_area(date)
                if tims:
                    print('; '.join(['%s (%s)'%(ti,','.join(tims[ti])) for ti in tims.keys()]))
            time.sleep(1)


if __name__=='__main__':
    ## change the parameters
    ## 预定日期时间范围
    date='2020-12-13'
    time_range=['18:00-19:00']
    paras={}
    paras['log']=Logger()
    ## NetID和密码
    paras['id']=''
    paras['pw']=''
    ## 百度智能云AK/SK
    paras['AK']=''
    paras['SK']=''
    ## 开始和结束执行预定程序的时间
    paras["start_time"]=get_now_time() #"2020-09-17 23:59:40"
    # paras["start_time"]=infer_start_time(date,3)
    ## 60秒后结束预定
    paras["end_time"]=time_offset(paras["start_time"],60)
    ## 请求间隔时间（秒）
    paras["active_sec"]=1
    paras["interval_sec"]=1
    ## 南校区场地序号优先级别
    name_priority=['3','4','5','6','1','2','7','8','9','10','11','12','13','14','15','16','17']
    paras["times"] = {'date': date, 'time': time_range, 'name_priority': name_priority}
    ## 检查AK/SK是否正确:
    if not get_AT(paras['AK'],paras['SK']):
        print('百度云 AK/SK 错误！退出程序！')
        sys.exit()
    ## 检查密码是否正确：
    if not check_passwd(paras['id'],paras['pw'],paras['AK'],paras['SK']):
        print('NetID 密码错误！')
        sys.exit()
    ## 开始预定
    start_book(paras)