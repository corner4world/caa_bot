
with open("test_data1.txt",'w') as write_file:
    with open("test_data.txt",'r') as read_file:
        for ele in read_file.readlines():
            for e in ele.split(" "):
                word=e.split("/")[0].replace("\n","")
                write_file.write(word)
                write_file.write(' ')
            write_file.write("\n")
