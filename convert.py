texts=open("convert.txt","r")
n=open("new.txt","w")
for i in range(15):
    text=texts.readline().replace("wizard","warrior").replace("Staff","bow")
    n.write(text)
n.close()
