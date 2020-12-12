## 鸭大体育馆自动预订系统（南校羽毛球馆）
### Get start
1. 下载项目源码并进入项目根目录。
2. 确保 Python >=3.6，安装依赖包：`pip install -r requirements.txt`
3. 在`config/para.txt`中按照提示提供百度智能云文字识别API需要使用的AK/SK (API Key、Secret Key)参数，
申请教程链接：[http://ai.baidu.com/forum/topic/show/867951](http://ai.baidu.com/forum/topic/show/867951)。
4. 进入`app`目录，执行`python gui.py`按照图形界面提示操作即可。

### Enviroment
* Python >=3.6
* Packages: 
    * pyquery==1.4.0
    * requests==2.21.0
    * Pillow==8.0.1
### NOTICE
1. 本程序仅适用于鸭大南校新体育馆羽毛球馆。
2. 高级需求请进入`sysu_book.py`主程序修改实现。
### Note：
* `app/gui.py`为图形界面主程序。
* `sysu_book.py`为主程序，支持定时运行，多线程并行，用法详见注释。
* `recognize_captcha.py`为CAS系统验证码识别程序，利用百度智能云文字识别API进行识别。
* `sysu_cas.py`为CAS系统自动登陆程序。
* `log.py`为日志记录程序。
