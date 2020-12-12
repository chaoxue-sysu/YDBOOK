import time
def log(content=''):
    if content=='':
        print(flush=True)
    else:
        content=time.strftime("%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
        # wt = FF.getWriter(self.logPath, True)
        print(content, flush=True)

def log_flow(content):
    content=time.strftime("%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
    print('\r' + content, end='', flush=True)

class Logger():
    def __init__(self):
        pass
    def log(self,content=''):
        if content=='':
            print( flush=True)
        else:
            content=time.strftime("%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
            # wt = FF.getWriter(self.logPath, True)
            print(content, flush=True)

    def log_flow(self,content):
        content=time.strftime("%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
        print('\r' + content, end='', flush=True)

class LocalLogger():
    def __init__(self,end,ele):
        self.end=end
        self.ele=ele
    def log(self,content=''):
        content=time.strftime("\n%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
        # print(content)
            # wt = FF.getWriter(self.logPath, True)
        self.ele.insert(self.end,content)
        self.ele.see(self.end)

    def log_flow(self,content):
        content=time.strftime("\n%Y-%m-%d %H:%M:%S [INFO] ", time.localtime(time.time()))+ "%s"%(content)
        # print(content)
        self.ele.insert(self.end,content)
        self.ele.see(self.end)
    def log_clear(self):
        self.ele.delete(0.0,self.end)

