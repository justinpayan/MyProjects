/*

%A context free grammar.

%A poem consists of three sentences.
poem(Z) :- s(A), s(B), s(C), append(A, B, X), append(X, C, Z).

%A sentence consists of a noun phrase and a verb phrase.
s(Z) :- np(X), vp(Y), append(X, Y, Z).

%A noun phrase consists of a determiner and a noun.
np(Z) :- n(Z).
np(Z) :- det(A), n(B), append(A, B, Z).
np(Z) :- det(A), np(B), append(A, B, Z).

%A verb phrase
vp(Z) :- v(X), np(Y), append(X, Y, Z).
vp(Z) :- v(Z). 

det([the]).
det([a]).

n([pants]).
n([mind]).

v([is]).
v([reading]).

adj([witty]).
*/

%Now I'm just going to work through examples given by LPN
s  -->  np,vp. 
    
np  -->  det,n.
np --> det,adj,n.
    
vp  -->  v,np. 
vp  -->  v. 
    
det  -->  [the]. 
det  -->  [a]. 
    
n  -->  [woman]. 
n  -->  [man]. 
    
v  -->  [shoots].

adj --> [hairy].