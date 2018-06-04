#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"集体",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----


#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

# 分页的模糊查询 参数说明:查询表名 - 参数字典名 - 不查询字段名列表 - 查询字段列表 - 提交地址
def form_search(dic_p,not_in_p,rows_p,file_name_p="script",database_is="mysql"):
    #调试用
    #for j in range(len(rows_p)):
        #print (rows_p[j][1] + " " + rows_p[j][2])

    txt = ""
    txt += "<center>"
    txt += "<form name=\"form_" + file_name_p + "\" method=\"post\" action=\"" + file_name_p + "\"  accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\" >"
    txt += """
    <table width="100%" border="0" align="center" cellpadding="0" cellspacing="0" bordercolor="#0000fa" bordercolordark="#ffffff">
    <tr>
      <td><div align="center">模糊搜索关键词： &nbsp;&nbsp; 
    """
    txt += "<input name=\"search_word\" type=\"text\" value=\"\" size=\"10\">&nbsp;&nbsp;"
    txt += "<select name=\"name_row\">"
    txt += "<option value=\"all\">全部可查询字段</option>"
    
    j = 0
    for j in range(0, len(rows_p)):
        if (not rows_p[j][1] in not_in_p):
            #数据库类型分支判别
            if (database_is == "sqlite"):
                txt += "<option value=\"" + rows_p[j][1] + "\">" + rows_p[j][1] + "</option>"
            if (database_is == "mysql"):
                txt += "<option value=\"" + rows_p[j][3] + "\">" + rows_p[j][19] + "</option>"
        j += 1
    
    txt += "<option value=\"nothing\">不查询关键词</option>"
    txt += "<option value=\"rand\">随机</option>"
    txt += "</select>"
    
    if "order" in dic_p:
        order_p = dic_p["order"]
    else:
        order_p = "nothing"
        
    # 升降序分支选择
    if (order_p == "desc"):
        txt += "<input name=\"order\" type=\"radio\" value=\"desc\" checked>降序"
        txt += "<input name=\"order\" type=\"radio\" value=\"asc\" >升序"
        txt += "<input name=\"order\" type=\"radio\" value=\"nothing\" >不排序"
        
    if (order_p == "asc"):
        txt += "<input name=\"order\" type=\"radio\" value=\"desc\" >降序"
        txt += "<input name=\"order\" type=\"radio\" value=\"asc\" checked>升序"
        txt += "<input name=\"order\" type=\"radio\" value=\"nothing\" >不排序"
        
    if (order_p == "nothing"):
        txt += "<input name=\"order\" type=\"radio\" value=\"desc\" >降序"
        txt += "<input name=\"order\" type=\"radio\" value=\"asc\" >升序"
        txt += "<input name=\"order\" type=\"radio\" value=\"nothing\" checked>不排序"
        
    txt += page_args_hide(dic_p,"page,search_word,name_row,order,submit,username,id,") #form参数隐式传递
    
    txt += "&nbsp;&nbsp;<input type=\"submit\" name=\"Submit\" value=\"确定\">"
    txt += "&nbsp;&nbsp;<input type=\"reset\" name=\"Submit2\" value=\"重置\">"
    txt += """
    </td>
        </tr>
            </table>
                </form>
                    </center>
    """
    return txt

# form参数隐式传递
def page_args_hide(dic_p,args_not_p):
    
    txt = ""
    for x in dic_p:
        
        if (x + "," in args_not_p):
            pass
        else:
            #print (x + "-" + y) #调试用
            txt += "<input name=\"" + x + "\" type=\"hidden\" value=\"" + dic_p[x] +"\" />\n"
            
    return txt

# html 头部视图模板
def html_view(content_p="",charset_p="utf-8",title_p="ldae",css_main_p="statics/css/default.css"):
    html_head = """
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset={{charset}}" />
<title>{{title}}</title>
<link rel="stylesheet" href="{{css_main}}" type="text/css" media="all">
<SCRIPT LANGUAGE="javascript">
        function do_msg() 
        {var msg = "将要进行有数据丢失危险的操作 >>>> 请确认！";
        if (confirm(msg)==true)
        {return true;}
        else
        {return false;}}
</SCRIPT>
</head>
<body>
"""
    html_head = html_head.replace("{{charset}}",charset_p)
    html_head = html_head.replace("{{title}}",title_p)
    html_head = html_head.replace("{{css_main}}",css_main_p)
    
    html_foot = """
    
</body>
</html>

"""
    content_last = html_head + content_p + html_foot
    return content_last

