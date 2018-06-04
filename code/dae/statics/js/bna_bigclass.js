var mytext = '';
mytext += '<select name="bigclass_name" onChange="changelocation_x0(document.myform_x0.bigclass_name.options[document.myform_x0.bigclass_name.selectedIndex].value)" size="1"><option selected value="">';
mytext += '<option value="" selected = "selected">请选择大类</option>';
mytext += '<option value="词向量">词向量</option>';
mytext += '<option value="语义识别">语义识别</option>';
mytext += '<option value="文本处理">文本处理</option>';
mytext += '</select>';
document.write(mytext);
