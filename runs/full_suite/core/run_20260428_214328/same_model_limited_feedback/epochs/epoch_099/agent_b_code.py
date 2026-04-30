def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    def cheb(a,b,c,d): 
        dx=a-c; 
        if dx<0: dx=-dx
        dy=b-d
        if dy<0: dy=-dy
        return dx if dx>dy else dy
    dirs=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best=None; bestv=-10**18
    for dx,dy in dirs:
        nx=sx+dx; ny=sy+dy
        if nx<0 or nx>=w or ny<0 or ny>=h: continue
        if (nx,ny) in obstacles: continue
        if resources:
            v=0
            for rx,ry in resources:
                ds=cheb(nx,ny,rx,ry); do=cheb(ox,oy,rx,ry)
                adv=do-ds  # positive: we are closer
                v += (30 if adv>0 else 0) + (5 if adv>=2 else 0) - ds*2 + (adv*1.5) - do*0.2
            # blocking pressure: move to reduce opponent distance to nearest resource relative to ours
            nds=min(cheb(nx,ny,rx,ry) for rx,ry in resources)
            ndo=min(cheb(ox,oy,rx,ry) for rx,ry in resources)
            v += (ndo-nds)*3
        else:
            v=-cheb(nx,ny,ox,oy)
        # obstacle proximity penalty
        adj=0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if ax==0 and ay==0: continue
                px=nx+ax; py=ny+ay
                if 0<=px<w and 0<=py<h and (px,py) in obstacles: adj+=1
        v -= adj*0.5
        # tie-break: prefer moves that head toward opponent (keeps pressure when resources are sparse)
        v += -cheb(nx,ny,ox,oy)*0.01
        if v>bestv:
            bestv=v; best=[dx,dy]
    if best is None: return [0,0]
    return best