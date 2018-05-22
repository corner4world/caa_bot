import pickle



def get_data():

    word_dict={"NONE":0}
    index=1
    label_dict={}
    label_index=0
    word_list = []
    labe_list = []
    with open("train_data.txt",'r') as read:

        for ele in read.readlines():
            label = ele.split(" ")[0]
            ss_w=[]
            ss_l=[]
            if label not in label_dict:
                label_dict[label] = label_index


                label_index += 1
            labe_list.append(int(label)-1)

            for e in ele.split(" ")[1::]:
                word=e.replace("\n","")
                if word not in word_dict:
                    word_dict[word]=index
                    index+=1
                ss_w.append(word_dict[word])
            word_list.append(ss_w)
    pickle.dump(word_dict,open("word_dict.p",'wb'))
    pickle.dump(label_dict,open("label_dict.p",'wb'))
    pickle.dump(word_list,open('word_list.p','wb'))
    pickle.dump(labe_list,open("label_list.p",'wb'))


if __name__ == '__main__':
    get_data()
