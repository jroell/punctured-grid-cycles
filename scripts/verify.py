#!/usr/bin/env python3
"""Independent small-case DFS and edge-orbit constraint enumeration."""
import json
import subprocess
from collections import Counter
from pathlib import Path
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]

def graph(side):
    n=side//2
    vertices=[(x,y) for x in range(side) for y in range(side)
              if not(x in (n-1,n) and y in (n-1,n))]
    index={v:i for i,v in enumerate(vertices)}
    edges=[]
    for v,(x,y) in enumerate(vertices):
        for p in ((x+1,y),(x,y+1)):
            if p in index:edges.append((v,index[p]))
    transforms=[lambda x,y:(x,y),lambda x,y:(side-1-y,x),
                lambda x,y:(side-1-x,side-1-y),lambda x,y:(y,side-1-x),
                lambda x,y:(side-1-x,y),lambda x,y:(x,side-1-y),
                lambda x,y:(y,x),lambda x,y:(side-1-y,side-1-x)]
    edge_index={tuple(sorted(e)):i for i,e in enumerate(edges)}
    maps=[]
    for transform in transforms:
        perm=[index[transform(*v)] for v in vertices]
        maps.append([edge_index[tuple(sorted((perm[a],perm[b])))] for a,b in edges])
    return vertices,edges,maps

def brute_cycles(side):
    vertices,edges,maps=graph(side)
    adj=[[] for _ in vertices]
    for i,(a,b) in enumerate(edges):
        adj[a].append((b,i));adj[b].append((a,i))
    full=(1<<len(vertices))-1
    cycles=set()
    def visit(v,seen,chosen):
        if seen==full:
            for u,e in adj[v]:
                if u==0:cycles.add(chosen|{e})
            return
        for u,e in adj[v]:
            if not(seen>>u&1):visit(u,seen|(1<<u),chosen|{e})
    visit(0,1,frozenset())
    fixed=[sum(frozenset(p[e] for e in cycle)==cycle for cycle in cycles) for p in maps]
    orbits={min(tuple(sorted(p[e] for e in cycle)) for p in maps) for cycle in cycles}
    both=sum(all(frozenset(maps[t][e] for e in cycle)==cycle for t in (4,5)) for cycle in cycles)
    return {'raw':len(cycles),'r90':fixed[1],'r180':fixed[2],'axis':fixed[4],
            'diagonal':fixed[6],'both_axes':both,'orbits':len(orbits),'all_fixed':fixed}

def orbit_count(side,generators,time_limit=60):
    vertices,edges,maps=graph(side)
    unseen=set(range(len(edges)));orbits=[]
    while unseen:
        seed=min(unseen);orbit={seed};pending=[seed]
        while pending:
            e=pending.pop()
            for t in generators:
                f=maps[t][e]
                if f not in orbit:orbit.add(f);pending.append(f)
        unseen-=orbit;orbits.append(sorted(orbit))
    incidence=[Counter() for _ in vertices]
    for k,orbit in enumerate(orbits):
        for e in orbit:
            for v in edges[e]:incidence[v][k]+=1
    start=monotonic();nodes=0
    def recurse(values):
        nonlocal nodes
        nodes+=1
        if nodes%1000==0 and monotonic()-start>time_limit:
            raise TimeoutError(f'{side=} {generators=} {nodes=} exceeded {time_limit}s')
        while True:
            forced={};best=None
            for v,terms in enumerate(incidence):
                degree=sum(mult for k,mult in terms.items() if values[k]==1)
                unknown=[(k,mult) for k,mult in terms.items() if values[k]<0]
                remaining=sum(mult for _,mult in unknown)
                if degree>2 or degree+remaining<2:return 0
                if unknown:
                    if degree==2 or degree+remaining==2:
                        value=int(degree+remaining==2)
                        for k,_ in unknown:
                            if k in forced and forced[k]!=value:return 0
                            forced[k]=value
                    elif best is None or len(unknown)<len(best):best=unknown
            if not forced:break
            for k,value in forced.items():values[k]=value
        # Any already closed component must cover every vertex.
        adj=[[] for _ in vertices]
        for k,orbit in enumerate(orbits):
            if values[k]==1:
                for e in orbit:
                    a,b=edges[e];adj[a].append(b);adj[b].append(a)
        unseen=set(range(len(vertices)))
        while unseen:
            seed=next(iter(unseen));component={seed};stack=[seed];unseen.remove(seed)
            while stack:
                for u in adj[stack.pop()]:
                    if u in unseen:unseen.remove(u);component.add(u);stack.append(u)
            if all(len(adj[v])==2 for v in component):
                return int(len(component)==len(vertices))
        if best is None:return 0
        k=best[0][0];answer=0
        for value in (0,1):
            child=values.copy();child[k]=value;answer+=recurse(child)
        return answer
    result=recurse([-1]*len(orbits))
    return result,nodes,monotonic()-start

def main():
    expected={r['side']:r for r in json.loads((ROOT/'results/symmetry.json').read_text())}
    records=[]
    reference=json.loads((ROOT/'results/oeis-a003763.json').read_text())['counts_by_n']
    benchmark=json.loads((ROOT/'results/benchmark.json').read_text())
    comparison=[r for r in benchmark if not r['hole']]
    assert len(comparison)==16
    for row in comparison:
        assert row['count']==reference[str(row['width']//2)], row
    print('PASS all intact-grid counts from both engines match OEIS A003763.',flush=True)
    for side in (4,6):
        start=monotonic();actual=brute_cycles(side)
        for field in ('raw','r90','r180','axis','diagonal','both_axes','orbits'):
            assert actual[field]==int(expected[side][field]),(side,field,actual[field],expected[side][field])
        records.append({'method':'full DFS','side':side,'seconds':monotonic()-start,'values':actual})
        print(f'PASS full DFS {side}: {actual}',flush=True)
    for side in (4,6,8):
        for field,generators in [('r90',[1]),('r180',[2]),('axis',[4]),('both_axes',[4,5])]:
            answer,nodes,seconds=orbit_count(side,generators)
            assert answer==int(expected[side][field]),(side,field,answer,expected[side][field])
            records.append({'method':'edge-orbit search','side':side,'field':field,'value':answer,'nodes':nodes,'seconds':seconds})
            print(f'PASS edge-orbit {side} {field}: {answer}; {nodes} nodes; {seconds:.3f}s',flush=True)
    for engine in ('parentheses','partners'):
        for args in [('17','16','1'),('0','4','0'),('4','4','2'),('4x','4','0'),('5','5','1')]:
            p=subprocess.run([str(ROOT/'build'/engine),*args],capture_output=True,text=True,timeout=5)
            assert p.returncode==2,(engine,args,p.returncode)
    (ROOT/'results/verification.json').write_text(json.dumps(records,indent=2)+'\n')
    print('PASS all verification checks.',flush=True)

if __name__=='__main__':main()
