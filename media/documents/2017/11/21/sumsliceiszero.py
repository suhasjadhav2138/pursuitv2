"""
Question:
p and q be integers, 0<=p<=q<N
Given an array A of size N, return the number of slices of A (p,q) whose sum is equal to 0.
such that a[p] + a[p+1] + .. + a[q]
Example: [2, -2, 3, 0, 4, -7] return 4
Solution:
  (2, -2), (0), (3, 0, 4, -7), (2, -2, 3, 0, 4, -7)
"""

# Approach===============================================================================:
# for every element in the list, find sum of all the numbers till the current index.
# if the value of sum is equal to a previous sum, this implies that the sum of the slice in between the two point sis zero
#
# So, create a dictionary d which stores the sum as key and the corresponding value equals to the number of occurances of the sum
# and then count the pairs using (n * (n-1))/2



def solution(A):
    # write your code in Python 2.7
    cnt = 0
    t = 0
    d = {}
    for a in A:

        t += a
        if t == 0:
            cnt += 1
            print "found sum 0"

        print a, t
        if not t in d:
            d[t] = 0

        d[t] += 1

    print d

    print " cnt here = ", cnt

    for k in d:
        # if k != 0 :
        cnt += ((d[k] * (d[k]-1)) / 2)
        print " == ", k , ' === ', d[k]
        print "------------", d[k],"    ",((d[k] * (d[k]-1)) / 2),"    ", cnt

    print "cnt = ", cnt




def a(A):
    count = 0
    tempsum = 0
    d = {}
    for elem in A:
        tempsum += elem
        if tempsum == 0:
            count += 1
        if not tempsum in d:
            d[tempsum] = 0
        d[tempsum] += 1
    for key in d:
        count += ((d[key] * (d[key]-1)) / 2)
    return count



# A = [2 -2, 3, 0, 4, -7]
A = [2 -2, 0, 3, 4, -7]
# A = [2,0,0,0,0,-2]
# A = [0,0,0]
solution(A)
print a(A)





