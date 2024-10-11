
currentpoint=10
problist=[1/13,1/13,1/13,1/13,1/13,1/13,1/13,1/13,1/13,4/13]
finallist=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]




def finalpointpos(currentpoint,problist,finallist):

    

    while currentpoint <= 16:
        for i in range(1,11):
            nextpoint=currentpoint+i
            if nextpoint>=22:
                nextpoint=22
            if finallist[nextpoint-1]==0:
                finallist[nextpoint-1]=finallist[nextpoint-1]+problist[i-1]
            else:
                finallist[nextpoint-1]=finallist[nextpoint-1]+finallist[nextpoint-1]*problist[i-1]
            
        currentpoint=currentpoint+1
        print(finallist[17])
        print(finallist[21])
        print(sum(finallist[17:22]))
    staylist=[]
    finalsum=sum(finallist[17:22])

    for i in range(16,22):
        staylist.append(finallist[i]/finalsum)
    print(staylist)
        
#    for i in range(0,22):
#        finallist[i]=round(finallist[i],3)
#    print(finallist)
    
    

finalpointpos(currentpoint,problist,finallist)
