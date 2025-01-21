def find_it(seq):
    list=[]
    quantity=[]
    for seqs in seq:
        if seqs in list:
            i=0
            for el in list:
                if el == seqs:
                    k = quantity[i] + 1
                    quantity[i] = k
                i=i+1 
        else:
            list.append(seqs)
            quantity.append(1)
    for k in range(len(list)):
        if quantity[k] % 2 == 1:
           result = list[k]
    return result

def find_it1(seq):
    for i in seq:
        if seq.count(i)%2!=0:
            return i

def test(s):
    print(len(s))

if __name__ == "__main__":
    # print(find_it([20,1,-1,2,-2,3,3,5,5,1,2,4,20,4,-1,-2,5]))
    # print(find_it1([20,1,-1,2,-2,3,3,5,5,1,2,4,20,4,-1,-2,5]))
    test("frghy")