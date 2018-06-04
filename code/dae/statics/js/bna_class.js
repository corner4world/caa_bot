var onecount_x0;
onecount_x0=0;
subcat_x0 = new Array();
subcat_x0[0] = new Array("分词","词向量","seg");
subcat_x0[1] = new Array("词性标注","词向量","pseg");
subcat_x0[2] = new Array("TF_IDF","词向量","tf_idf");
subcat_x0[3] = new Array("命名实体","词向量","ne");
subcat_x0[4] = new Array("主题(关键)词","词向量","mk");
subcat_x0[5] = new Array("近义词","词向量","sm");
subcat_x0[6] = new Array("LR_闲聊_意图识别","语义识别","cf_lr_gossip");
subcat_x0[7] = new Array("LR_是非型_意图识别","语义识别","cf_lr_yesno");
subcat_x0[8] = new Array("svm_是为型_意图识别","语义识别","cf_svm_whathow");
subcat_x0[9] = new Array("Cnn+Bilstm意图识别","语义识别","cf_cnn_bilstm");
subcat_x0[10] = new Array("短文本相似度","文本处理","similar_shorttxt");
subcat_x0[11] = new Array("答案抽取_相似度","文本处理","answer_extract_similar");
onecount_x0=12;
function changelocation_x0(locationid)
{document.myform_x0.action.length = 0;

    var locationid=locationid;
    var i;
    for (i=0;i < onecount_x0; i++)
        {
        if (subcat_x0[i][1] == locationid)    
            { 
        document.myform_x0.action.options[document.myform_x0.action.length] = new Option(subcat_x0[i][0], subcat_x0[i][2]);
       
        }        
        }
        
    }
        