# html 分页视图模板
def page_view(total_number_p,step_p,form_name_p,dic_p):
    
    txt = ""
    if ("page" in dic_p):
        page = int(dic_p["page"])
    else:
        page = 1
    
    mod = divmod(total_number_p,step_p)
    if ( mod[1] == 0 ):
        n = mod[0]
    else:
        n = mod[0] + 1
    
    txt +="""
<script type="text/javascript">
function add(key,value,id)
{
    document.getElementById(key).value = value;
    document.getElementById(id).submit();
}
</script>
    """
    

    # 首页链接form
    txt +="<form name=\"first\" method=\"post\" action=\"" + form_name_p + "\" id=\"first\" accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\"  >\n"
    txt +=page_args_hide(dic_p,"page,submit,username,") #form参数隐式传递
    txt +="<input type=\"Submit\" name=\"argsubmit\" id=\"s\" style=\"display:none\" />\n"
    txt +="</form>\n"
    
    # 下一页链接form
    txt +="<form name=\"first\" method=\"post\" action=\"" + form_name_p + "\" id=\"next\" accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\"  >\n"
    txt +=page_args_hide(dic_p,"page,submit,username,") #form参数隐式传递
    txt +="<input name=\"page\" type=\"hidden\" value=\"" + str(page+1) + "\" />\n"
    txt +="<input type=\"Submit\" name=\"argsubmit\" id=\"s\" style=\"display:none\" />\n"
    txt +="</form>\n"

    # 上一页链接form
    txt +="<form name=\"first\" method=\"post\" action=\"" + form_name_p + "\" id=\"back\" accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\"  >\n"
    txt +=page_args_hide(dic_p,"page,submit,username,") #form参数隐式传递
    txt +="<input name=\"page\" type=\"hidden\" value=\"" + str(page-1) + "\" />\n"
    txt +="<input type=\"Submit\" name=\"argsubmit\" id=\"s\" style=\"display:none\" />\n"
    txt +="</form>\n"

    # 尾页链接form
    txt +="<form name=\"first\" method=\"post\" action=\"" + form_name_p + "\" id=\"last\" accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\"  >\n"
    txt +=page_args_hide(dic_p,"page,submit,username,") #form参数隐式传递
    txt +="<input name=\"page\" type=\"hidden\" value=\"" + str(n) + "\" />\n"
    txt +="<input type=\"Submit\" name=\"argsubmit\" id=\"s\" style=\"display:none\" />\n"
    txt +="</form>\n"

    txt +="<p align=\"center\"><table><tr><td>"
    if ( page < 2 ):
        txt +="<font color='#000080'>首页 上一页</font> "
    else:
        txt +="<a href=\"javascript:;\" onclick =\"add('s','','first');\">首页</a> "
        txt +="<a href=\"javascript:;\" onclick =\"add('s','','back');\">上一页</a> "

    if ( n - page < 1 ):
        txt +="<font color='#000080'>下一页 尾页</font>"
    else:
        txt +="<a href=\"javascript:;\" onclick =\"add('s','','next');\">"
        txt +="下一页</a> <a href=\"javascript:;\" onclick =\"add('s','','last');\">尾页</a>"

    txt +="<font color=\"#000080\"> 页次：</font><strong><font color=red>" + str(page) + "</font><font color='#000080'>/" + str(n) + "</strong>页</font> "
    txt +="<font color=\"#000080\"> 共 <b>" + str(total_number_p) +"</b> 个记录 <b>" + str(step_p) + "</b> 个记录/页</font> "
    
    #form传递参数跳转
    txt +="<td>"
    txt +="<form name=\"page_link\" method=\"post\" action=\"" + form_name_p + "\" accept-charset=\"utf-8\" onsubmit=\"document.charset='utf-8';\"  >"
    txt +="<td>"
    txt +="<font color=\"#000080\">转到：</font>"
    txt +="<input type=\"text\" name=\"page\" size=\"4\" maxlength=\"10\" class=\"smallInput\" value=\"" + str(page) + "\">"
    txt +=page_args_hide(dic_p,"page,submit,username") #form参数隐式传递
    txt +=" <input type=\"submit\"  value=\"跳转\" >"
    txt +="</td>"
    txt +="</form>"
    
    txt +="<tr></table>"
    txt +="</p>"
    
    return txt
    
# 分类处理
class Class_main():
    def __init__(self,rows_p):
        self.rows_p = rows_p
        pass
    # 全表读数据
    def make_js(self,id_p):
    
        txt = ""
        txt += "<script language = \"JavaScript\">\n"
        txt += "var onecount_x" + str(id_p) + ";\n"
        txt += "onecount_x" + str(id_p) + "=0;\n"
        txt += "subcat_x" + str(id_p) + " = new Array();\n"
        for i in range(len(self.rows_p)):
            txt += "subcat_x" + str(id_p) + "[" + str(i) + "] = new Array(\"" + self.rows_p[i][0] + "\",\"" + self.rows_p[i][1] + "\",\"" + self.rows_p[i][0] + "\");\n"
        txt += "subcat_x" + str(id_p) + "[" + str(i+1) + "] = new Array(\"" + self.rows_p[i][0] + "\",\"" + self.rows_p[i][1] + "\",\"" + self.rows_p[i][0] + "\");\n"
        txt += "onecount_x" + str(id_p) + "=" + str(i+1) + ";\n" #JS与py数组下标差的补丁
        txt += "function changelocation_x" + str(id_p) + "(locationid)\n"
        txt += "{"
        txt += "document.myform_x" + str(id_p) + ".smallclass_name.length = 0;\n" 
        txt += """
    var locationid=locationid;
    var i;
    """
        txt += "for (i=0;i < onecount_x" + str(id_p) + "; i++)"
        txt += """
        {
        """
        txt += "if (subcat_x" + str(id_p) + "[i][1] == locationid)"
        txt += """    
            { 
        """
        txt += "document.myform_x" + str(id_p) + ".smallclass_name.options[document.myform_x" + str(id_p) + ".smallclass_name.length] = new Option(subcat_x" + str(id_p) + "[i][0], subcat_x" + str(id_p) + "[i][2]);\n"
        txt += """       
        }        
        }
        
    }    
</script>
        """
        return txt
        
#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    print ("") #调试用
    
if __name__ == '__main__':
    
    main()
    
#---------- 主过程<<结束>> -----------#