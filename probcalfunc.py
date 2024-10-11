def greatestone(lis):
    qua=max(lis)
    index=lis.index(qua)
    return index


#list=[3,4,5]


cardlist=[4,4,4,4,4,4,4,4,4,16]
valuemap=[1,2,3,4,5,6,7,8,9,10]
#greatindex=greatestone(list)
#value=valuemap[greatindex]



inival=6
curval=inival
totnum=sum(cardlist)
curtot=totnum
greatindex=greatestone(cardlist)
inilist=cardlist
curlist=inilist
value=valuemap[greatindex]
running=True
inipro=1
curpro=1
templist=curlist
endprob=[0]*22
ignlist=[]
n=0

while sum(templist)!=0:
    n+=1
    if curval <17:
        #draw the greatest possible card
        drawindex=greatestone(templist)
        drawprob=curlist[drawindex]/curtot
        drawval=valuemap[drawindex]
        curval+=drawval
        curlist[drawindex]+=-1
        curpro*=drawprob
        print([curlist,curval,curpro])
    else :
        if curval>21:
            endprob[0]+=curpro
            
        else:
            endprob[curval]+=curpro
        
        
        templist[greatestone(templist)]=0
        curval=inival
        curpro=inipro
        curlist=[4,4,4,4,4,4,4,4,4,16]
        
        print(templist)
        
    if n>80:
        break
    
print(templist)            
print(endprob)
print(sum(endprob))
    
        
        
        



















#print(value)
#print(greatestone(list))
