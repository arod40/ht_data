from joblib import Parallel, delayed

x =[1,2,3,4,5]
y =[3,5,7,8,7]

def function(val1,val2):
    return val1 + val2

result = Parallel(n_jobs=2)(
    delayed(function)(i,j,) for (i,j) in zip(x,y))

print(result)