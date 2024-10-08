def maxindex(alist):
    return alist.index(max(alist))

def procalfunc(currentlist, currentvalue, currentprob):
    valmap = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    endprob = [0] * 22
    curlist = currentlist[:]
    templist = curlist[:]
    orival=currentvalue
    curval = currentvalue
    basicprob = currentprob
    
    while sum(templist) != 0:
        maxinde = maxindex(templist)
        templist[maxinde] = 0
        curprob = curlist[maxinde] / sum(curlist) * basicprob
        val = valmap[maxinde]
        curval += val
        curlist[maxinde] -= 1
        
        if curval < 17:
            # Recursive call to compute probabilities for the next state
           # print("for this loop:",curlist,curval,curprob)
            problist = procalfunc(curlist, curval, curprob)
            endprob = [x + y for x, y in zip(problist, endprob)]

            #print(orival,curval)
            curval=orival
        else:
            curlist[maxinde] += 1
            if curval > 21:
                endprob[0] += curprob  # "Bust" condition
            else:
                endprob[curval] += curprob  # Valid result within 17-21
            curval=orival
    
    return endprob