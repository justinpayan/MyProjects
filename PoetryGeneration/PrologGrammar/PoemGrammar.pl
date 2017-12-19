poem --> sent_simp, np(_,_), pp, sent_comp.

sent_simp --> np(subj,_), vp.
sent_comp --> sent_simp, conj, sent_simp.

np(_,_) --> n.
np(_,_) --> det, n.
np(_,_) --> det, n, pp.
np(_,_) --> det, adj, n.
np(X,_) --> pro(X).

n(_,plural) --> n(_,sing), [s]. %plurals

vp --> v, np(obj,_).
vp --> v.
vp --> adv, v.

adj --> pro(adj).

pp --> prep, det, n.

n --> [love].
v --> [was].
prep --> [for].
adj --> [new].
prep --> [on].
prep --> [in].
pro(adj) --> [his].
adv --> [not].
pro(subj) --> [he].
det --> [a].
conj --> [but].
adj --> [also].
prep --> [of].
pro(obj) --> [it].
pro(subj) --> [it].
prep --> [as].
prep --> [from].
v --> [make].
n --> [year].
adj --> [new].
pro(subj) --> [i].
pro(obj) --> [me].
n --> [time].
v --> [play].
n --> [play].
n --> [children].
n --> [life].
n --> [world].
n --> [parent].
v --> [like].