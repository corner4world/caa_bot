d = new dTree('d'); 
d.add(0,-1,'点击 + 号展开');
d.add(74,0,'成员管理','javascript: d.o(1);' ,'','','','','');
d.add(65,0,'任务管理','javascript: d.o(2);' ,'','','','','');
d.add(67,0,'数据采集','javascript: d.o(3);' ,'','','','','');
d.add(75,0,'数据预处理','javascript: d.o(4);' ,'','','','','');
d.add(68,0,'数据分析','javascript: d.o(5);' ,'','','','','');
d.add(56,0,'模型库','javascript: d.o(6);' ,'','','','','');
d.add(72,0,'辅助功能','javascript: d.o(7);' ,'','','','','');
d.add(149,56,'关键词向量','javascript: d.o(8);' ,'','','','','');
d.add(175,65,'标准任务','javascript: d.o(9);' ,'','','','','');
d.add(181,67,'数据页','javascript: d.o(10);' ,'','','','','');
d.add(187,68,'舆情分析','javascript: d.o(11);' ,'','','','','');
d.add(191,72,'后台管理','javascript: d.o(12);' ,'','','','','');
d.add(192,72,'前台管理','javascript: d.o(13);' ,'','','','','');
d.add(203,72,'系统信息','javascript: d.o(14);' ,'','','','','');
d.add(207,75,'查询索引','javascript: d.o(15);' ,'','','','','');
d.add(213,74,'账号管理','javascript: d.o(16);' ,'','','','','');
d.add(224,72,'调试测试','javascript: d.o(17);' ,'','','','','');
d.add(225,68,'商情分析','javascript: d.o(18);' ,'','','','','');
d.add(226,67,'数据种子','javascript: d.o(19);' ,'','','','','');
d.add(1392,181,'训练集数据页','./page_list.py?table_name=page_train','','right','','','');
d.add(1393,224,'视角测试','./test_view.py?n=0','','right','','','');
d.add(1394,224,'运行测试','./work_run.py?id=1394','','right','','','');
d.add(1395,203,'主数据库信息','./data_main_list.py?','','right','','','');
d.add(1396,187,'吐槽管理','./mechat_list.py?','','right','','','');
d.add(1397,187,'生成情感评分','./feel_score_get.py?','','right','','','');
d.add(1398,225,'生成排行榜','./top_get.py?','','right','','','');
d.add(1399,149,'搜索推荐词库','./dic_search_tag.py?','','right','','','');
d.add(1400,226,'种子管理','./url_seed.py?','','right','','','');
d.add(1401,226,'种子分类','./url_seed_type.py?','','right','','','');
d.add(1402,192,'前台首页','./foreground_index.py?','','right','','','');
d.add(1403,192,'友情链接','./frind_link.py?','','right','','','');
d.add(1404,175,'子任务','./task.py?','','right','','','');
d.add(1385,149,'视角汇总词库','./dic_list.py?table_name=dic_view_all','','right','','','');
d.add(1389,149,'视角一级词库','./dic_list.py?table_name=dic_view_class1','','right','','','');
d.add(1390,149,'视角二级词库','./dic_list.py?table_name=dic_view_class2','','right','','','');
d.add(1391,149,'视角三级词库','./dic_list.py?table_name=dic_view_class3','','right','','','');
d.add(1386,187,'视角分析结果','./feel_view_list.py?n=0','','right','','','');
d.add(1296,187,'视角决策树法','./feel_view_tree.py?n=0','','right','','','');
d.add(1215,149,'主词库','./dic_list.py?table_name=dic_main','','right','','','');
d.add(1216,149,'专业术语','./dic_list.py?table_name=dic_major','','right','','','');
d.add(1217,149,'扩展词库','./dic_list.py?table_name=dic_expansion','','right','','','');
d.add(1218,149,'正面词库','./dic_list.py?table_name=dic_positive','','right','','','');
d.add(1219,149,'负面词库','./dic_list.py?table_name=dic_negative','','right','','','');
d.add(1220,149,'分析关键词','./dic_list.py?table_name=dic_analysis','','right','','','');
d.add(1221,149,'汇总词库','./dic_list.py?table_name=dic_all','','right','','','');
d.add(1237,207,'查询索引主表','./index_main_list.py?n=0','','right','','','');
d.add(1247,181,'生产型数据页','./page_list.py?table_name=page','','right','','','');
d.add(1285,191,'主菜单管理','./menu.py?n=0','','right','','','');
d.add(1290,175,'主任务','./work.py?n=0','','right','','','');
d.add(1298,224,'分词测试','./test_segment.py?n=0','','right','','','');
d.add(1310,203,'环境自我测试','./test_self.py?n=0','','right','','','');
d.add(1315,213,'修改账号','./user_edit.py?n=0','','right','','','');
d.add(1375,207,'生成查询正序','./index_seq_get.py?n=0','','right','','','');
d.add(1381,207,'建立查询倒排','./index_invert_get.py?n=0','','right','','','');
d.add(1383,203,'CGI环境变量','./sys_cgi_list.py?n=0','','right','','','');
d.add(1387,207,'生成视角索引','./index_feel_get.py?n=0','','right','','','');
d.add(1388,149,'排行词库','./dic_list.py?table_name=dic_top','','right','','','');
document.write(d);