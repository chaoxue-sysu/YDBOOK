from PIL import Image
import os,requests,tempfile
import base64


def code_image(url):
    with open(url, 'rb') as fin:
        image_data = fin.read()
        base64_data = base64.b64encode(image_data)
        return base64_data


def get_AT(AK,SK):
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    # AK='3NifUYAZUdooTAf7kmiFe0Ky'
    # SK='03SFnz3DYUigIfMEoB0sDNW58GOHG1VM'
    # AK,SK=get_config()
    # print(AK,SK)
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'%(AK,SK)
    header={'Content-Type':'application/json; charset=UTF-8'}
    rq=requests.post(host,headers=header)
    x=rq.json()
    if x.__contains__('access_token'):
        return x['access_token']
    else:
        return None

def recognize(url,AK,SK):
    iuc=code_image(url)
    AT=get_AT(AK,SK)
    # print(AT)
    # host='https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=%s'%AT
    host='https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=%s'%AT
    # host='https://aip.baidubce.com/rest/2.0/ocr/v1/webimage?access_token=%s'%AT
    header={'Content-Type':'application/x-www-form-urlencoded'}
    paras={'image':iuc,'language_type':'ENG'} ##
    # paras = {'url':'https://cas.sysu.edu.cn/cas/captcha.jsp'}
    rq=requests.post(host,data=paras,headers=header)
    res=rq.json()
    import re
    rstr = r"[\-\_\=\(\)\,\/\\\:\*\?\"\<\>\|\' ']"
    if res.__contains__('words_result'):
        chars=re.sub(rstr,'',str(res['words_result'][0]['words']))
        return chars
    return

def get_arround(i,j,step,max_i,max_j):
    all=[]
    il=i-step
    jl=j-step
    if il<0:
        il=0
    if jl<0:
        jl=0
    iu=i+step
    ju=j+step
    if iu>max_i:
        iu=max_i
    if ju>max_j:
        ju=max_j
    for x in range(il,iu):
        for y in range(jl,ju):
            if x==i and j==y:
                continue
            all.append([x,y])
    return all

def deal_pic(in_pic,out):
    img = Image.open(in_pic)
    ## remove background line
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r<30 and g<30 and b<30:
                img.putpixel((i,j), (255,255,255))
    ## make words black and background white
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r<200 and g<200 and b<200:
                img.putpixel((i,j), (0,0,0))
            else:
                img.putpixel((i,j), (255,255,255))
    ## remove Outlier point
    cutoff=2
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r==0 and g==0 and b==0:
                cou=0
                for x,y in get_arround(i,j,2,img.size[0],img.size[1]):
                    rx,gx,bx = img.getpixel((x,y))
                    if rx==0 and gx==0 and bx==0:
                        cou+=1
                if cou<cutoff:
                    img.putpixel((i,j), (255,255,255))
    img.save(out)

def get_captcha(url,session,AK,SK):
    tmpdir = tempfile.gettempdir()
    # url='https://cas.sysu.edu.cn/cas/captcha.jsp'
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    local='%s/sysu.jpg'%(tmpdir)
    rq=session.get(url)
    # print(header)
    con=rq.content
    with open(local,'wb') as bw:
        bw.write(con)
    rq.close()
    img = Image.open(local)
    ## remove background line
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r<30 and g<30 and b<30:
                img.putpixel((i,j), (255,255,255))
    ## make words black and background white
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r<200 and g<200 and b<200:
                img.putpixel((i,j), (0,0,0))
            else:
                img.putpixel((i,j), (255,255,255))
    ## remove Outlier point
    cutoff=2
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r,g,b = img.getpixel((i,j))
            if r==0 and g==0 and b==0:
                cou=0
                for x,y in get_arround(i,j,2,img.size[0],img.size[1]):
                    rx,gx,bx = img.getpixel((x,y))
                    if rx==0 and gx==0 and bx==0:
                        cou+=1
                if cou<cutoff:
                    img.putpixel((i,j), (255,255,255))

    local_out='%s/sysu_deal.jpg'%(tmpdir)
    img.save(local_out)
    captcha=recognize(local_out,AK,SK)
    return captcha



if __name__=='__main__':
    ## test pic
    # deal_pic()
    pass
