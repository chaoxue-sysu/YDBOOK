from tkinter import *
from tkinter import ttk
sys.path.append('../')
from sysu_book import *

from log import LocalLogger
# global first_time,running_task
first_time=True
running_task=False

def get_para():
    AK=''
    SK=''
    id=''
    pw=''
    with open('../config/para.txt', 'r', encoding='utf-8') as br:
        for line in br:
            if line.startswith('#'):
                continue
            arr=line.strip().split(':')
            if len(arr)<2:
                continue
            if arr[0]=='AK':
                AK=arr[1].replace('"','').replace('\'','').strip()
            if arr[0]=='SK':
                SK=arr[1].replace('"','').replace('\'','').strip()
            if arr[0]=='NetID':
                id=arr[1].replace('"','').replace('\'','').strip()
            if arr[0]=='Password':
                pw=arr[1].replace('"','').replace('\'','').strip()
    return AK,SK,id,pw

def add():
    paras={}
    paras['log']=LocalLogger(END,result)
    global first_time,running_task,bk
    if running_task:
        paras['log'].log(f'已有任务在运行 PID:{bk.ident}，不能运行新任务！请先结束任务')
        return
    time_range=[entry4.get(),entry5.get()]
    # global AK,SK
    # print(AK,SK)
    # paras['AK'],paras['SK']=get_para()
    paras['AK'],paras['SK']=AK,SK
    paras['email']=''


    if first_time:
        paras['log'].log('Disclaimer: the code is free of charge. All materials are provided without any warranty. Please use them at your own risk.')
    first_time=False

    # paras['log']=logger
    date=entry3.get()
    paras['date']=date
    ## NetID和密码
    paras['id']=entry1.get()
    paras['pw']=entry2.get()
    ## 开始和结束执行预定程序的时间
    now=True
    if not entry6.get()=='立刻':
        now=False
    if now:
        paras["start_time"]=get_now_time()
    else:
        paras["start_time"]=infer_start_time(date,1)
    paras["end_time"]=time_offset(paras["start_time"],120)
    ## 请求间隔时间（秒）
    paras["active_sec"]=1
    paras["interval_sec"]=1
    ## 南校区场地序号优先级别
    name_priority=['3','4','5','6','1','2','7','8','9','10','11','12','13','14','15','16','17']
    paras["times"] = {'date': date, 'time': time_range, 'name_priority': name_priority}
    ## 开始预定
    # msg='你已成功提交预定任务：日期：%s, 时间段：%s。预定结束后，预定结果将发送至您的邮箱：%s。'%(paras['date'],', '.join(paras['times']['time']),paras['email'])
    paras['log'].log('YDSYS 开始执行！')
    if not get_AT(paras['AK'],paras['SK']):
        paras['log'].log('百度云 AK/SK 错误！请在conf/para.txt处提供正确的AK/SK参数！')
        return
    if not check_passwd(paras['id'],paras['pw'],paras['AK'],paras['SK']):
        # result.config(text='密码错误，请重试！',fg='red')
        paras['log'].log('密码错误，请重试！')
        return
    else:
        paras['log'].log('密码验证成功！')
        bk=book(paras)
        running_task=True
        bk.start()
    return

def stop_thread():
    try:
        global running_task
        bk.stop()
        running_task=False
    except:
        LocalLogger(END,result).log('WARNING: No running task!')

def clear_log():
    LocalLogger(END,result).log_clear()

root = Tk()
root.geometry('500x720')
global AK,SK
AK,SK,id,pw=get_para()


time_list=[]
time_list.append('08:00-09:00')
for i in range(9,22):
    time_list.append('%02d:01-%02d:00'%(i,i+1))
time_tp=tuple(time_list)
dates=[]
for i in range(3):
    tom_date=(datetime.datetime.now()+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
    dates.append(tom_date)
date_tp=tuple(dates)

root.title('鸭大羽毛球馆（南校新体育馆）预定系统')
root.iconbitmap('sysu.ico')
lablet=Label(root,text='SYB System',font='Helvetica 18 bold')
lable1=Label(root,text='Net ID',font='Helvetica 10 ')
entry1=Entry(root,width=10)
entry1.insert(0,id)
lable2=Label(root,text='Password',font='Helvetica 10 ')
entry2=Entry(root,width=10)
entry2.insert(0,pw)
lable3=Label(root,text='日期',font='Helvetica 10 ')
entry3=ttk.Combobox(root,state='readonly',width=10)
entry3['value']=date_tp

entry3.current(2)
lable4=Label(root,text='时间段1',font='Helvetica 10')
entry4=ttk.Combobox(root,state='readonly',width=10)
entry4['value']=time_tp
entry4.current(11)
# entry4=Entry(root,width=20)
lable5=Label(root,text='时间段2',font='Helvetica 10',width=10)
entry5=ttk.Combobox(root,state='readonly',width=10)
entry5['value']=time_tp
entry5.current(12)
lable6=Label(root,text='执行时间',font='Helvetica 10')
entry6=ttk.Combobox(root,state='readonly',width=10)
entry6['value']=('立刻','出票时间')
entry6.current(1)


btn=Button(root,command=add,text='提交任务',font='Helvetica 12 bold',bg='green',fg='white',width=10)
stop_btn=Button(root,command=stop_thread,text='停止任务',font='Helvetica 12 bold',bg='orange',fg='white',width=10)
clear_btn=Button(root,command=clear_log,text='清除日志',font='Helvetica 12 bold',bg='blue',fg='white',width=10)
# result=Label(root)
result=Text(root,width=60)

lablet.grid(row=0,column=0,pady=20,sticky=N+S+E+W,columnspan=2)
lable1.grid(row=1,column=0,sticky=N+S+E+W, pady=5)
entry1.grid(row=1,column=1,sticky=N+S+E+W, pady=5)
lable2.grid(row=2,column=0,sticky=N+S+E+W, pady=5)
entry2.grid(row=2,column=1,sticky=N+S+E+W, pady=5)
entry2['show']='*'
lable3.grid(row=3,column=0,sticky=N+S+E+W, pady=5)
entry3.grid(row=3,column=1,sticky=N+S+E+W, pady=5)
lable4.grid(row=4,column=0,sticky=N+S+E+W, pady=5)
entry4.grid(row=4,column=1,sticky=N+S+E+W, pady=5)
lable5.grid(row=5,column=0,sticky=N+S+E+W, pady=5)
entry5.grid(row=5,column=1,sticky=N+S+E+W, pady=5)
lable6.grid(row=6,column=0,sticky=N+S+E+W, pady=5)
entry6.grid(row=6,column=1,sticky=N+S+E+W, pady=5)
btn.grid(row=7,column=0,pady=5)
stop_btn.grid(row=7,column=1,pady=5)
clear_btn.grid(row=9,column=0)
result.grid(row=8,column=0,columnspan=2,padx=20, pady=20,sticky=N+S+E+W)
root.mainloop()

