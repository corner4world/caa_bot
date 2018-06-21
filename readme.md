# 中文人工智能助理机器人 (Chinese artificial intelligence assistant robot 简称：caa_bot)

---前言---

#说明：
技术思想源于2018年度某中文阅读理解大赛，某多轮对话竞赛，某创业大赛和《灵魂魔罐---深入浅出搞定人工智能助理机器人》技术书籍的编写计划。
本开源组件已经包含了若干年内此人工智能产品开发框架与代码包，因此请注意已实现与框架预制搭建的区别。

#功能（含展望部分）：

1 能够提供泛化型可变任务驱动多轮对话引擎。
2 提供基本AI助理辅助决策功能，例如：生活，健康，喜好等。
3 良好的硬件驱动接口，能唤醒电器，监控，高级版本能嵌入到手机端或专业实体机械型机器人。
4 人机接口可以支持语音输入，图像动作与手势识别和脑波输入等。
5 自带爬虫，数据清理引擎。
6 自带可泛化和扩展的语料库。
7 自带知识图谱采集加工引擎和标准知识库框架。
8 自带机器学习模型库和与之配套用来驱动模型的方法库，如：NLP基础引擎，分类器，检索器，匹配加速器，NLU答案生成器等软件模块。

#可用性：

稍作修改可以直接用于相关工程实践。

#部署：

1 MYSQl数据库
建议版本号：mysql 5.6 64位
依次执行 \data\model\*.sql文件 建立基准数据库

python3.5 windows2008 

# 调用

1 数据分析引擎（dae）模块调用方法：

1-1 确保进入code\cache目录 运行 __redis_start.bat
1-2 进入dae目录 进入CMD界面 运行 python web.py
1-3 api与web调用 1-1,1-2顺利启动后，在浏览器中输入 http://127.0.0.1:8001/ 调用 注意8001端口是否被占用
（注：所有参数可在相应目录下config.py中修改）

2 多轮对话引擎（chat）模块调用方法
1-1 确保进入code\cache目录 运行 __redis_start.bat
1-2 进入code\dae目录 进入CMD界面 运行 python web.py
1-3 进入code\chat目录 进入CMD界面 运行 python web.py
1-3 api与web调用 1-1,1-2顺利启动后，在浏览器中输入 http://127.0.0.1:8000/ 调用 注意8000端口是否被占用


（注：所有参数可在相应目录下config.py中修改）

相关支持库和包附表
Package                Version
---------------------- ---------
absl-py                0.2.0
asn1crypto             0.24.0
astor                  0.6.2
beautifulsoup4         4.6.0
bleach                 1.5.0
boto                   2.48.0
bs4                    0.0.1
bz2file                0.98
certifi                2017.7.27
cffi                   1.11.4
chardet                3.0.4
ChatterBot             0.8.7
chatterbot-corpus      1.1.2
cryptography           2.1.4
cycler                 0.10.0
et-xmlfile             1.0.1
future                 0.16.0
gast                   0.2.0
gensim                 3.0.1
get                    0.0.21
grpcio                 1.11.0
h5py                   2.7.1
html5lib               0.9999999
idna                   2.6
jdcal                  1.3
jieba                  0.39
Jinja2                 2.10
jupyter-pip            0.3.1
Keras                  2.0.3
lxml                   4.1.0
Markdown               2.6.9
MarkupSafe             1.0
mathparse              0.1.1
matplotlib             2.1.0
nltk                   3.3
numpy                  1.14.3
oauthlib               2.0.7
openpyxl               2.4.9
pandas                 0.21.0
Pillow                 5.0.0
pip                    10.0.1
post                   0.0.13
protobuf               3.5.2.pos
psutil                 5.4.3
public                 0.0.38
pycparser              2.18
pyecharts              0.3.1
pymongo                3.6.1
PyMySQL                0.7.11
pyparsing              2.2.0
PyQt5                  5.9
python-dateutil        2.6.1
python-twitter         3.4.1
pytz                   2017.2
PyYAML                 3.12
query-string           0.0.12
redis                  2.10.6
request                0.0.13
requests               2.18.4
requests-oauthlib      0.8.0
scikit-learn           0.19.1
scipy                  1.0.1
selenium               3.6.0
setupfiles             0.0.50
setuptools             39.1.0
sip                    4.19.3
six                    1.11.0
sklearn                0.0
smart-open             1.5.3
SQLAlchemy             1.2.7
tensorboard            1.7.0
tensorflow-gpu         1.7.0
tensorflow-tensorboard 0.1.8
termcolor              1.1.0
Theano                 1.0.1
tornado                4.5.2
tqdm                   4.19.4
ujson                  1.35
urllib3                1.22
Werkzeug               0.14.1
wheel                  0.31.0


---技术文档正文部分---

原理：

1.对话与问答的区别

传统语义上的区别就暂且不谈，谈谈工程实践上的系统构造上的区别：
问答：一问一答，人来问，机器来答。可以近似理解为单轮对话或单边对话，并基于知识库。
对话：对话的核心宗旨是体现三化原则，即个性化，人性化与智能化。
最大的区别不仅仅是有疑问句的交流，还有很多平行语。例如：问：你好？答：你好，有什么可以帮到您？平行语的作用其实是模拟了感情因子，更贴近于真实的人与人之间的交流，这体现了人性化原则。
同时，对话与问答的区别还有话语权的转换，最主要的表现特征是：机器也可以反问。通过反问，更加明确服务对象的真实深层意图，增加准度，这个体现了智能化的特点。同时如果反问到提问者，作为“人”属的画像特征，身高体重，社会地位收入，个人爱好倾向，还会进一步提升准度，又体现了个性化的服务特性。
在现有的技术水平下，可以理解为基于NLP的双边对话，双边对话进行内部API扩展可以升级为多边对话，通俗的解释即为群聊。
对话一般为多轮，即最少4个句子。
例如：
人：你好
机：你好，有什么可以帮您？
人：没事，就是来测试下系统。
机：收到，再见，祝您生活愉快!

总体讲：问答是对话的子系统，对话包括问答。但是问答可以独立对外服务。对于专业知识领域的对话服务，问答是核心组件，对于闲聊和情感关怀对话，问答是加分选项。

---使用与部署说明---

# 命令示例见：0_命令调用示例.txt

# 整体架构与代码说明见：1_文件级架构说明.txt

---附文---

同框架 参考网站：http://www.kc2017.cn
