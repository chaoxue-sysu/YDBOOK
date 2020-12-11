## sysu cas system login
### reference: https://www.cnblogs.com/lihuidu/p/6495247.html
import requests,time
from pyquery import PyQuery as pq
import sys
from recognize_captcha import get_captcha,get_AT


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}


def login_cas(id,pw,AK,SK):
    s= requests.Session()
    captcha_url='https://cas.sysu.edu.cn/cas/captcha.jsp'
    while True:
        try:
            capt=get_captcha(captcha_url,s,AK,SK)
            if len(capt)==4:
                break
        except:
            continue

    login_url='https://cas.sysu.edu.cn/cas/login?service=http://gym.sysu.edu.cn/order/myorders.html'
    res=s.get(login_url,headers=header)

    htmls=pq(res.text)
    exe_val=htmls("input[name='execution']").items().__next__().attr('value')
    # print(exe_val)
    paras={
        'username':id,
        'password':pw,
        'captcha': capt,
        '_eventId':'submit',
        'execution':exe_val
    }
    # print(paras)
    res_log=s.post(login_url,paras,headers=header, allow_redirects=False)
    return res_log

def login(id,pw,logger,AK,SK):
    s= requests.Session()
    rec=0
    if not get_AT(AK,SK):
        logger.log('百度云 AK/SK 错误！退出程序！')
        sys.exit()
        return
    logger.log('start to login CAS')
    while True:
        res_log=login_cas(id,pw,AK,SK)
        try:
            book_url=res_log.headers['Location']
            break
        except:
            rec+=1
            logger.log_flow('retry to login: %s'%rec)
            continue
    # ss= requests.Session()
    if rec!=0:
        logger.log()
    logger.log('login successfully')
    res_book=s.get(book_url)
    # print(requests.utils.dict_from_cookiejar(res_book.cookies))
    return s



def check_passwd(id,pw,AK,SK):
    if not get_AT(AK,SK):
        return False
    res=login_cas(id,pw,AK,SK)
    try:
        htmls=pq(res.text)
        msg=htmls('span').items().__next__().html().strip()
        # print('密码错误')
        return False
    except:
        # print('密码正确')
        return True

if __name__=='__main__':
    pass






