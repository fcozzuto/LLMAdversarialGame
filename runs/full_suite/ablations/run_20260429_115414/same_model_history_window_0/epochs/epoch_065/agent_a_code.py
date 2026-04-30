def choose_move(observation):
    w=observation.get('grid_width',8); h=observation.get('grid_height',8)
    sx,sy=observation['self_position']; ox,oy=observation['opponent_position']
    resources=observation.get('resources',[]); obstacles=set(tuple(p) for p in observation.get('obstacles',[]))
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    candidates=[]
    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if nx<0 or nx>=w or ny<0 or ny>=h: continue
        if (nx,ny) in obstacles: continue
        candidates.append((dx,dy,nx,ny))
    if not candidates: return [0,0]
    if not resources:
        tx,ty=w//2,h//2
        best=None; bv=-10**9
        for dx,dy,nx,ny in candidates:
            d=abs(nx-tx)+abs(ny-ty)
            adv=-d
            dd=abs(nx-ox)+abs(ny-oy)
            adv+=2 if dd>3 else -3 if dd<=1 else -1
            if adv>bv: bv=adv; best=[dx,dy]
        return best
    def d(a,b,c,d0): return abs(a-c)+abs(b-d0)
    best_res=None; best_val=-10**9
    for rx,ry in resources:
        md=d(sx,sy,rx,ry); od=d(ox,oy,rx,ry)
        val=(od-md)*3 - md
        if md==od: val-=1  # prefer resources we're strictly closer to
        if val>best_val: best_val=val; best_res=(rx,ry)
    rx,ry=best_res
    away_threshold=2
    best=None; best_score=-10**9
    for dx,dy,nx,ny in candidates:
        score=0
        if (nx,ny)==(rx,ry): score+=50
        score-=d(nx,ny,rx,ry)
        # obstacle-like staying: discourage moving adjacent if opponent pressure is high
        opp_d=d(nx,ny,ox,oy)
        if opp_d<=away_threshold: score+=12-(opp_d*6)
        else: score-=max(0,opp_d-2)*0.3
        # anti-jitter: prefer moves that reduce distance to target
        cur=d(sx,sy,rx,ry); nxt=d(nx,ny,rx,ry)
        if nxt<cur: score+=4
        elif nxt>cur: score-=2
        if score>best_score:
            best_score=score; best=[dx,dy]
    return best