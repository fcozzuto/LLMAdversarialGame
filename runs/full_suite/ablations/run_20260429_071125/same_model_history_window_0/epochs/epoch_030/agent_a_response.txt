def choose_move(observation):
    w=observation.get('grid_width',8); h=observation.get('grid_height',8)
    sp=observation.get('self_position',[0,0]); op=observation.get('opponent_position',[0,0])
    resources=observation.get('resources',[]); obstacles=set(tuple(xy) for xy in observation.get('obstacles',[]))
    sx,sy=int(sp[0]),int(sp[1]); ox,oy=int(op[0]),int(op[1])

    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b,c,d): 
        dx=a-c; dy=b-d
        return (dx*dx+dy*dy)
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles

    cand=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    if not resources:
        # no resources: drift toward center while staying safe
        tx,ty=w//2,h//2
        best=[0,0]; bs=-10**18
        for dx,dy in cand:
            nx,ny=sx+dx,sy+dy
            if not valid(nx,ny): continue
            sc=-(dist(nx,ny,tx,ty)) + 0.1*dist(nx,ny,ox,oy)
            if sc>bs: bs=sc; best=[dx,dy]
        return best

    # choose target resource where we have the biggest approach advantage over opponent
    best_target=None; best_adv=-10**18
    for rx,ry in resources:
        sd=dist(sx,sy,rx,ry); od=dist(ox,oy,rx,ry)
        adv=od - sd  # positive means we're closer
        if adv>best_adv:
            best_adv=adv; best_target=(rx,ry)
    tx,ty=best_target

    # evaluate moves: prefer getting closer to target, avoid traps near obstacles, avoid getting too close to opponent
    best_move=[0,0]; best_score=-10**18
    for dx,dy in cand:
        nx,ny=sx+dx,sy+dy
        if not valid(nx,ny): continue
        to_target=dist(nx,ny,tx,ty)
        to_opp=dist(nx,ny,ox,oy)
        # discourage moving into "narrow" obstacle-adjacent cells
        obs_adj=0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if ax==0 and ay==0: continue
                xx,yy=nx+ax,ny+ay
                if 0<=xx<w and 0<=yy<h and (xx,yy) in obstacles: obs_adj+=1
        # if opponent is very close, prioritize distancing
        opp_close = 1 if to_opp<=4 else 0
        sc = -to_target + 0.6*to_opp - 0.15*obs_adj + 4*opp_close
        if sc>best_score: best_score=sc; best_move=[dx,dy]

    return best_move