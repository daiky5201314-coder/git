#!/usr/bin/env python3
"""Independent numerical reference sanity check for the included 2025 exam problems.
Not a replacement for symbolic or mathematical proof.
"""
from math import sqrt, log, sin, cos, pi

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return sqrt(dot(a,a))
def diff(a,b):return tuple(x-y for x,y in zip(a,b))
def close(x,y,tol=1e-9):return abs(x-y)<tol

E=(0,0,0);F=(1,0,0);B=(0,2,0);C=(1,1,0);A=(0,-1,0);D=(1,-1,0)
Ap=(0,.5,sqrt(3)/2);Dp=(1,.5,sqrt(3)/2)
assert close(norm(diff(A,D)),1) and close(norm(diff(C,F)),1) and close(norm(diff(E,B)),2)
assert close(norm(diff(A,B)),3) and close(norm(diff(C,D)),2)
assert close(norm(diff(E,Ap)),1) and close(norm(diff(F,Dp)),1)
# A'B has direction x=0; target plane CD'F has x=1.
assert all(close(p[0],1) for p in (C,Dp,F)) and close(Ap[0],0) and close(B[0],0)
n1=(0,sqrt(3),-1);n2=(sqrt(3),sqrt(3),1)
assert close(dot(n1,diff(F,E)),0) and close(dot(n1,diff(Ap,E)),0)
assert close(dot(n2,diff(C,B)),0) and close(dot(n2,diff(Dp,B)),0)
co=abs(dot(n1,n2))/(norm(n1)*norm(n2));si=sqrt(1-co*co)
assert close(co,1/sqrt(7)) and close(si,sqrt(42)/7)
# Fold of A around x-axis at 120 degrees yields Ap.
assert close(-cos(2*pi/3),Ap[1]) and close(sin(2*pi/3),Ap[2])

for k in (.01,.05,.12,.26,.32):
    x1=1/(3*k)-1
    f=lambda x:log(1+x)-x+x*x/2-k*x**3
    df=lambda x:x*x*(1-3*k*(1+x))/(1+x)
    assert x1>0 and df(x1/2)>0 and close(df(x1),0) and df(x1*1.5)<0
    assert f(x1)>0 and f(2*x1)<0
    lo,hi=x1,2*x1
    for _ in range(90):
        mid=(lo+hi)/2
        if f(mid)>0:lo=mid
        else:hi=mid
    x2=(lo+hi)/2
    assert x1<x2<2*x1 and abs(f(x2))<1e-7
    for t in (.1*x1,.5*x1,.9*x1):
        gp=6*k*t*t*(t*t-x1*x1-2*x1)/((1+x1)**2-t*t)
        assert gp<0
print('PASS: sample 17 geometry, normal vectors, angle; sample 18 k-range, extrema, root, g derivative signs')