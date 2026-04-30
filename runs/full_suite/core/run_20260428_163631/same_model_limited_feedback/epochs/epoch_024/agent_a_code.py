def choose_move(observation):
    w=observation.get('grid_width',8); h=observation.get('grid_height',8)
    sx,sy=observation['self_position']; ox,oy=observation['opponent_position']
    obstacles=set((x,y) for x,y in observation.get('obstacles',[]))
    resources=observation.get('resources',[])
    if not resources:
        tx,ty=w//2,h//2
    def bfs(st):
        dist=[[-1]*w for _ in range(h)]
        q=[st]; dist[st[1]][st[0]]=0
        qi=0
        while qi<len(q):
            x,y=q[qi]; qi+=1
            d=dist[y][x]+1
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0: continue
                    nx,ny=x+dx,y+dy
                    if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles and dist[ny][nx]==-1:
                        dist[ny][nx]=d; q.append((nx,ny))
        return dist
    ds=bfs((sx,sy)); do=bfs((ox,oy))
    best=None; bestval=-10**9
    for rx,ry in resources:
        if (rx,ry) in obstacles: continue
        d1=ds[ry][rx]; d2=do[ry][rx]
        if d1==-1: continue
        if d1==0: return [0,0]
        val=(d2 if d2!=-1 else 99)-d1
        # slight bias to closer resources if tie
        val=val*100 - d1
        if val>bestval:
            bestval=val; best=(rx,ry)
    if best is None:
        tx,ty=w//2,h//2
    else:
        tx,ty=best
    # choose next step along decreasing distance to target
    curd=ds[sy][sx]
    if ds[ty][tx]==-1:
        tx,ty=sx,sy
    curd=ds[sy][sx]
    best_step=[0,0]; best_score=-10**9
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx,ny=sx+dx,sy+dy
            if not (0<=nx<w and 0<=ny<h) or (nx,ny) in obstacles: continue
            nd=ds[ny][nx]
            if nd==-1: continue
            # prefer closer to target, then also avoid being closer to opponent
            score=(ds[ty][tx]-nd)*1000 if ds[ty][tx]!=-1 else 0
            od=do[ny][nx] if do[ny][nx]!=-1 else 99
            score-=od
            # deterministic tie-break
            if score>best_score or (score==best_score and (dx,dy)<tuple(best_step)):
                best_score=score; best_step=[dx,dy]
    return [int(best_step[0]),int(best_step[1])]